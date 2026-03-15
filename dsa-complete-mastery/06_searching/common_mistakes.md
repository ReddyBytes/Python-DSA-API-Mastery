# Common Mistakes with Binary Search and Searching Algorithms

> "Binary search is one of the simplest algorithms to describe ('check the middle, go left or right') and one of the hardest to implement bug-free. Even Jon Bentley reported that only about 10% of professional programmers could write a correct binary search on the first try."

This guide covers every major searching mistake with stories, visual traces, and correct implementations. By the end, you will write binary search correctly on the first try, every time.

---

## Table of Contents

1. [Overflow in Midpoint Calculation](#1-overflow-in-midpoint-calculation)
2. [Infinite Loop: Wrong Boundary Update](#2-infinite-loop-wrong-boundary-update)
3. [Wrong Template for Boundary Search](#3-wrong-template-for-boundary-search)
4. [Off-by-One in the Return Value](#4-off-by-one-in-the-return-value)
5. [Applying Binary Search to Unsorted Input](#5-applying-binary-search-to-unsorted-input)
6. [bisect_left vs bisect_right for Duplicates](#6-bisect_left-vs-bisect_right-for-duplicates)
7. [Search Space is the Answer Range, Not the Array](#7-search-space-is-the-answer-range-not-the-array)
8. [Linear Search When a Hash Set Is Better](#8-linear-search-when-a-hash-set-is-better)
9. [Missing the Check After the Loop Exits](#9-missing-the-check-after-the-loop-exits)
10. [DFS vs BFS for Shortest Path](#10-dfs-vs-bfs-for-shortest-path)

---

## 1. Overflow in Midpoint Calculation

### The Story: The Overflowing Gas Tank

In C and Java, integers have a fixed size (32-bit signed: max ~2.1 billion). If `left = 1,000,000,000` and `right = 1,500,000,000`, then `left + right = 2,500,000,000`, which overflows a 32-bit signed integer and wraps to a negative number. The midpoint formula `(left + right) / 2` silently produces garbage.

Python is immune to this because Python integers have arbitrary precision. But you are expected to know this in interviews because you will be asked to code in Java or C++, or asked "would your code work in a language with fixed-size integers?"

### Python Is Safe (But You Must Know Why)

```python
# Python: NO overflow issue. Integers are arbitrary precision.
left = 1_000_000_000
right = 2_000_000_000

mid = (left + right) // 2
print(mid)   # 1500000000  -- correct, no overflow in Python

# Python integers can be arbitrarily large:
huge = 10 ** 100   # A googol -- no problem!
mid_huge = (huge + huge * 2) // 2
print(mid_huge)    # 1500000...00 -- works fine
```

### The Problem in C/Java

```
// Java (32-bit int, max value = 2,147,483,647)
int left = 1_500_000_000;
int right = 2_000_000_000;
int mid = (left + right) / 2;   // OVERFLOW!
// left + right = 3,500,000,000 which overflows to -794,967,296
// mid = -397,483,648  -- COMPLETELY WRONG

// Safe version in Java:
int mid = left + (right - left) / 2;
// right - left = 500,000,000  (fits in int)
// left + 250,000,000 = 1,750,000,000  (fits in int)
```

### The Python Equivalent (For Interview Awareness)

```python
# Both are correct in Python, but write the safe version
# to show interviewers you know about overflow:

# Version 1: Direct (fine in Python, bad in C/Java)
def binary_search_naive_mid(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2   # Fine in Python
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


# Version 2: Overflow-safe (correct in ALL languages)
def binary_search_safe_mid(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2   # PREFERRED: no overflow risk
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


# Both give the same result in Python:
arr = list(range(100))
assert binary_search_naive_mid(arr, 42) == binary_search_safe_mid(arr, 42) == 42
print("Both find 42 at index 42")
```

### Why left + (right - left) // 2 Works

```
Regular:   mid = (left + right) // 2
Safe:      mid = left + (right - left) // 2

Proof they are equal:
  left + (right - left) // 2
= left + right/2 - left/2
= left/2 + right/2
= (left + right) / 2  ✓

But the intermediate value (right - left) is always <= (right - 0) = right,
which is bounded by the array size. No overflow risk.
```

### The Bit-Shift Alternative (Seen in Competitive Programming)

```python
# (left + right) >> 1 is equivalent to (left + right) // 2 for non-negative
# Often seen in competitive programming for speed:
mid = (left + right) >> 1   # Same as (left + right) // 2

# WARNING: In Python this has no speed advantage (integers aren't fixed-width)
# In C/Java, right-shift may be marginally faster than integer division
# Prefer the readable // 2 version in interviews
```

---

## 2. Infinite Loop: Wrong Boundary Update

### The Story: The Two Guards Who Never Move

Imagine two guards standing at opposite ends of a hallway. Their job is to walk toward each other until they meet or pass. But one guard misunderstands the instruction: instead of "always step forward," he sometimes does not move at all. If he stays in place, the other guard eventually reaches him but neither has "passed" — and they are stuck standing next to each other forever.

`left = mid` instead of `left = mid + 1` can cause exactly this: when `left` and `right` are adjacent, `mid` equals `left`, and setting `left = mid` means `left` never advances. Infinite loop.

### The WRONG Code

```python
# WRONG: Using left = mid (can cause infinite loop)
def binary_search_wrong(arr, target):
    left, right = 0, len(arr) - 1

    while left < right:   # Note: using < not <=
        mid = left + (right - left) // 2
        if arr[mid] < target:
            left = mid    # BUG: should be left = mid + 1
        else:
            right = mid

    return left if arr[left] == target else -1

# This hangs on certain inputs!
# binary_search_wrong([1, 2], 2)  # INFINITE LOOP!
```

### Visual Trace: The Infinite Loop

```
arr = [1, 2], target = 2
left = 0, right = 1

Iteration 1:
  mid = 0 + (1-0)//2 = 0
  arr[0] = 1 < 2 (target)
  -> left = mid = 0   <-- left stays at 0! No progress!

Iteration 2:
  mid = 0 + (1-0)//2 = 0
  arr[0] = 1 < 2 (target)
  -> left = mid = 0   <-- still 0! Infinite loop!

The condition left < right (0 < 1) is always True,
and left never advances because left = mid = 0.
```

### Understanding the Three Template Variants

There are three standard binary search templates. Each has different loop conditions and boundary updates. Mixing them causes bugs.

```
Template 1: while left <= right (most common, find exact match)
  - left starts at 0, right starts at len-1
  - left = mid + 1 when arr[mid] < target
  - right = mid - 1 when arr[mid] > target
  - Returns -1 when loop exits without finding

Template 2: while left < right (find left boundary)
  - left starts at 0, right starts at len
  - left = mid + 1 when condition(mid) is False
  - right = mid when condition(mid) is True
  - Returns left after loop exits

Template 3: while left + 1 < right (find boundary, explicit midpoint)
  - left and right are "invalid" boundaries, never checked
  - More conservative, less prone to edge case bugs
  - Returns left or right depending on problem
```

### Template 1: Exact Match (The Most Common)

```python
# RIGHT: Template 1 -- find exact match
def binary_search_exact(arr, target):
    left, right = 0, len(arr) - 1   # Both inclusive

    while left <= right:             # Loop until pointers cross
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid               # Found!
        elif arr[mid] < target:
            left = mid + 1           # Must be +1, not mid
        else:
            right = mid - 1          # Must be -1, not mid

    return -1   # Not found
```

### Template 2: Left Boundary Search

```python
# RIGHT: Template 2 -- find leftmost position where condition is true
def binary_search_left(arr, target):
    left, right = 0, len(arr)   # right = len (exclusive boundary)

    while left < right:          # Loop until left == right
        mid = left + (right - left) // 2
        if arr[mid] < target:
            left = mid + 1       # mid is not a valid answer, move past it
        else:
            right = mid          # mid might be the answer, keep it

    # left == right at this point
    # Check if a valid answer was found
    if left < len(arr) and arr[left] == target:
        return left
    return -1
```

### Two-Element Trace: Proving Template 1 Terminates

```
arr = [1, 2], target = 2 with Template 1:

Iteration 1:
  left=0, right=1
  mid = 0 + (1-0)//2 = 0
  arr[0]=1 < 2
  left = mid + 1 = 1

Iteration 2:
  left=1, right=1
  mid = 1 + (1-1)//2 = 1
  arr[1]=2 == target
  return 1  ✓

Template 1 ALWAYS terminates because:
  - When arr[mid] < target: left = mid+1 -> left strictly increases
  - When arr[mid] > target: right = mid-1 -> right strictly decreases
  - Either way, the interval [left, right] strictly shrinks each iteration.
```

---

## 3. Wrong Template for Boundary Search

### The Story: The First Seat in a Row

You are in a theater looking for the first available seat in row 5. You use binary search: you check the middle seat. It is available. You mark it as a "possible answer" and keep looking left to see if there is an earlier available seat. But if you are using the wrong template — the one that stops as soon as it finds ANY available seat — you stop at the middle one and miss the first one.

The "find exact" template returns ANY match. The "find leftmost" template returns the FIRST match. Mixing these up gives wrong answers on problems asking for the first or last occurrence.

### The Problem Setup

```python
arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]
target = 2
# Expected leftmost index: 3
# Expected rightmost index: 5
```

### The WRONG Code: "Find Any" When Asked for "Find First"

```python
# WRONG: Returns some occurrence of target, not necessarily the FIRST
def find_first_wrong(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid          # BUG: returns immediately without checking for earlier occurrences!
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1

arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]
print(find_first_wrong(arr, 2))  # Returns 4 (middle of the 2s) -- not 3!
```

### Visual Trace: Why It Returns the Wrong Index

```
arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]
idx:   0  1  2  3  4  5  6  7  8

left=0, right=8
mid = 4
arr[4] = 2 == target!
return 4 immediately.  <-- But first occurrence is at index 3!
```

### The RIGHT Code: Find Leftmost (First) Occurrence

```python
# RIGHT: Returns the FIRST (leftmost) occurrence of target
def find_first_right(arr, target):
    left, right = 0, len(arr) - 1
    result = -1   # track the best answer found so far

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid        # Record this as a possible answer
            right = mid - 1    # But keep searching LEFT for an earlier one!
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result

arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]
print(find_first_right(arr, 2))   # 3  -- correct!
print(find_first_right(arr, 1))   # 0  -- correct!
print(find_first_right(arr, 3))   # 6  -- correct!
print(find_first_right(arr, 4))  # -1  -- not found, correct!
```

### The RIGHT Code: Find Rightmost (Last) Occurrence

```python
# RIGHT: Returns the LAST (rightmost) occurrence of target
def find_last_right(arr, target):
    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid       # Record this as a possible answer
            left = mid + 1    # But keep searching RIGHT for a later one!
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result

arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]
print(find_last_right(arr, 2))   # 5  -- correct!
print(find_last_right(arr, 1))   # 2  -- correct!
print(find_last_right(arr, 3))   # 8  -- correct!
```

### Count Occurrences Using Both

```python
def count_occurrences(arr, target):
    first = find_first_right(arr, target)
    if first == -1:
        return 0
    last = find_last_right(arr, target)
    return last - first + 1

arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]
print(count_occurrences(arr, 2))  # 3  (indices 3, 4, 5)
print(count_occurrences(arr, 1))  # 3  (indices 0, 1, 2)
print(count_occurrences(arr, 4))  # 0  (not found)
```

---

## 4. Off-by-One in the Return Value

### The Story: The Pointer After the Race

At the end of a binary search, the loop exits and your two pointers `left` and `right` are sitting somewhere in the array. But WHERE exactly? And what does each pointer "mean" at that moment?

This is one of the most confusing aspects of binary search: after the loop exits, you need to know precisely what `left`, `right`, and `left-1` point to. Getting this wrong by 1 causes silent bugs — no error, just wrong answers.

### What the Pointers Mean After the Loop (Template 1)

```python
# Template 1: while left <= right
# After the loop exits (left > right):
#
#   right < left
#   right points to the last element < target
#   left  points to the first element > target
#   (or left/right is out of bounds if target is smaller/larger than all elements)
#
# Visualized:
#
#   arr = [1, 3, 5, 7, 9]  target = 6
#               ^right ^left
#   After loop: right = 2 (arr[2]=5, last element < 6)
#               left  = 3 (arr[3]=7, first element > 6)
```

### Step-by-Step Trace

```
arr = [1, 3, 5, 7, 9], target = 6

Iteration 1: left=0, right=4
  mid=2, arr[2]=5 < 6 -> left = 3

Iteration 2: left=3, right=4
  mid=3, arr[3]=7 > 6 -> right = 2

Loop exits: left=3 > right=2

State:
  arr:     [1,  3,  5,  7,  9]
  index:    0   1   2   3   4
                   ^R  ^L
  right=2: arr[2]=5 is the largest element < target
  left=3:  arr[3]=7 is the smallest element > target
  target (6) would be INSERTED at index 3 (= left)
```

### Common Return Value Decisions

```python
arr = [1, 3, 5, 7, 9]

# After template 1 loop exits with target not found:

# Q: "Where would target be inserted to keep sorted order?"
# A: return left
def insertion_point(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return left   # Index where target would be inserted

print(insertion_point([1, 3, 5, 7, 9], 6))  # 3 (between 5 and 7)
print(insertion_point([1, 3, 5, 7, 9], 0))  # 0 (before everything)
print(insertion_point([1, 3, 5, 7, 9], 10)) # 5 (after everything)


# Q: "Find the largest element <= target (floor)"
# A: return right (if right >= 0)
def floor_value(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] <= target:
            left = mid + 1
        else:
            right = mid - 1
    # right is the index of the largest element <= target
    if right < 0:
        return None   # all elements > target
    return arr[right]

print(floor_value([1, 3, 5, 7, 9], 6))   # 5  (largest <= 6)
print(floor_value([1, 3, 5, 7, 9], 5))   # 5  (exact match)
print(floor_value([1, 3, 5, 7, 9], 0))   # None (all > 0)


# Q: "Find the smallest element >= target (ceiling)"
# A: return left (if left < len(arr))
def ceiling_value(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    # left is the index of the smallest element >= target
    if left >= len(arr):
        return None   # all elements < target
    return arr[left]

print(ceiling_value([1, 3, 5, 7, 9], 6))   # 7  (smallest >= 6)
print(ceiling_value([1, 3, 5, 7, 9], 5))   # 5  (exact match)
print(ceiling_value([1, 3, 5, 7, 9], 10))  # None (all < 10)
```

### The Critical Summary Table

```
After Template 1 loop (while left <= right) exits WITHOUT finding target:

    ...elements < target... | ...elements > target...
                            ^right  ^left

    left  = index of first element > target (or len(arr) if target > all)
    right = index of last element < target  (or -1 if target < all)

    left = insertion point (for bisect_right behavior)
    right + 1 = left = same insertion point

    Return left when you want: insertion point, ceiling, count of elements <= target
    Return right when you want: floor, last element < target
```

---

## 5. Applying Binary Search to Unsorted Input

### The Story: Looking Up a Word in a Shuffled Dictionary

Binary search works because a sorted array has a predictable structure: if the middle is too small, the answer must be to the right; if too large, to the left. This reasoning collapses completely for an unsorted array. You look at the middle, decide to "go right," but the answer was actually to the left all along. Binary search gives wrong answers silently — no error, just a confident wrong result.

### The WRONG Code

```python
# WRONG: Binary search on an unsorted array
def binary_search_wrong(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# Test on shuffled array
shuffled = [5, 3, 8, 1, 9, 2, 7, 4, 6]
print(binary_search_wrong(shuffled, 7))  # -1  -- WRONG! 7 is at index 6.
print(binary_search_wrong(shuffled, 5))  # 0   -- happens to be correct (lucky!)
print(binary_search_wrong(shuffled, 4))  # -1  -- WRONG! 4 is at index 7.
```

### Visual Trace: Silent Wrong Answer

```
arr = [5, 3, 8, 1, 9, 2, 7, 4, 6], target = 7
      idx: 0  1  2  3  4  5  6  7  8

Iteration 1: left=0, right=8
  mid=4, arr[4]=9
  9 > 7  -> right = mid - 1 = 3
  (Binary search "decides" 7 must be to the left of index 4)
  (But 7 is at index 6 -- to the RIGHT! Wrong direction, wrong decision.)

Iteration 2: left=0, right=3
  mid=1, arr[1]=3
  3 < 7  -> left = mid + 1 = 2

Iteration 3: left=2, right=3
  mid=2, arr[2]=8
  8 > 7  -> right = 1

Loop exits: left=2 > right=1
Return -1  -- WRONG. 7 exists at index 6 but was never checked.
```

### The RIGHT Code: Sort First (Or Use Linear Search)

```python
# RIGHT Option A: Sort then binary search (when you only need to know IF it exists)
def contains_binary(arr, target):
    sorted_arr = sorted(arr)   # O(n log n)
    return binary_search_wrong(sorted_arr, target) != -1  # now correct on sorted

# RIGHT Option B: Linear search for unsorted (O(n) but correct)
def contains_linear(arr, target):
    for item in arr:
        if item == target:
            return True
    return False

# RIGHT Option C: Set membership (O(1) average, best for repeated queries)
def setup_search(arr):
    return set(arr)  # O(n) to build

lookup_set = setup_search([5, 3, 8, 1, 9, 2, 7, 4, 6])
print(7 in lookup_set)  # True -- O(1)!
print(10 in lookup_set) # False -- O(1)!


# Demonstration: never use binary search on unsorted input
shuffled = [5, 3, 8, 1, 9, 2, 7, 4, 6]

wrong_results = [(x, binary_search_wrong(shuffled, x)) for x in range(1, 10)]
for target, result in wrong_results:
    exists = target in shuffled
    correct = result != -1
    if exists != correct:
        print(f"WRONG: target={target}, in_array={exists}, binary_search_said={result!=-1}")

# Expected output shows several wrong answers:
# WRONG: target=4, in_array=True, binary_search_said=False
# WRONG: target=7, in_array=True, binary_search_said=False
# etc.
```

### Rotated Sorted Array: The Exception

```python
# Special case: Rotated sorted arrays can use a modified binary search
# e.g., [4, 5, 6, 7, 0, 1, 2] -- was sorted, then rotated

def search_rotated(arr, target):
    """Binary search in a rotated sorted array."""
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid

        # Determine which half is sorted
        if arr[left] <= arr[mid]:   # Left half is sorted
            if arr[left] <= target < arr[mid]:
                right = mid - 1    # Target is in sorted left half
            else:
                left = mid + 1     # Target is in right half
        else:                       # Right half is sorted
            if arr[mid] < target <= arr[right]:
                left = mid + 1     # Target is in sorted right half
            else:
                right = mid - 1    # Target is in left half

    return -1

print(search_rotated([4, 5, 6, 7, 0, 1, 2], 0))  # 4  -- correct!
print(search_rotated([4, 5, 6, 7, 0, 1, 2], 5))  # 1  -- correct!
```

---

## 6. bisect_left vs bisect_right for Duplicates

### The Story: The Queue with Identical Tickets

Imagine a sorted queue of people, some holding identical numbered tickets. You have a ticket and want to join. `bisect_left` says: "Get in at the leftmost position where your ticket number fits." `bisect_right` says: "Get in at the rightmost position where your ticket number fits."

For unique arrays, they give the same answer. For arrays with duplicates, they diverge — and using the wrong one causes subtle off-by-one errors.

### What bisect_left and bisect_right Return

```python
from bisect import bisect_left, bisect_right

arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]
#      0  1  2  3  4  5  6  7  8

# bisect_left: returns leftmost index where value CAN be inserted
# to keep sorted order (i.e., index of first occurrence)
print(bisect_left(arr, 1))   # 0  (insert before index 0 to keep sorted)
print(bisect_left(arr, 2))   # 3  (insert before index 3)
print(bisect_left(arr, 3))   # 6  (insert before index 6)
print(bisect_left(arr, 0))   # 0  (insert at beginning -- smaller than all)
print(bisect_left(arr, 4))   # 9  (insert at end -- larger than all)

# bisect_right: returns rightmost index where value CAN be inserted
# (i.e., index AFTER the last occurrence)
print(bisect_right(arr, 1))  # 3  (insert after all 1s, before first 2)
print(bisect_right(arr, 2))  # 6  (insert after all 2s, before first 3)
print(bisect_right(arr, 3))  # 9  (insert after all 3s, at the end)
```

### Visual: What Each Returns

```
arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]
       0  1  2  3  4  5  6  7  8

For target = 2:

bisect_left:          bisect_right:
  |                                   |
[1, 1, 1, | 2, 2, 2, 3, 3, 3]   [1, 1, 1, 2, 2, 2, | 3, 3, 3]
  Inserts before first 2             Inserts after last 2
  Returns 3                          Returns 6

bisect_left(arr, 2) = 3  = index of FIRST occurrence of 2
bisect_right(arr, 2) = 6 = index of element AFTER last 2
                         = index where 2.5 would be inserted
```

### The WRONG Code: Using Wrong bisect Function

```python
from bisect import bisect_left, bisect_right

arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]

# WRONG: Using bisect_right to find if target exists
def contains_wrong(arr, target):
    idx = bisect_right(arr, target)
    # idx points AFTER target's last occurrence
    # arr[idx] is NOT target (it's the next element)
    return idx < len(arr) and arr[idx] == target  # WRONG: arr[idx] is never target!

print(contains_wrong(arr, 2))  # False -- WRONG! 2 is in the array.

# WRONG: Using bisect_left to count occurrences
def count_wrong(arr, target):
    left = bisect_left(arr, target)
    # bisect_left gives start, but using bisect_left again for end is wrong
    right = bisect_left(arr, target + 1)  # This is actually correct for integers!
    # But for floats: bisect_left(arr, 2.5) might not give right answer
    return right - left
```

### The RIGHT Code

```python
from bisect import bisect_left, bisect_right

arr = [1, 1, 1, 2, 2, 2, 3, 3, 3]

# RIGHT: Check if target exists
def contains_right(arr, target):
    idx = bisect_left(arr, target)
    return idx < len(arr) and arr[idx] == target

print(contains_right(arr, 2))  # True
print(contains_right(arr, 4))  # False


# RIGHT: Find first occurrence
def first_occurrence(arr, target):
    idx = bisect_left(arr, target)
    if idx < len(arr) and arr[idx] == target:
        return idx
    return -1

print(first_occurrence(arr, 2))  # 3


# RIGHT: Find last occurrence
def last_occurrence(arr, target):
    idx = bisect_right(arr, target) - 1
    if idx >= 0 and arr[idx] == target:
        return idx
    return -1

print(last_occurrence(arr, 2))  # 5


# RIGHT: Count occurrences
def count_occurrences(arr, target):
    return bisect_right(arr, target) - bisect_left(arr, target)

print(count_occurrences(arr, 1))  # 3
print(count_occurrences(arr, 2))  # 3
print(count_occurrences(arr, 3))  # 3
print(count_occurrences(arr, 4))  # 0
```

### Practical Use: Insert Into Sorted List

```python
from bisect import insort_left, insort_right

# insort_left: inserts before existing equal values
# insort_right: inserts after existing equal values (default behavior of insort)

arr = [1, 2, 2, 3]
insort_left(arr, 2)
print(arr)   # [1, 2, 2, 2, 3] -- new 2 inserted before existing 2s

arr = [1, 2, 2, 3]
insort_right(arr, 2)
print(arr)   # [1, 2, 2, 2, 3] -- new 2 inserted after existing 2s
# Both produce [1, 2, 2, 2, 3] but at different positions within the 2s
```

---

## 7. Search Space is the Answer Range, Not the Array

### The Story: Guessing the Mystery Number

Your friend thinks of a number between 1 and 1,000,000. You do not search through a list of numbers — you binary search on the VALUE SPACE. "Is it more or less than 500,000?" Each question halves the search space. In 20 questions, you can find any number.

Many binary search problems on LeetCode are NOT about searching in an array — they are about searching on the ANSWER (the value range). Beginner mistake: trying to binary search the array index when you should be binary searching the value domain.

### Classic Example: Koko Eating Bananas

```
Problem: Koko has piles of bananas, e.g., [3, 6, 7, 11].
She must eat all bananas in h=8 hours.
Each hour she picks one pile and eats k bananas from it.
Find the minimum k (bananas per hour) such that she finishes in time.
```

```python
# WRONG: Searching on array index (wrong search space)
def koko_wrong(piles, h):
    # WRONG: Binary search on piles index
    left, right = 0, len(piles) - 1
    while left <= right:
        mid = left + (right - left) // 2
        # Check something with piles[mid]?
        # This makes no sense -- we need to search on the RATE k, not the pile index!
        pass
    return -1


# RIGHT: Binary search on the answer (the value of k)
def koko_right(piles, h):
    import math

    def can_finish(k):
        """Can Koko eat all piles in h hours with speed k?"""
        hours_needed = sum(math.ceil(pile / k) for pile in piles)
        return hours_needed <= h

    # Search space: k can range from 1 to max(piles)
    left, right = 1, max(piles)   # THIS is the search space: values of k!

    while left < right:
        mid = left + (right - left) // 2
        if can_finish(mid):
            right = mid      # mid might be the answer, search left for smaller
        else:
            left = mid + 1   # mid is too slow, need larger k

    return left

print(koko_right([3, 6, 7, 11], 8))  # 4
print(koko_right([30, 11, 23, 4, 20], 5))  # 30
```

### Why This Works: The Monotone Condition

```
For Koko's problem, the condition "can_finish(k) = True" has a clean structure:
  k=1:  can_finish? No  (too slow)
  k=2:  can_finish? No
  k=3:  can_finish? No
  k=4:  can_finish? Yes
  k=5:  can_finish? Yes
  k=6:  can_finish? Yes  (faster is always also valid)
  ...
  k=11: can_finish? Yes

Pattern:  No, No, No, ..., Yes, Yes, Yes, ...
         [              ][                  ]
                        ^ first Yes = answer

This is called a "monotone predicate" -- it switches from False to True exactly once.
Binary search finds the switch point in O(log(max_value)) time.
```

### Other "Binary Search on Answer" Problems

```python
import math

# Example 1: Minimum time to ship packages (LeetCode 1011)
def ship_packages(weights, days):
    """Minimum capacity to ship all weights within 'days' days."""
    def can_ship(capacity):
        current_day = 1
        current_load = 0
        for w in weights:
            if current_load + w > capacity:
                current_day += 1
                current_load = 0
            current_load += w
        return current_day <= days

    left = max(weights)        # minimum capacity (must fit largest package)
    right = sum(weights)       # maximum capacity (ship everything in one day)

    while left < right:
        mid = left + (right - left) // 2
        if can_ship(mid):
            right = mid
        else:
            left = mid + 1

    return left

print(ship_packages([1,2,3,4,5,6,7,8,9,10], 5))  # 15


# Example 2: Sqrt using binary search on the answer
def isqrt_binary(n):
    if n < 2:
        return n
    left, right = 1, n // 2

    while left <= right:
        mid = left + (right - left) // 2
        if mid * mid == n:
            return mid
        elif mid * mid < n:
            left = mid + 1
        else:
            right = mid - 1

    return right  # right = floor(sqrt(n))

print(isqrt_binary(16))   # 4
print(isqrt_binary(17))   # 4 (floor)
print(isqrt_binary(25))   # 5
```

### The Template for "Binary Search on Answer"

```python
def binary_search_on_answer(lo, hi, condition):
    """
    Find the minimum value in [lo, hi] where condition(value) is True.
    Requires: condition is False for all values < answer,
              condition is True for all values >= answer (monotone).
    """
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if condition(mid):
            hi = mid       # mid satisfies, look for smaller
        else:
            lo = mid + 1   # mid doesn't satisfy, need larger
    return lo  # lo == hi == minimum satisfying value
```

---

## 8. Linear Search When a Hash Set Is Better

### The Story: The Slow Librarian Who Reads Every Book

A librarian is asked "Is Moby Dick in the library?" She starts at shelf 1, checks every book. Takes 30 minutes. The smart librarian has a card catalog (hash map): looks up "Moby Dick" in 2 seconds.

`if x in list` is the slow librarian: O(n) per lookup. `if x in set` is the card catalog: O(1) average per lookup. When you do this inside a loop, it is O(n) × O(n) = O(n²) vs O(n) × O(1) = O(n).

### The WRONG Code

```python
# WRONG: Linear search inside a loop -- O(n²)
def find_pairs_wrong(arr, target):
    """Find all pairs that sum to target."""
    pairs = []
    for i in range(len(arr)):
        complement = target - arr[i]
        if complement in arr:  # BUG: linear search O(n) each time!
            if complement != arr[i]:  # avoid pairing with self
                pairs.append((arr[i], complement))
    return pairs

# For n=10,000: 10,000 iterations × 10,000 checks = 100,000,000 operations!
import time
n = 10_000
arr = list(range(n))
target = n - 1

start = time.time()
result = find_pairs_wrong(arr, target)
print(f"Linear search: {time.time()-start:.3f}s")
```

### Visual: O(n) vs O(1) Lookup

```
Linear search (list):
  arr = [5, 3, 8, 1, 9, 2, 7, 4, 6]
  Looking for 7:
  Check arr[0]=5? No.
  Check arr[1]=3? No.
  Check arr[2]=8? No.
  Check arr[3]=1? No.
  Check arr[4]=9? No.
  Check arr[5]=2? No.
  Check arr[6]=7? Yes! (6 checks)
  Worst case: n checks.

Hash set lookup:
  s = {5, 3, 8, 1, 9, 2, 7, 4, 6}
  Looking for 7:
  Compute hash(7) = 7 % table_size -> index -> check bucket
  Found in ~1 step (amortized O(1))
```

### The RIGHT Code: Use a Set

```python
# RIGHT: Hash set for O(1) lookups -- O(n) total
def find_pairs_right(arr, target):
    seen = set()
    pairs = set()
    for num in arr:
        complement = target - num
        if complement in seen:   # O(1) hash set lookup!
            pair = tuple(sorted([num, complement]))
            pairs.add(pair)
        seen.add(num)
    return list(pairs)

import time
n = 10_000
arr = list(range(n))
target = n - 1

start = time.time()
result = find_pairs_right(arr, target)
print(f"Hash set:      {time.time()-start:.4f}s")

# Typical output:
# Linear search:   2.500s
# Hash set:        0.002s  (1000x+ faster!)
```

### Common Patterns Where Sets Replace Linear Search

```python
# Pattern 1: "Does this element exist?" in a loop
# WRONG:
def has_duplicate_wrong(arr):
    for i in range(len(arr)):
        if arr[i] in arr[i+1:]:   # O(n) search in O(n) loop = O(n²)
            return True
    return False

# RIGHT:
def has_duplicate_right(arr):
    return len(arr) != len(set(arr))  # O(n) to build set, O(1) comparison

# Pattern 2: Intersection of two arrays
# WRONG:
def intersection_wrong(a, b):
    return [x for x in a if x in b]  # O(n*m)!

# RIGHT:
def intersection_right(a, b):
    return list(set(a) & set(b))  # O(n+m)


# Pattern 3: Sliding window "contains duplicate within k distance"
def contains_nearby_duplicate(nums, k):
    window = set()
    for i, num in enumerate(nums):
        if num in window:   # O(1) lookup
            return True
        window.add(num)
        if len(window) > k:
            window.remove(nums[i - k])   # O(1) removal
    return False
```

### When NOT to Replace with a Set

```python
# Sets do NOT preserve order.
# Sets do NOT support index access.
# Sets do NOT support binary search (use sorted list + bisect instead).

# Use a sorted list + bisect when you need:
# - Ordered iteration
# - Range queries ("all elements between 3 and 7")
# - Rank queries ("what is the 5th smallest element?")

import bisect

sorted_list = []
for val in [5, 3, 8, 1, 9, 2, 7, 4, 6]:
    bisect.insort(sorted_list, val)  # O(n) insert but maintains sorted order

print(sorted_list)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Range query: elements in [3, 7]
lo = bisect.bisect_left(sorted_list, 3)
hi = bisect.bisect_right(sorted_list, 7)
print(sorted_list[lo:hi])  # [3, 4, 5, 6, 7]
```

---

## 9. Missing the Check After the Loop Exits

### The Story: The Confident Announcer Who Never Verified

After the binary search loop exits, the announcer confidently says "Found at index left!" without checking if `arr[left]` actually equals the target. If the target was not in the array, `left` still points to some valid index — just not the target. The function returns a wrong index instead of -1.

### The WRONG Code

```python
# WRONG: Returning left without verifying arr[left] == target
def binary_search_wrong(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return left   # BUG: returns left even if arr[left] != target!

arr = [1, 3, 5, 7, 9]
print(binary_search_wrong(arr, 6))  # Returns 3 (arr[3]=7) -- WRONG, 6 is not in array!
print(binary_search_wrong(arr, 10)) # Returns 5 -- INDEX OUT OF BOUNDS risk!
```

### Visual Trace: The Unverified Left Pointer

```
arr = [1, 3, 5, 7, 9], target = 6

Iteration 1: left=0, right=4, mid=2, arr[2]=5 < 6 -> left=3
Iteration 2: left=3, right=4, mid=3, arr[3]=7 > 6 -> right=2
Loop exits: left=3, right=2

arr[3] = 7, which is NOT 6.
Returning left=3 says "6 is at index 3" which is WRONG.

For target=10:
Iteration 1: left=0, right=4, mid=2, arr[2]=5 < 10 -> left=3
Iteration 2: left=3, right=4, mid=3, arr[3]=7 < 10 -> left=4
Iteration 3: left=4, right=4, mid=4, arr[4]=9 < 10 -> left=5
Loop exits: left=5

arr[5] is INDEX OUT OF BOUNDS for a 5-element array!
```

### The RIGHT Code: Always Verify After the Loop

```python
# RIGHT: Verify arr[left] == target after the loop
def binary_search_right(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    # MUST verify: left might be out of bounds OR arr[left] != target
    if left < len(arr) and arr[left] == target:
        return left
    return -1   # target not found


arr = [1, 3, 5, 7, 9]
print(binary_search_right(arr, 6))   # -1  -- correct (6 not in array)
print(binary_search_right(arr, 7))   # 3   -- correct
print(binary_search_right(arr, 10))  # -1  -- correct (10 not in array)
print(binary_search_right(arr, 0))   # -1  -- correct (0 not in array)
```

### The Pattern: "Leftmost Insertion Point" vs "Find Exact"

```python
# Two different use cases with the same loop structure:

def find_exact(arr, target):
    """Returns index of target, or -1 if not found."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1   # Not found -- do NOT return left here


def find_insertion_point(arr, target):
    """Returns the index where target WOULD be inserted to maintain sorted order."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return left  # Here, returning left IS correct (it IS the insertion point, even if not in array)


arr = [1, 3, 5, 7, 9]
print(find_exact(arr, 6))             # -1  (6 not in array)
print(find_insertion_point(arr, 6))   # 3   (would be inserted at index 3: [1,3,5,6,7,9])
```

---

## 10. DFS vs BFS for Shortest Path

### The Story: The Maze Navigator

You are in a maze and need to find the shortest path to the exit. DFS (depth-first search) charges ahead down one corridor, going as deep as possible. It might find the exit after traveling 100 steps — but that is not necessarily the shortest path. There was a shorter 3-step path, but DFS went deep in the wrong direction first.

BFS (breadth-first search) explores layer by layer: first all 1-step neighbors, then all 2-step neighbors, then all 3-step neighbors. The FIRST time it reaches the exit, that path is guaranteed to be the shortest (in an unweighted graph).

### The WRONG Code: DFS for Shortest Path

```python
# WRONG: Using DFS to find shortest path in unweighted graph
def shortest_path_dfs_wrong(graph, start, end):
    """Returns a path from start to end using DFS -- NOT guaranteed shortest!"""
    def dfs(node, path, visited):
        if node == end:
            return path
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                result = dfs(neighbor, path + [neighbor], visited)
                if result:
                    return result   # Returns FIRST path found, not SHORTEST!
        return None

    return dfs(start, [start], set())


# Test graph: A -> B -> E (short path) OR A -> C -> D -> E (long path)
graph = {
    'A': ['C', 'B'],   # DFS will explore C first (alphabetical or insertion order)
    'B': ['E'],
    'C': ['D'],
    'D': ['E'],
    'E': [],
}

wrong_path = shortest_path_dfs_wrong(graph, 'A', 'E')
print("DFS path:", wrong_path)  # ['A', 'C', 'D', 'E'] -- 3 edges, NOT shortest!
# Shortest is ['A', 'B', 'E'] -- 2 edges
```

### Visual Trace: DFS Goes Deep in the Wrong Direction

```
Graph:
  A ----> B ----> E
  |
  v
  C ----> D ----> E

DFS from A (exploring C before B due to adjacency list order):
  Visit A
    Explore C (depth-first)
      Visit C
        Explore D
          Visit D
            Explore E
              Visit E -- FOUND! Path: A->C->D->E (length 3)
              Return immediately.

DFS never explores A->B->E (length 2) because it returned as soon
as it found ANY path to E.

Result: ['A', 'C', 'D', 'E'] -- 3 hops
Shortest: ['A', 'B', 'E'] -- 2 hops

DFS was WRONG for shortest path.
```

### The RIGHT Code: BFS for Shortest Path

```python
# RIGHT: BFS guarantees shortest path in unweighted graphs
from collections import deque

def shortest_path_bfs(graph, start, end):
    """Returns the shortest path from start to end (unweighted graph)."""
    if start == end:
        return [start]

    queue = deque([[start]])          # queue of paths, not just nodes
    visited = {start}

    while queue:
        path = queue.popleft()        # get the next path to explore
        node = path[-1]               # current node is last in path

        for neighbor in graph[node]:
            if neighbor == end:
                return path + [neighbor]   # FIRST time we reach end = shortest!

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return None  # no path found


graph = {
    'A': ['C', 'B'],
    'B': ['E'],
    'C': ['D'],
    'D': ['E'],
    'E': [],
}

right_path = shortest_path_bfs(graph, 'A', 'E')
print("BFS path:", right_path)  # ['A', 'B', 'E'] -- 2 edges, SHORTEST!
```

### Memory-Efficient BFS: Track Distance Instead of Full Path

```python
from collections import deque

def shortest_distance_bfs(graph, start, end):
    """Returns the shortest distance (hop count) from start to end."""
    if start == end:
        return 0

    queue = deque([(start, 0)])  # (node, distance)
    visited = {start}

    while queue:
        node, dist = queue.popleft()

        for neighbor in graph[node]:
            if neighbor == end:
                return dist + 1   # shortest distance!

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))

    return -1   # no path


# Test
print(shortest_distance_bfs(graph, 'A', 'E'))  # 2


# Even more memory efficient: BFS with parent tracking
def shortest_path_with_parents(graph, start, end):
    """Returns the shortest path, tracking parent pointers instead of full paths."""
    if start == end:
        return [start]

    parent = {start: None}
    queue = deque([start])

    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in parent:
                parent[neighbor] = node
                if neighbor == end:
                    # Reconstruct path
                    path = []
                    curr = end
                    while curr is not None:
                        path.append(curr)
                        curr = parent[curr]
                    return list(reversed(path))
                queue.append(neighbor)

    return None

print(shortest_path_with_parents(graph, 'A', 'E'))  # ['A', 'B', 'E']
```

### BFS Level-by-Level (The Classic Template)

```python
from collections import deque

def bfs_levels(graph, start):
    """BFS exploring level by level, tracking distance from start."""
    distances = {start: 0}
    queue = deque([start])

    while queue:
        node = queue.popleft()

        for neighbor in graph[node]:
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)

    return distances

# Test
graph2 = {
    0: [1, 2],
    1: [3, 4],
    2: [5],
    3: [],
    4: [],
    5: [6],
    6: [],
}

dists = bfs_levels(graph2, 0)
print(dists)
# {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 3}

# The distance to each node is the shortest path length.
# 0 is at distance 0
# 1, 2 are at distance 1 (direct neighbors)
# 3, 4, 5 are at distance 2
# 6 is at distance 3
```

### When to Use DFS vs BFS

```
Use BFS when:
  - Shortest path in UNWEIGHTED graph (guaranteed correct)
  - Level-order traversal (exploring neighbors before going deeper)
  - "Minimum steps to reach X" problems
  - Flood fill (painting connected regions)
  - Finding closest X from a source

Use DFS when:
  - Detecting cycles
  - Topological sort
  - Exploring ALL paths (not just shortest)
  - Connected components
  - Backtracking (solving mazes by exploring all options)
  - When memory is a concern (DFS uses O(depth) stack vs BFS uses O(width) queue)

Use Dijkstra when:
  - Shortest path in WEIGHTED graph (non-negative weights)

Use Bellman-Ford when:
  - Shortest path in WEIGHTED graph with NEGATIVE weights
```

### Mini Test Case

```python
# Prove BFS gives shortest path, DFS does not
def run_comparison():
    # A graph where DFS takes the long route
    # 0 -> 1 -> 4  (length 2)
    # 0 -> 2 -> 3 -> 4  (length 3)
    graph = {
        0: [2, 1],   # 2 listed before 1, so DFS explores 2 first
        1: [4],
        2: [3],
        3: [4],
        4: [],
    }

    dfs_path = shortest_path_dfs_wrong(graph, 0, 4)
    bfs_path = shortest_path_bfs(graph, 0, 4)

    print(f"DFS path: {dfs_path} (length {len(dfs_path)-1})")
    print(f"BFS path: {bfs_path} (length {len(bfs_path)-1})")

    assert len(bfs_path) <= len(dfs_path), "BFS should always find <= length path"
    print("BFS is always <= DFS in unweighted shortest path!")

run_comparison()
# DFS path: [0, 2, 3, 4] (length 3)
# BFS path: [0, 1, 4] (length 2)
# BFS is always <= DFS in unweighted shortest path!
```

---

## Quick Reference: All 10 Mistakes at a Glance

```
#   Mistake                          | Quick Fix
----|----------------------------------|-------------------------------------------------
1   Overflow in midpoint              | Use left + (right - left) // 2 (safe in all languages)
2   Infinite loop: wrong boundary     | Template 1: left=mid+1, right=mid-1. Never left=mid.
3   Wrong template for boundary       | Find first: record result, keep right=mid-1 to search left
4   Off-by-one in return value        | After loop: left=insertion point, right=last element < target
5   Binary search on unsorted input   | Sort first OR use set/linear search for unsorted
6   bisect_left vs bisect_right       | left=first occurrence, right-1=last occurrence, right-left=count
7   Search on array vs answer range   | "Minimize X s.t. condition(X)" -> binary search on X values
8   Linear search in a loop           | Convert list to set before the loop for O(1) lookups
9   Missing check after loop exits    | Always: if left < len(arr) and arr[left] == target: return left
10  DFS for shortest path             | Use BFS for shortest path in unweighted graphs
```

---

## Binary Search Template Cheat Sheet

```python
# Template 1: Find exact value
def search_exact(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: left = mid + 1
        else: right = mid - 1
    return -1


# Template 2: Find leftmost (first occurrence)
def search_leftmost(arr, target):
    left, right = 0, len(arr) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid
            right = mid - 1    # keep searching left!
        elif arr[mid] < target: left = mid + 1
        else: right = mid - 1
    return result


# Template 3: Find rightmost (last occurrence)
def search_rightmost(arr, target):
    left, right = 0, len(arr) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid
            left = mid + 1     # keep searching right!
        elif arr[mid] < target: left = mid + 1
        else: right = mid - 1
    return result


# Template 4: Binary search on answer
def search_on_answer(lo, hi, is_feasible):
    """Find minimum value in [lo, hi] where is_feasible(value) is True."""
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if is_feasible(mid): hi = mid
        else: lo = mid + 1
    return lo
```

---

## Final Checklist Before Submitting Search Code

```
[ ] Did I use left + (right - left) // 2 for midpoint?
[ ] Is my boundary update mid+1/mid-1 (never just mid in Template 1)?
[ ] Am I using the right template (exact / leftmost / rightmost)?
[ ] Did I verify arr[left] == target after the loop exits?
[ ] Is the input array guaranteed sorted? If not, sort it first.
[ ] For duplicates: did I choose bisect_left vs bisect_right correctly?
[ ] Is my search space the VALUE RANGE (not the array) for "minimize X" problems?
[ ] Did I replace any "x in list" inside a loop with a set lookup?
[ ] Am I using BFS (not DFS) for shortest path in an unweighted graph?
[ ] Did I handle the edge cases: empty array, single element, target not present?
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real World Usage](./real_world_usage.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
