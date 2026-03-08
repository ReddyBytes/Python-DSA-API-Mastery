# Two Pointers — Pattern Recognition Guide

> **Core Idea**: Use two index variables to avoid nested loops, reducing O(n²) → O(n).
> The key insight is that both pointers together scan the array without redundant comparisons.

---

## 1. Pattern Recognition Signals

When you see these features in a problem, think "two pointers":

| Signal | Example Phrasing |
|--------|-----------------|
| Sorted array / sorted input | "Given a sorted array…" |
| Find a pair with a target sum | "Find two numbers that sum to X" |
| Palindrome check | "Determine if string is a palindrome" |
| Remove/partition in-place | "Remove duplicates in-place, return length" |
| Linked list cycle or midpoint | "Detect cycle", "Find middle node" |
| Container / area problems | "Max water between walls" |
| Merge two sorted sequences | "Merge two sorted arrays" |
| Slow and fast movement | "Move zeros to end", "Partition around pivot" |

**Anti-signals** (do NOT use two pointers):
- Unsorted array where order matters
- Need to find all pairs (use hash map instead)
- Subarray problems with a running sum constraint (use sliding window)

---

## 2. Pattern 1: Converging Pointers (Opposite Ends)

**Mental model**: Start from both ends, move toward center based on a condition.

**When to use**:
- Sorted array, find pair with target sum
- Palindrome validation
- Container with most water
- Three-sum (outer loop + inner converging pair)

### Template

```python
def converging_pointers(arr, target):
    left, right = 0, len(arr) - 1  # start at both ends

    while left < right:             # stop when they meet
        current = arr[left] + arr[right]

        if current == target:
            # FOUND: process answer
            return [left, right]

        elif current < target:
            left += 1               # need larger value → move left forward

        else:
            right -= 1              # need smaller value → move right back

    return []                       # no answer found
```

**Key invariant**: Everything to the left of `left` and to the right of `right` has already been eliminated.

---

### Worked Example 1: Two Sum II (Sorted Array)

**Problem**: Array is sorted. Find indices of two numbers that add to `target`.

```python
def two_sum_sorted(numbers, target):
    left, right = 0, len(numbers) - 1

    while left < right:
        s = numbers[left] + numbers[right]

        if s == target:
            return [left + 1, right + 1]  # 1-indexed answer

        elif s < target:
            left += 1    # sum too small, move left pointer right (larger value)

        else:
            right -= 1   # sum too large, move right pointer left (smaller value)

    return []

# Trace: numbers=[2,7,11,15], target=9
# Step 1: left=0(2), right=3(15), sum=17 > 9 → right-=1
# Step 2: left=0(2), right=2(11), sum=13 > 9 → right-=1
# Step 3: left=0(2), right=1(7),  sum=9 == 9 → return [1,2]
```

---

### Worked Example 2: Container With Most Water

**Problem**: Array of heights. Find two lines forming the container holding max water.

```python
def max_water(height):
    left, right = 0, len(height) - 1
    max_area = 0

    while left < right:
        # Area = width × min(left_height, right_height)
        width = right - left
        area = width * min(height[left], height[right])
        max_area = max(max_area, area)

        # Move the shorter wall — the taller wall can only help with a wider container
        # Moving the taller wall can never increase area (width shrinks, height limited by shorter)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return max_area

# Trace: height=[1,8,6,2,5,4,8,3,7]
# left=0(1), right=8(7) → area=1*1=1, move left
# left=1(8), right=8(7) → area=7*7=49, move right
# left=1(8), right=7(3) → area=6*3=18, move right
# ... eventually max_area=49
```

---

## 3. Pattern 2: Parallel Pointers (Same Direction, Different Roles)

**Mental model**: One pointer reads, one pointer writes (or partitions).
Both move left to right, but at different rates or triggered by different conditions.

**When to use**:
- Remove duplicates from sorted array (in-place)
- Move zeros to end
- Partition array around a value
- Separate even/odd, negative/positive

### Template

```python
def parallel_pointers(arr):
    write = 0   # "slow" pointer: marks next position to write valid element

    for read in range(len(arr)):   # "fast" pointer: scans every element
        if is_valid(arr[read]):    # condition: should this element be kept?
            arr[write] = arr[read] # write valid element at write position
            write += 1             # advance write pointer

    return write   # write = length of valid portion
```

**Key invariant**: `arr[0..write-1]` always contains the valid/processed elements.

---

