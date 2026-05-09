# Arrays — Practice Questions

> 25 questions covering theory, visual patterns, real-world usage, and common mistakes.
> Work through these in order — difficulty builds from Basic to Advanced.

---

## Quick Index

| # | Slug | Title | Difficulty |
|---|------|-------|-----------|
| [Q1](#q1) | array-indexing | Why Is Indexing O(1)? | Basic |
| [Q2](#q2) | dynamic-resize | Dynamic Array Resizing | Basic |
| [Q3](#q3) | insert-delete-complexity | Insert vs Delete Complexity | Basic |
| [Q4](#q4) | 2d-grid-init | Initialize a 2D Grid Correctly | Basic |
| [Q5](#q5) | reverse-in-place | Reverse an Array In-Place | Basic |
| [Q6](#q6) | contains-duplicate | Contains Duplicate | Basic |
| [Q7](#q7) | move-zeros | Move Zeros to End | Basic |
| [Q8](#q8) | remove-duplicates-sorted | Remove Duplicates from Sorted Array | Basic |
| [Q9](#q9) | prefix-sum-build | Build a Prefix Sum Array | Intermediate |
| [Q10](#q10) | range-sum-query | Range Sum Query | Intermediate |
| [Q11](#q11) | subarray-sum-k | Count Subarrays with Sum K | Intermediate |
| [Q12](#q12) | max-subarray-kadane | Maximum Subarray (Kadane's) | Intermediate |
| [Q13](#q13) | two-pointer-pair-sum | Two-Pointer Pair Sum | Intermediate |
| [Q14](#q14) | three-sum | Three Sum (Triplets to Zero) | Intermediate |
| [Q15](#q15) | rotate-array | Rotate Array Right by K | Intermediate |
| [Q16](#q16) | dutch-flag | Dutch National Flag Sort | Intermediate |
| [Q17](#q17) | product-except-self | Product of Array Except Self | Intermediate |
| [Q18](#q18) | sliding-window-max-avg | Sliding Window Maximum Average | Intermediate |
| [Q19](#q19) | two-pointer-without-sort | Why Two-Pointer Requires Sorting | Intermediate |
| [Q20](#q20) | shallow-vs-deep-copy | Shallow vs Deep Copy Trap | Intermediate |
| [Q21](#q21) | numpy-vs-list | NumPy vs Python List Tradeoffs | Intermediate |
| [Q22](#q22) | circular-buffer | Implement a Circular Buffer | Advanced |
| [Q23](#q23) | merge-intervals | Merge Overlapping Intervals | Advanced |
| [Q24](#q24) | trapping-rain-water | Trapping Rain Water | Advanced |
| [Q25](#q25) | subarray-with-target-sum | Find Subarray with Exact Sum (HashMap + Prefix) | Advanced |

---

## Basic Questions (Q1–Q8)

---

<a id="q1"></a>
### Q1 · array-indexing — Why Is Indexing O(1)? 🔢

Explain why `arr[i]` runs in constant time regardless of array size.
Then write a function that returns the element at a given index, and explain what happens at the memory level.

```
Input: arr = [10, 20, 30, 40, 50], i = 3
Output: 40
```

<details>
<summary>Hint</summary>
Think about the formula: address = base + (index × element_size). How many arithmetic operations does that take?
</details>

<details>
<summary>Answer</summary>

```python
def get_element(arr: list, i: int):
    return arr[i]   # ← one memory lookup via base + offset formula

# Memory model:
# base = 1000 (hypothetical start address)
# element_size = 8 bytes (Python object pointer)
# arr[3] -> address = 1000 + (3 × 8) = 1024
# One arithmetic op. Same cost whether arr has 5 or 5 million elements.
```

**Why:** Arrays store elements in **contiguous memory**. The CPU computes the exact address with one multiplication and one addition — no looping, no searching. The computation cost is independent of n.
Time: O(1) · Space: O(1)
</details>

---

<a id="q2"></a>
### Q2 · dynamic-resize — Dynamic Array Resizing 📦

Answer both parts:
1. When does Python's list trigger a resize, and what happens internally?
2. Why is `append` described as amortized O(1) rather than O(1)?

<details>
<summary>Hint</summary>
Think about what "amortized" means: the expensive operation (copying) is rare enough that its cost, spread across many appends, averages out.
</details>

<details>
<summary>Answer</summary>

```python
import sys

arr = []
prev_size = sys.getsizeof(arr)

for i in range(20):
    arr.append(i)
    new_size = sys.getsizeof(arr)
    if new_size != prev_size:
        print(f"Resize at len={len(arr)}: {prev_size} -> {new_size} bytes")
        prev_size = new_size

# Resize triggers at: 1, 5, 9, 17... (approximate growth factor ~1.125 in CPython)
```

**Why:** When capacity is full, Python allocates a larger block (roughly 1.125x), copies all n existing elements, then inserts the new one. This copy costs O(n), but it happens rarely — once every ~n appends. Spreading that O(n) cost over n appends gives **amortized O(1)** per append. The total work for n appends is O(n), not O(n²).
Time: O(1) amortized per append · Space: O(n)
</details>

---

<a id="q3"></a>
### Q3 · insert-delete-complexity — Insert vs Delete Complexity 🔀

Given the array below, perform the following operations and state the exact number of element shifts required for each:

```
arr = [10, 20, 30, 40, 50]
a) Insert 99 at index 1
b) Delete element at index 2
```

<details>
<summary>Hint</summary>
Count how many elements must shift after the insertion/deletion point.
</details>

<details>
<summary>Answer</summary>

```python
# (a) Insert 99 at index 1:
arr = [10, 20, 30, 40, 50]
arr.insert(1, 99)
# [10, 99, 20, 30, 40, 50]
# Elements shifted: 20, 30, 40, 50 → 4 shifts (n - index = 5 - 1 = 4)

# (b) Delete index 2 (value 30):
arr = [10, 20, 30, 40, 50]
arr.pop(2)
# [10, 20, 40, 50]
# Elements shifted: 40, 50 → 2 shifts (n - index - 1 = 5 - 2 - 1 = 2)

# Worst case: insert or delete at index 0 → shifts all n elements → O(n)
# Best case: insert or delete at the end → 0 shifts → O(1)
```

**Why:** Arrays are contiguous. Every element after the insertion/deletion point must physically move one position. The shift count equals `n - index`, which in the worst case (index 0) is n.
Time: O(n) worst case · Space: O(1) (in-place)
</details>

---

<a id="q4"></a>
### Q4 · 2d-grid-init — Initialize a 2D Grid Correctly 🗂️

Create a 3×4 grid of zeros. Then write code that demonstrates why `[[0]*4]*3` is a trap and `[[0]*4 for _ in range(3)]` is correct.

```
Expected after grid[1][2] = 9:
Row 0: [0, 0, 0, 0]
Row 1: [0, 0, 9, 0]   ← only row 1 changed
Row 2: [0, 0, 0, 0]
```

<details>
<summary>Hint</summary>
The multiplication operator on a list creates references to the same inner object, not copies.
</details>

<details>
<summary>Answer</summary>

```python
# WRONG: multiplication creates 3 references to the SAME inner list
bad_grid = [[0] * 4] * 3
bad_grid[1][2] = 9
for row in bad_grid:
    print(row)
# [0, 0, 9, 0]
# [0, 0, 9, 0]   ← all rows mutated — they all point to the same object
# [0, 0, 9, 0]

# RIGHT: comprehension creates a NEW inner list on each iteration
good_grid = [[0] * 4 for _ in range(3)]   # ← fresh list per row
good_grid[1][2] = 9
for row in good_grid:
    print(row)
# [0, 0, 0, 0]
# [0, 0, 9, 0]   ← only row 1 changed
# [0, 0, 0, 0]
```

**Why:** `[x] * n` stores n pointers to the same object. Mutating via any pointer mutates the shared object. The comprehension calls `[0]*4` on each iteration, creating independent list objects at different memory addresses.
Time: O(n*m) to build · Space: O(n*m)
</details>

---

<a id="q5"></a>
### Q5 · reverse-in-place — Reverse an Array In-Place ↩️

Reverse the array `[1, 2, 3, 4, 5]` in-place using the two-pointer technique. No built-in `.reverse()` or slicing.

```
Input:  [1, 2, 3, 4, 5]
Output: [5, 4, 3, 2, 1]
```

<details>
<summary>Hint</summary>
Use a left pointer starting at 0 and a right pointer starting at n-1. Swap and move both inward until they meet.
</details>

<details>
<summary>Answer</summary>

```python
def reverse_in_place(arr: list) -> list:
    left, right = 0, len(arr) - 1   # ← two pointers at opposite ends
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]   # ← swap
        left += 1
        right -= 1
    return arr

print(reverse_in_place([1, 2, 3, 4, 5]))   # [5, 4, 3, 2, 1]
print(reverse_in_place([1, 2]))             # [2, 1]
print(reverse_in_place([1]))               # [1]
```

**Why:** The **two-pointer** pattern starts at both ends and converges inward. Each swap places both elements in their final positions, so n/2 swaps suffice. No extra array needed — pure in-place.
Time: O(n) · Space: O(1)
</details>

---

<a id="q6"></a>
### Q6 · contains-duplicate — Contains Duplicate 🔍

Given an integer array, return `True` if any value appears at least twice, `False` if all elements are distinct.

```
Input: [1, 2, 3, 1]     Output: True
Input: [1, 2, 3, 4]     Output: False
```

<details>
<summary>Hint</summary>
A set can check membership in O(1). As you iterate, add each element; if it is already in the set, you found a duplicate.
</details>

<details>
<summary>Answer</summary>

```python
def contains_duplicate(nums: list) -> bool:
    seen = set()
    for num in nums:
        if num in seen:   # ← O(1) hash lookup
            return True
        seen.add(num)
    return False

# Alternatively, one-liner:
def contains_duplicate_v2(nums: list) -> bool:
    return len(nums) != len(set(nums))   # ← set deduplicates, compare lengths

print(contains_duplicate([1, 2, 3, 1]))   # True
print(contains_duplicate([1, 2, 3, 4]))   # False
```

**Why:** A Python `set` uses a hash table internally, giving O(1) average lookup. Iterating once through the array is O(n). The naive approach of checking all pairs would be O(n²).
Time: O(n) · Space: O(n)
</details>

---

<a id="q7"></a>
### Q7 · move-zeros — Move Zeros to End 🚶

Given an array, move all zeros to the end while maintaining the relative order of non-zero elements. Do it in-place.

```
Input:  [0, 1, 0, 3, 12]
Output: [1, 3, 12, 0, 0]
```

<details>
<summary>Hint</summary>
Use a slow pointer that tracks the next position to place a non-zero element. The fast pointer scans every element.
</details>

<details>
<summary>Answer</summary>

```python
def move_zeros(nums: list) -> list:
    slow = 0   # ← position for next non-zero element
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow] = nums[fast]   # ← place non-zero at slow position
            slow += 1
    # Fill remaining positions with zeros
    while slow < len(nums):
        nums[slow] = 0
        slow += 1
    return nums

print(move_zeros([0, 1, 0, 3, 12]))   # [1, 3, 12, 0, 0]
print(move_zeros([0, 0, 1]))          # [1, 0, 0]
print(move_zeros([1, 2, 3]))          # [1, 2, 3]  — no change
```

**Why:** The **fast-slow pointer** pattern (a special case of two pointers) partitions the array in one pass. `slow` always points to where the next non-zero should land. After the loop, every position from `slow` onward is filled with zeros.
Time: O(n) · Space: O(1)
</details>

---

<a id="q8"></a>
### Q8 · remove-duplicates-sorted — Remove Duplicates from Sorted Array 📋

Given a sorted array, remove duplicates in-place and return the length of the unique portion. Elements beyond that length do not matter.

```
Input:  [1, 1, 2, 2, 3]
Output: 3  (array is [1, 2, 3, ...])
```

<details>
<summary>Hint</summary>
Use a slow pointer for the last unique position. The fast pointer scans forward; when it finds a new value, write it at slow+1.
</details>

<details>
<summary>Answer</summary>

```python
def remove_duplicates(nums: list) -> int:
    if not nums:
        return 0
    slow = 0   # ← index of last confirmed unique element
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:   # ← new unique value found
            slow += 1
            nums[slow] = nums[fast]    # ← write it into the unique region
    return slow + 1   # ← length of unique portion

nums = [1, 1, 2, 2, 3]
k = remove_duplicates(nums)
print(k)            # 3
print(nums[:k])     # [1, 2, 3]
```

**Why:** Because the array is sorted, all duplicates of a value are adjacent. The slow pointer marks the boundary of the de-duplicated prefix. Only when fast finds a genuinely new value does slow advance. This is the canonical in-place de-duplication pattern.
Time: O(n) · Space: O(1)
</details>

---

## Intermediate Questions (Q9–Q21)

---

<a id="q9"></a>
### Q9 · prefix-sum-build — Build a Prefix Sum Array 📊

Build a prefix sum array using the 1-indexed (exclusive) convention where `prefix[0] = 0` and `prefix[i] = sum of arr[0..i-1]`.

```
Input:  arr = [3, 1, 4, 1, 5, 9]
Output: prefix = [0, 3, 4, 8, 9, 14, 23]
```

<details>
<summary>Hint</summary>
The array has length n+1. prefix[0] is always 0. For each subsequent index, add the previous prefix to the current array element.
</details>

<details>
<summary>Answer</summary>

```python
def build_prefix(arr: list) -> list:
    n = len(arr)
    prefix = [0] * (n + 1)   # ← one extra slot; prefix[0] = 0 sentinel
    for i in range(n):
        prefix[i + 1] = prefix[i] + arr[i]   # ← running total
    return prefix

arr = [3, 1, 4, 1, 5, 9]
print(build_prefix(arr))   # [0, 3, 4, 8, 9, 14, 23]
```

**Why:** The sentinel zero at index 0 makes the range query formula clean and avoids special-casing when `left == 0`. This **1-indexed prefix** convention is preferred over the 0-indexed version because `sum(l, r) = prefix[r+1] - prefix[l]` works uniformly for all subarrays.
Time: O(n) to build · Space: O(n)
</details>

---

<a id="q10"></a>
### Q10 · range-sum-query — Range Sum Query ⚡

Using the prefix array built in Q9, answer range sum queries in O(1). Demonstrate with two queries.

```
arr = [3, 1, 4, 1, 5, 9, 2, 6]
query(2, 5)  -> 19   (4+1+5+9)
query(0, 3)  -> 9    (3+1+4+1)
```

<details>
<summary>Hint</summary>
With the 1-indexed prefix, sum of arr[l..r] inclusive = prefix[r+1] - prefix[l].
</details>

<details>
<summary>Answer</summary>

```python
def build_prefix(arr):
    prefix = [0] * (len(arr) + 1)
    for i in range(len(arr)):
        prefix[i + 1] = prefix[i] + arr[i]
    return prefix

def range_sum(prefix: list, l: int, r: int) -> int:
    return prefix[r + 1] - prefix[l]   # ← O(1): two array lookups and one subtraction

arr = [3, 1, 4, 1, 5, 9, 2, 6]
prefix = build_prefix(arr)

print(range_sum(prefix, 2, 5))   # 19
print(range_sum(prefix, 0, 3))   # 9
print(range_sum(prefix, 0, 7))   # 31  (entire array)
```

**Why:** `prefix[r+1]` holds the sum of everything from index 0 through r. `prefix[l]` holds the sum of everything before index l. Their difference is exactly the elements from l to r inclusive. Build once in O(n), then each query is O(1) — critical for analytics systems answering millions of range queries.
Time: O(1) per query after O(n) build · Space: O(n)
</details>

---

<a id="q11"></a>
### Q11 · subarray-sum-k — Count Subarrays with Sum K 🗂️

Given an array of integers and a value `k`, return the number of contiguous subarrays whose sum equals `k`.

```
Input: nums = [1, 1, 1], k = 2
Output: 2   ([1,1] starting at index 0, [1,1] starting at index 1)
```

<details>
<summary>Hint</summary>
Think about prefix sums. If running_sum - k was seen before at some index i, then the subarray from i+1 to current index sums to k. Use a hash map to track prefix sum frequencies.
</details>

<details>
<summary>Answer</summary>

```python
from collections import defaultdict

def subarray_sum(nums: list, k: int) -> int:
    count = 0
    running = 0
    seen = defaultdict(int)
    seen[0] = 1   # ← empty prefix: sum 0 has been seen once

    for x in nums:
        running += x
        count += seen[running - k]   # ← if (running-k) exists, subarray sums to k
        seen[running] += 1
    return count

print(subarray_sum([1, 1, 1], 2))      # 2
print(subarray_sum([1, 2, 3], 3))      # 2  ([1,2] and [3])
print(subarray_sum([-1, -1, 1], 0))   # 1
```

**Why:** Combining **prefix sums** with a **hash map** converts an O(n²) brute-force scan into O(n). The key insight: if `prefix[j] - prefix[i] == k`, then subarray `i+1..j` sums to k. Equivalently, if `prefix[j] - k` has appeared before as a prefix sum, we have found a valid subarray.
Time: O(n) · Space: O(n)
</details>

---

<a id="q12"></a>
### Q12 · max-subarray-kadane — Maximum Subarray (Kadane's) 📈

Find the contiguous subarray with the largest sum. Your solution must handle all-negative arrays correctly.

```
Input: [-2, 1, -3, 4, -1, 2, 1, -5, 4]
Output: 6   (subarray [4, -1, 2, 1])

Input: [-5, -3, -1, -9]
Output: -1  (best single element)
```

<details>
<summary>Hint</summary>
At each element, you have two choices: start a new subarray here, or extend the current one. The wrong version resets to 0, which fails for all-negative arrays. Initialize to arr[0].
</details>

<details>
<summary>Answer</summary>

```python
def max_subarray(arr: list) -> int:
    if not arr:
        return 0
    max_sum = arr[0]    # ← must initialize to arr[0], not 0
    cur_sum = arr[0]

    for x in arr[1:]:
        cur_sum = max(x, cur_sum + x)   # ← extend or restart fresh here
        max_sum = max(max_sum, cur_sum)
    return max_sum

print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))   # 6
print(max_subarray([-5, -3, -1, -9]))                    # -1
print(max_subarray([1, 2, 3, 4, 5]))                     # 15
```

**Why:** **Kadane's algorithm** makes a greedy choice at each step. `max(x, cur_sum + x)` asks: "is it better to start fresh here, or extend the streak?" Initializing to `arr[0]` (not 0) ensures the algorithm respects the constraint that at least one element must be chosen — critical for all-negative inputs.
Time: O(n) · Space: O(1)
</details>

---

<a id="q13"></a>
### Q13 · two-pointer-pair-sum — Two-Pointer Pair Sum 👆👆

Given a **sorted** array, find all unique pairs that sum to a target value.

```
Input: arr = [1, 2, 3, 4, 6], target = 6
Output: [(2, 4), (3, 3)]   → but [3,3] only if arr has two 3s
         Actually: [(2, 4)]  — since only one 3 in arr

Input: arr = [1, 2, 3, 4, 6], target = 7
Output: [(1, 6), (3, 4)]
```

<details>
<summary>Hint</summary>
Place one pointer at each end of the sorted array. If the sum is too small, move the left pointer right. If too large, move the right pointer left.
</details>

<details>
<summary>Answer</summary>

```python
def pair_sum(arr: list, target: int) -> list:
    # Precondition: arr must be sorted
    lo, hi = 0, len(arr) - 1
    result = []
    while lo < hi:
        s = arr[lo] + arr[hi]
        if s == target:
            result.append((arr[lo], arr[hi]))
            lo += 1    # ← advance both to find next pair
            hi -= 1
        elif s < target:
            lo += 1    # ← need larger sum: move left pointer right
        else:
            hi -= 1    # ← need smaller sum: move right pointer left
    return result

print(pair_sum([1, 2, 3, 4, 6], 7))    # [(1, 6), (3, 4)]
print(pair_sum([1, 2, 3, 4, 6], 6))    # [(2, 4)]
print(pair_sum([1, 1, 2, 3], 4))       # [(1, 3)]
```

**Why:** The **two-pointer** technique on a sorted array eliminates the O(n²) brute-force search. When the array is sorted, moving the left pointer right strictly increases the sum; moving the right pointer left strictly decreases it. This directed movement guarantees we check each possible pair exactly once.
Time: O(n) after sorting · Space: O(1)
</details>

---

<a id="q14"></a>
### Q14 · three-sum — Three Sum (Triplets to Zero) 🎯

Given an array, find all unique triplets that sum to zero. Return as a list of sorted triplets (no duplicates in the output).

```
Input:  [-1, 0, 1, 2, -1, -4]
Output: [[-1, -1, 2], [-1, 0, 1]]
```

<details>
<summary>Hint</summary>
Sort the array. Fix one element with an outer loop. For the remaining two elements, apply the two-pointer pattern. Skip duplicates to avoid repeating triplets.
</details>

<details>
<summary>Answer</summary>

```python
def three_sum(nums: list) -> list:
    nums.sort()   # ← enables two-pointer on the remaining pair
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:   # ← skip duplicate first element
            continue
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s == 0:
                result.append([nums[i], nums[lo], nums[hi]])
                while lo < hi and nums[lo] == nums[lo + 1]:   # ← skip dupes
                    lo += 1
                while lo < hi and nums[hi] == nums[hi - 1]:   # ← skip dupes
                    hi -= 1
                lo += 1
                hi -= 1
            elif s < 0:
                lo += 1
            else:
                hi -= 1
    return result

print(three_sum([-1, 0, 1, 2, -1, -4]))   # [[-1, -1, 2], [-1, 0, 1]]
print(three_sum([0, 0, 0]))               # [[0, 0, 0]]
```

**Why:** Sorting + two-pointer reduces three-sum from O(n³) to O(n²). The outer loop fixes one element; the inner two-pointer scan finds all valid pairs in O(n). Careful duplicate skipping ensures each unique triplet appears exactly once.
Time: O(n²) · Space: O(1) excluding output
</details>

---

<a id="q15"></a>
### Q15 · rotate-array — Rotate Array Right by K 🔄

Rotate the array to the right by `k` positions in-place using O(1) extra space.

```
Input:  arr = [1, 2, 3, 4, 5, 6, 7], k = 3
Output: [5, 6, 7, 1, 2, 3, 4]
```

<details>
<summary>Hint</summary>
The reverse trick: reverse the entire array, then reverse the first k elements, then reverse the rest. Three reverses equal one rotation.
</details>

<details>
<summary>Answer</summary>

```python
def rotate(arr: list, k: int) -> None:
    n = len(arr)
    k %= n   # ← handle k > n (rotating n times is a no-op)

    def reverse(lo, hi):
        while lo < hi:
            arr[lo], arr[hi] = arr[hi], arr[lo]
            lo += 1
            hi -= 1

    reverse(0, n - 1)   # ← reverse entire array
    reverse(0, k - 1)   # ← reverse first k elements
    reverse(k, n - 1)   # ← reverse remaining elements

arr = [1, 2, 3, 4, 5, 6, 7]
rotate(arr, 3)
print(arr)   # [5, 6, 7, 1, 2, 3, 4]

arr = [1, 2]
rotate(arr, 3)   # k=3 → k%2=1
print(arr)       # [2, 1]
```

**Why:** The **reverse trick** is elegant: reversing the whole array puts everything in the right relative zones, then reversing each zone un-reverses the within-zone order. Three passes, each O(n), but with only O(1) extra space — no temporary array needed.
Time: O(n) · Space: O(1)
</details>

---

<a id="q16"></a>
### Q16 · dutch-flag — Dutch National Flag Sort 🚩

Sort an array containing only 0s, 1s, and 2s in a single pass without using any sorting function.

```
Input:  [2, 0, 2, 1, 1, 0]
Output: [0, 0, 1, 1, 2, 2]
```

<details>
<summary>Hint</summary>
Use three pointers: low, mid, high. Maintain the invariant: everything before low is 0, everything after high is 2, between low and mid is 1.
</details>

<details>
<summary>Answer</summary>

```python
def sort_colors(nums: list) -> None:
    lo, mid, hi = 0, 0, len(nums) - 1

    while mid <= hi:
        if nums[mid] == 0:
            nums[lo], nums[mid] = nums[mid], nums[lo]   # ← push 0 to front
            lo += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1   # ← 1 is already in the correct zone
        else:          # nums[mid] == 2
            nums[mid], nums[hi] = nums[hi], nums[mid]   # ← push 2 to back
            hi -= 1    # ← do NOT increment mid: swapped value needs checking

nums = [2, 0, 2, 1, 1, 0]
sort_colors(nums)
print(nums)   # [0, 0, 1, 1, 2, 2]
```

**Why:** This is Dijkstra's **Dutch National Flag** algorithm. The three-pointer invariant partitions the array into three regions simultaneously. The subtle rule: when swapping with `hi`, do not advance `mid` because the element swapped in from the right is unknown and must be re-examined.
Time: O(n) · Space: O(1)
</details>

---

<a id="q17"></a>
### Q17 · product-except-self — Product of Array Except Self 🔢

Return an array where each element is the product of all other elements. No division allowed. O(1) extra space (excluding output).

```
Input:  [1, 2, 3, 4]
Output: [24, 12, 8, 6]
```

<details>
<summary>Hint</summary>
Build a left-product array and a right-product array separately. output[i] = left_product[i] × right_product[i]. Then optimize to O(1) extra space by computing in one output array.
</details>

<details>
<summary>Answer</summary>

```python
def product_except_self(nums: list) -> list:
    n = len(nums)
    result = [1] * n

    # Left pass: result[i] = product of all elements to the left of i
    prefix = 1
    for i in range(n):
        result[i] = prefix
        prefix *= nums[i]   # ← update prefix for next element

    # Right pass: multiply in the product of all elements to the right
    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix
        suffix *= nums[i]   # ← update suffix for next element

    return result

print(product_except_self([1, 2, 3, 4]))   # [24, 12, 8, 6]
print(product_except_self([2, 3, 4, 5]))   # [60, 40, 30, 24]
```

**Why:** Two prefix-product passes replace the need for division. The left pass fills `result[i]` with the product of everything to the left. The right pass multiplies in everything to the right. This is the **prefix/suffix product** pattern — a generalization of prefix sums.
Time: O(n) · Space: O(1) extra (output array not counted)
</details>

---

<a id="q18"></a>
### Q18 · sliding-window-max-avg — Sliding Window Maximum Average 🪟

Find the maximum average of any contiguous subarray of length `k`.

```
Input: nums = [1, 12, -5, -6, 50, 3], k = 4
Output: 12.75   (subarray [12, -5, -6, 50] / 4 = 51/4 = 12.75)
```

<details>
<summary>Hint</summary>
Compute the sum of the first window, then slide: add the next element and subtract the element leaving the window. Avoid recomputing from scratch each time.
</details>

<details>
<summary>Answer</summary>

```python
def max_average(nums: list, k: int) -> float:
    # Initialize first window
    window_sum = sum(nums[:k])   # ← O(k) initial sum
    max_sum = window_sum

    # Slide the window one element at a time
    for i in range(k, len(nums)):
        window_sum += nums[i]       # ← add incoming element
        window_sum -= nums[i - k]   # ← remove outgoing element
        max_sum = max(max_sum, window_sum)

    return max_sum / k

print(max_average([1, 12, -5, -6, 50, 3], 4))   # 12.75
print(max_average([5, 5, 5, 5, 5], 2))          # 5.0
```

**Why:** The **sliding window** pattern avoids O(n*k) recomputation by maintaining a running sum. When the window slides by one position, only two operations change it: one addition and one subtraction. This is the fixed-size sliding window variant — the window size k stays constant throughout.
Time: O(n) · Space: O(1)
</details>

---

<a id="q19"></a>
### Q19 · two-pointer-without-sort — Why Two-Pointer Requires Sorting 🚫

Demonstrate with a concrete example why applying two-pointer to an unsorted array produces a wrong answer. Then fix it.

```
arr = [4, 5, 3, 6], target = 9
Expected: finds pairs (3,6) and (4,5)
```

<details>
<summary>Hint</summary>
Trace through the unsorted array with two pointers manually. Show which valid pair gets missed.
</details>

<details>
<summary>Answer</summary>

```python
def two_pointer_wrong(arr, target):
    """Applies two-pointer to unsorted array — INCORRECT."""
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        s = arr[lo] + arr[hi]
        if s == target:
            return (arr[lo], arr[hi])
        elif s < target:
            lo += 1
        else:
            hi -= 1
    return None

def two_pointer_correct(arr, target):
    """Sort first, then apply two-pointer — CORRECT."""
    arr_sorted = sorted(arr)   # ← O(n log n)
    lo, hi = 0, len(arr_sorted) - 1
    while lo < hi:
        s = arr_sorted[lo] + arr_sorted[hi]
        if s == target:
            return (arr_sorted[lo], arr_sorted[hi])
        elif s < target:
            lo += 1
        else:
            hi -= 1
    return None

arr = [4, 5, 3, 6]
# Trace on unsorted [4, 5, 3, 6], target=9:
# lo=0,hi=3: 4+6=10 > 9 → hi-- (now hi=2)
# lo=0,hi=2: 4+3=7  < 9 → lo++ (now lo=1)
# lo=1,hi=2: 5+3=8  < 9 → lo++ (now lo=2)
# lo=2,hi=2: lo not < hi → exit. Returns None!
# MISSED the pair (3,6) and (4,5)

print(two_pointer_wrong(arr, 9))    # None — WRONG
print(two_pointer_correct(arr, 9))  # (3, 6) — correct
```

**Why:** Two-pointer logic assumes "move left right to get a larger sum, move right left to get a smaller sum." This reasoning is only valid when the array is sorted. In an unsorted array, moving left to a higher index may actually decrease the value, and the algorithm misses valid pairs.
Time (wrong): O(n) but incorrect · Time (correct): O(n log n) + O(n) · Space: O(1)
</details>

---

<a id="q20"></a>
### Q20 · shallow-vs-deep-copy — Shallow vs Deep Copy Trap 📋

Demonstrate the shallow copy trap on a 2D grid. Show the bug and three ways to fix it.

```
grid = [[1, 2], [3, 4]]
Modify the copy. The original should remain unchanged.
```

<details>
<summary>Hint</summary>
`list.copy()` creates a new outer list but the inner lists are still shared references. Any mutation of an inner list affects both the copy and the original.
</details>

<details>
<summary>Answer</summary>

```python
import copy

grid = [[1, 2], [3, 4]]

# WRONG: shallow copy shares inner lists
shallow = grid.copy()
shallow[0][0] = 99
print(grid)    # [[99, 2], [3, 4]] ← original corrupted!

# Fix 1: copy.deepcopy (recursive copy of all nested objects)
grid = [[1, 2], [3, 4]]
deep = copy.deepcopy(grid)
deep[0][0] = 99
print(grid)    # [[1, 2], [3, 4]] ← original unchanged

# Fix 2: list comprehension (for 2D only — one level deep)
grid = [[1, 2], [3, 4]]
comp = [row[:] for row in grid]   # ← copies each inner list individually
comp[0][0] = 99
print(grid)    # [[1, 2], [3, 4]] ← unchanged

# Fix 3: for NxM grid initialization (avoids the problem entirely)
rows, cols = 3, 4
fresh_grid = [[0] * cols for _ in range(rows)]   # ← each row is independent
```

**Why:** Python's `list.copy()` creates a new container but copies the references to inner objects — not the inner objects themselves. Since the inner lists are mutable and shared, mutating them through either handle affects both. `deepcopy` recursively creates new objects at every level. The comprehension fix `[row[:] for row in grid]` achieves the same for exactly one level of nesting.
Time: O(n*m) for deepcopy/comprehension · Space: O(n*m)
</details>

---

<a id="q21"></a>
### Q21 · numpy-vs-list — NumPy vs Python List Tradeoffs 🔬

Answer the following:
1. Why is `np.array([1,2,3])` roughly 9x more memory-efficient than `[1, 2, 3]` for integers?
2. When should you still use a Python list instead of NumPy?

Then write code to verify the memory difference.

<details>
<summary>Hint</summary>
Python list elements are Python objects (~28 bytes each) with a pointer (~8 bytes) in the list. NumPy stores raw C integers (4 or 8 bytes each) contiguously with no object overhead.
</details>

<details>
<summary>Answer</summary>

```python
import sys
import numpy as np

# Python list: pointer array + per-element Python object overhead
py_list = [1, 2, 3, 4, 5]
list_mem = sys.getsizeof(py_list) + sum(sys.getsizeof(x) for x in py_list)
print(f"Python list memory: ~{list_mem} bytes")   # ~340 bytes for 5 ints

# NumPy int32 array: contiguous raw C integers, no per-element overhead
np_arr = np.array([1, 2, 3, 4, 5], dtype=np.int32)
print(f"NumPy array memory: {np_arr.nbytes} bytes")   # 20 bytes (5 × 4)

# Performance comparison
import time
n = 1_000_000
py = list(range(n))
np_a = np.arange(n, dtype=np.int32)

start = time.perf_counter()
_ = [x * 2 for x in py]
print(f"List multiply: {time.perf_counter()-start:.3f}s")

start = time.perf_counter()
_ = np_a * 2   # ← single vectorized C-level loop
print(f"NumPy multiply: {time.perf_counter()-start:.4f}s")
```

**Why:** Python list stores pointers (8 bytes) to **Python int objects** (~28 bytes each). NumPy stores raw C integers contiguously — 4 bytes for int32, no object overhead. Vectorized operations run in compiled C/Fortran, bypassing Python's interpreter loop entirely. Use a Python list when elements are heterogeneous, when you need frequent insertions/deletions, or when the dataset is small enough that overhead is irrelevant.
Time: O(n) for both, but NumPy's constant factor is ~50-100x smaller · Space: O(n) (NumPy ~9x less)
</details>

---

## Advanced Questions (Q22–Q25)

---

<a id="q22"></a>
### Q22 · circular-buffer — Implement a Circular Buffer 🔁

Implement a fixed-size circular buffer (ring buffer) with O(1) write and read. Support detecting full and empty states.

```
buffer = CircularBuffer(3)
buffer.write(1)  → True
buffer.write(2)  → True
buffer.write(3)  → True
buffer.write(4)  → False  (full)
buffer.read()    → 1
buffer.write(4)  → True   (space freed)
```

<details>
<summary>Hint</summary>
Use two pointers: read_pos and write_pos, both advancing modulo capacity. Track the current size to distinguish full from empty (both pointers are equal in both states without a size counter).
</details>

<details>
<summary>Answer</summary>

```python
class CircularBuffer:
    """Fixed-size ring buffer using a single array. O(1) read and write."""

    def __init__(self, capacity: int):
        self.buffer = [None] * capacity
        self.capacity = capacity
        self.read_pos = 0
        self.write_pos = 0
        self.size = 0

    def write(self, value) -> bool:
        if self.size == self.capacity:
            return False   # ← buffer full: would overwrite unread data
        self.buffer[self.write_pos] = value
        self.write_pos = (self.write_pos + 1) % self.capacity   # ← wrap around
        self.size += 1
        return True

    def read(self):
        if self.size == 0:
            return None   # ← buffer empty
        value = self.buffer[self.read_pos]
        self.read_pos = (self.read_pos + 1) % self.capacity   # ← wrap around
        self.size -= 1
        return value

    def __len__(self):
        return self.size

buf = CircularBuffer(3)
print(buf.write(1), buf.write(2), buf.write(3))   # True True True
print(buf.write(4))    # False — full
print(buf.read())      # 1
print(buf.write(4))    # True — space freed
print(buf.read(), buf.read(), buf.read())          # 2 3 4
```

**Why:** The **modulo index** (`pos = (pos + 1) % capacity`) wraps the pointer back to 0 when it reaches the end, turning a linear array into a logical ring. This is used in audio drivers, network socket buffers, and the Linux kernel's `kfifo` because it guarantees O(1) operations with zero dynamic memory allocation — critical in real-time systems.
Time: O(1) per read/write · Space: O(capacity)
</details>

---

<a id="q23"></a>
### Q23 · merge-intervals — Merge Overlapping Intervals 📅

Given a list of intervals, merge all overlapping intervals.

```
Input:  [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]

Input:  [[1,4],[4,5]]
Output: [[1,5]]   (touching intervals merge)
```

<details>
<summary>Hint</summary>
Sort by start time. Then iterate: if the current interval's start is within the last merged interval, extend the end. Otherwise, start a new merged interval.
</details>

<details>
<summary>Answer</summary>

```python
def merge_intervals(intervals: list) -> list:
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])   # ← sort by start time O(n log n)
    merged = [intervals[0]]

    for start, end in intervals[1:]:
        last_end = merged[-1][1]
        if start <= last_end:
            merged[-1][1] = max(last_end, end)   # ← extend the last interval
        else:
            merged.append([start, end])   # ← no overlap: start new interval
    return merged

print(merge_intervals([[1,3],[2,6],[8,10],[15,18]]))   # [[1,6],[8,10],[15,18]]
print(merge_intervals([[1,4],[4,5]]))                  # [[1,5]]
print(merge_intervals([[1,4],[0,4]]))                  # [[0,4]]
print(merge_intervals([[1,4],[2,3]]))                  # [[1,4]]  (contained)
```

**Why:** Sorting by start time ensures all overlapping intervals are adjacent. The greedy check `start <= last_end` captures both overlap and touching. When intervals are nested (one fully inside another), `max(last_end, end)` correctly retains the wider boundary. This is the standard O(n log n) merge-intervals pattern seen in calendar and scheduling problems.
Time: O(n log n) for sort + O(n) for scan · Space: O(n) for output
</details>

---

<a id="q24"></a>
### Q24 · trapping-rain-water — Trapping Rain Water 🌧️

Given an array where each element represents the height of a bar, compute how much rainwater can be trapped between the bars.

```
Input:  [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
Output: 6

Input:  [4, 2, 0, 3, 2, 5]
Output: 9
```

<details>
<summary>Hint</summary>
Water above position i equals min(max_left[i], max_right[i]) - height[i]. Start with a prefix-max and suffix-max approach, then optimize with two pointers.
</details>

<details>
<summary>Answer</summary>

```python
def trap(height: list) -> int:
    """Two-pointer solution — O(n) time, O(1) space."""
    if not height:
        return 0
    lo, hi = 0, len(height) - 1
    max_left = max_right = 0
    water = 0

    while lo < hi:
        if height[lo] <= height[hi]:
            if height[lo] >= max_left:
                max_left = height[lo]   # ← new max on left side
            else:
                water += max_left - height[lo]   # ← water trapped here
            lo += 1
        else:
            if height[hi] >= max_right:
                max_right = height[hi]   # ← new max on right side
            else:
                water += max_right - height[hi]  # ← water trapped here
            hi -= 1
    return water

print(trap([0,1,0,2,1,0,1,3,2,1,2,1]))   # 6
print(trap([4,2,0,3,2,5]))               # 9
print(trap([3,0,3]))                     # 3
```

**Why:** The key insight is that water at position i is bounded by `min(max_left, max_right) - height[i]`. The two-pointer approach exploits this: when `height[lo] <= height[hi]`, the water at `lo` is determined solely by `max_left` (we know there is a taller bar on the right). This avoids building two prefix arrays, reducing space to O(1). This problem elegantly combines two-pointer + prefix-max reasoning.
Time: O(n) · Space: O(1)
</details>

---

<a id="q25"></a>
### Q25 · subarray-with-target-sum — Find Subarray with Exact Sum (HashMap + Prefix) 🗺️

Given an integer array (may contain negatives) and a target sum `k`, return the start and end indices of the first subarray with sum equal to `k`. Return `(-1, -1)` if none exists.

```
Input: nums = [1, -1, 5, -2, 3], k = 3
Output: (0, 3)   (subarray [1, -1, 5, -2] sums to 3)

Input: nums = [-2, -1, 2, 1], k = 1
Output: (2, 3)   ([2, 1] doesn't work... let me trace: cumsum at 3 = 0, at 2 = 2, at 4 = 0. Actually: prefix={0:−1, −2:0, −3:1, −1:2}, at i=3 prefix=0, 0−1=−1 → seen at i=2. So (2,3).)
Simpler: nums = [1, 2, 3, 4, 5], k = 9
Output: (1, 3)   ([2, 3, 4] sums to 9)
```

<details>
<summary>Hint</summary>
Use a running prefix sum and a hash map `{prefix_sum: index}`. When you see `running - k` already in the map, the subarray from map[running-k]+1 to current index sums to k.
</details>

<details>
<summary>Answer</summary>

```python
def find_subarray(nums: list, k: int):
    seen = {0: -1}   # ← prefix_sum → index; seed with 0 at "before start"
    running = 0

    for i, x in enumerate(nums):
        running += x
        if running - k in seen:           # ← complement found
            start = seen[running - k] + 1  # ← subarray starts one after stored index
            return (start, i)
        if running not in seen:           # ← only store first occurrence
            seen[running] = i
    return (-1, -1)

print(find_subarray([1, 2, 3, 4, 5], 9))     # (1, 3) → [2,3,4]
print(find_subarray([1, -1, 5, -2, 3], 3))   # (0, 3) → [1,-1,5,-2]
print(find_subarray([1, 2, 3], 10))          # (-1, -1)
print(find_subarray([3, 4, 7, 2, -3, 1], 7)) # (0, 1) → [3,4]
```

**Why:** This combines **prefix sums** with a **hash map** to find the exact subarray in O(n). When `running - k` is in the map, it means a prefix ending at some earlier index `j` equals `running - k`, so `nums[j+1..i]` sums to `k`. Storing only the first occurrence of each prefix sum ensures we find the leftmost (earliest) matching subarray. Critically, this works for arrays with negative numbers — sliding window alone cannot handle negatives.
Time: O(n) · Space: O(n)
</details>

---

## Navigation

**[Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md) · [Local Practice](./practice_local.py)