### Worked Example 1: Remove Duplicates from Sorted Array

```python
def remove_duplicates(nums):
    if not nums:
        return 0

    write = 1   # first element is always unique, start write at index 1

    for read in range(1, len(nums)):
        if nums[read] != nums[read - 1]:   # new unique element found
            nums[write] = nums[read]        # place it at write position
            write += 1

    return write   # nums[0..write-1] has unique elements

# Trace: nums=[1,1,2,3,3,4]
# read=1: nums[1]==nums[0] (1==1), skip
# read=2: nums[2]!=nums[1] (2!=1) → nums[1]=2, write=2
# read=3: nums[3]!=nums[2] (3!=2) → nums[2]=3, write=3
# read=4: nums[4]==nums[3] (3==3), skip
# read=5: nums[5]!=nums[4] (4!=3) → nums[3]=4, write=4
# Result: nums=[1,2,3,4,...], return 4
```

---

### Worked Example 2: Move Zeros to End

```python
def move_zeros(nums):
    write = 0   # position for next non-zero element

    # Pass 1: move all non-zeros to front
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write] = nums[read]
            write += 1

    # Pass 2: fill remaining positions with zeros
    while write < len(nums):
        nums[write] = 0
        write += 1

# Alternative: single pass with swap
def move_zeros_swap(nums):
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1

# Trace: nums=[0,1,0,3,12]
# read=0: 0, skip (write=0)
# read=1: 1≠0 → swap(0,1) → [1,0,0,3,12], write=1
# read=2: 0, skip
# read=3: 3≠0 → swap(1,3) → [1,3,0,0,12], write=2
# read=4: 12≠0 → swap(2,4) → [1,3,12,0,0], write=3
```

---

## 4. Pattern 3: Fast / Slow Pointers — Floyd's Algorithm (Linked Lists)

**Mental model**: Fast pointer moves 2× speed of slow pointer.
In a cycle, they must eventually meet. In a straight list, fast reaches end first.

**When to use**:
- Detect cycle in linked list
- Find the middle node
- Find the entry point of a cycle
- Determine if linked list length is even/odd

### Template — Cycle Detection

```python
def has_cycle(head):
    slow = fast = head

    while fast and fast.next:      # fast needs 2 steps → check both
        slow = slow.next           # move 1 step
        fast = fast.next.next      # move 2 steps

        if slow == fast:           # they met → cycle exists
            return True

    return False   # fast hit None → no cycle
```

### Template — Find Middle Node

```python
def find_middle(head):
    slow = fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    # When fast reaches end, slow is at middle
    # For even length: slow lands at second middle (e.g., index n//2)
    return slow
```

### Template — Find Cycle Entry Point

```python
def detect_cycle_entry(head):
    slow = fast = head

    # Phase 1: Detect cycle
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None   # no cycle

    # Phase 2: Find entry
    # Math: distance from head to entry == distance from meeting point to entry
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next

    return slow   # entry point of cycle
```

---

### Worked Example 1: Linked List Cycle Detection

```python
# List: 1 → 2 → 3 → 4 → 5 → 3 (cycle back to node with value 3)
#
# Step 1: slow=1, fast=1
# Step 2: slow=2, fast=3
# Step 3: slow=3, fast=5
# Step 4: slow=4, fast=4  ← MEET (fast jumped from 5 to 3 to... wait, let's be precise)
# Actually with cycle at index 2 (0-based):
# Step 1: slow=2, fast=3
# Step 2: slow=3, fast=5
# Step 3: slow=4, fast=4  ← cycle wraps fast back → MEET
# Return True
```

---

### Worked Example 2: Find Middle of Linked List

```python
# List: 1 → 2 → 3 → 4 → 5
#
# Start: slow=1, fast=1
# Step 1: slow=2, fast=3
# Step 2: slow=3, fast=5
# Step 3: fast.next=None → loop ends
# Return slow=3 (middle) ✓

# List: 1 → 2 → 3 → 4
#
# Start: slow=1, fast=1
# Step 1: slow=2, fast=3
# Step 2: slow=3, fast=None → loop ends (fast.next was None)
# Return slow=3 (second middle of even-length list)
```

---

## 5. Pattern 4: Merge Two Sorted Sequences

**Mental model**: Two pointers, one per array. Always advance the pointer with the smaller value.

**When to use**:
- Merge sort's merge step
- Intersection / union of sorted arrays
- Compare characters in two strings (with transformations)

### Template

```python
def merge_sorted(arr1, arr2):
    i, j = 0, 0
    result = []

    while i < len(arr1) and j < len(arr2):
        if arr1[i] <= arr2[j]:
            result.append(arr1[i])
            i += 1
        else:
            result.append(arr2[j])
            j += 1

    # Append remaining elements (only one of these will execute)
    result.extend(arr1[i:])
    result.extend(arr2[j:])

    return result
```

### Variant: Intersection of Two Sorted Arrays

```python
def intersection(arr1, arr2):
    i, j = 0, 0
    result = []

    while i < len(arr1) and j < len(arr2):
        if arr1[i] == arr2[j]:
            result.append(arr1[i])
            i += 1
            j += 1
        elif arr1[i] < arr2[j]:
            i += 1   # arr1 is behind, catch up
        else:
            j += 1   # arr2 is behind, catch up

    return result
```

---

## 6. Pattern Decision Matrix

| Problem Type | Array Sorted? | Key Signal | Use Pattern |
|---|---|---|---|
| Find pair summing to target | Yes | Two values | Converging Pointers |
| Find pair summing to target | No | Two values | Hash Map |
| Palindrome check (string/array) | N/A | Compare ends | Converging Pointers |
| Container with most water | N/A | Max area | Converging Pointers |
| Three-sum problem | Sort first | Triplet | Converging (inner) + loop (outer) |
| Remove duplicates in-place | Yes (sorted) | In-place | Parallel Pointers |
| Move zeros / partition | N/A | In-place filter | Parallel Pointers |
| Cycle in linked list | N/A | Linked list | Fast/Slow |
| Middle of linked list | N/A | Linked list | Fast/Slow |
| Cycle entry point | N/A | Linked list | Fast/Slow (2 phases) |
| Merge two sorted sequences | Yes | Two arrays | Merge Pointers |

---

## 7. Combined Patterns

### Two Pointers + Binary Search: Three-Sum Closest

When you have a sorted array and need the closest sum:

```python
def three_sum_closest(nums, target):
    nums.sort()
    closest = float('inf')

    for i in range(len(nums) - 2):
        left, right = i + 1, len(nums) - 1   # converging pointers for inner pair

        while left < right:
            s = nums[i] + nums[left] + nums[right]

            if abs(s - target) < abs(closest - target):
                closest = s

            if s < target:
                left += 1
            elif s > target:
                right -= 1
            else:
                return s   # exact match

    return closest
```

### Two Pointers + Hash Map: Four-Sum

Use a hash map to store pair sums, then two-pointer over the remaining structure:

```python
def four_sum_count(A, B, C, D):
    from collections import defaultdict

    # Hash map stores all pair sums from A and B
    ab_sums = defaultdict(int)
    for a in A:
        for b in B:
            ab_sums[a + b] += 1

    # Two pointers on C and D looking for complement
    count = 0
    for c in C:
        for d in D:
            complement = -(c + d)
            count += ab_sums[complement]

    return count
```

### Two Pointers + Sliding Window: Minimum Window Substring

When the "pair" concept expands to a "window":

```python
# See sliding_window/patterns.md for the full template
# The expand/shrink dynamic is two pointers (left, right) on a string
# with a hash map tracking character counts
def min_window(s, t):
    from collections import Counter
    need = Counter(t)
    have = {}
    formed = 0
    required = len(need)

    left = 0
    result = (float('inf'), 0, 0)

    for right in range(len(s)):         # right pointer always expands
        char = s[right]
        have[char] = have.get(char, 0) + 1
        if char in need and have[char] == need[char]:
            formed += 1

        while formed == required:       # left pointer shrinks when valid
            if right - left + 1 < result[0]:
                result = (right - left + 1, left, right)
            have[s[left]] -= 1
            if s[left] in need and have[s[left]] < need[s[left]]:
                formed -= 1
            left += 1

    return "" if result[0] == float('inf') else s[result[1]:result[2]+1]
```

---

## Quick Reference: Pointer Movement Rules

```
Converging:
  sum < target  → left += 1   (need bigger)
  sum > target  → right -= 1  (need smaller)
  sum == target → found!

Parallel (read/write):
  valid element → write it, advance write
  invalid       → skip (only advance read)

Fast/Slow:
  slow += 1 step always
  fast += 2 steps always
  meeting point → cycle exists

Merge:
  arr1[i] <= arr2[j] → take from arr1, i += 1
  else               → take from arr2, j += 1
```
