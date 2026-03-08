# Arrays — Cheatsheet

## Array Operations Complexity

```
+---------------------------+----------+----------+-----------------------------+
| Operation                 | Time     | Space    | Note                        |
+---------------------------+----------+----------+-----------------------------+
| Access by index arr[i]    | O(1)     | O(1)     |                             |
| Search (unsorted)         | O(n)     | O(1)     | linear scan                 |
| Search (sorted)           | O(log n) | O(1)     | binary search               |
| Append to end             | O(1)*    | O(1)*    | amortized                   |
| Insert at index i         | O(n)     | O(1)     | shifts n-i elements         |
| Delete at index i         | O(n)     | O(1)     | shifts n-i elements         |
| Pop from end              | O(1)     | O(1)     |                             |
| Pop from index i          | O(n)     | O(1)     |                             |
| Slice arr[i:j]            | O(k)     | O(k)     | k=j-i, CREATES NEW LIST     |
| Reverse                   | O(n)     | O(1)     | in-place                    |
| Sort                      | O(n log n)| O(n)   | TimSort                     |
| Min / Max                 | O(n)     | O(1)     |                             |
| Sum                       | O(n)     | O(1)     |                             |
+---------------------------+----------+----------+-----------------------------+
```

---

## Python List Quick Reference

```python
arr = [3, 1, 4, 1, 5]

arr.append(9)          # O(1)* — add to end
arr.pop()              # O(1)  — remove from end, returns element
arr.pop(0)             # O(n)  — SLOW, use deque for frequent front pops
arr.insert(2, 99)      # O(n)  — insert at index
arr.remove(1)          # O(n)  — removes FIRST occurrence
arr.index(4)           # O(n)  — returns first index of value
arr.count(1)           # O(n)  — count occurrences
arr.reverse()          # O(n)  — in-place
arr.sort()             # O(n log n) — in-place
sorted(arr)            # O(n log n) — returns new list
arr[::-1]              # O(n)  — reversed COPY
arr[1:4]               # O(k)  — slice COPY, k=3
len(arr)               # O(1)
5 in arr               # O(n)  — convert to set for O(1)

# Initialization patterns
zeros  = [0] * n                   # O(n)  — all same value
grid   = [[0] * m for _ in range(n)]  # O(n*m) — 2D grid (CORRECT way)
# WRONG: [[0]*m]*n — all rows are same object!
```

---

## Pattern 1 — Prefix Sum

```python
# Use: range sum queries in O(1) after O(n) preprocessing
# Use: subarray sum problems

def build_prefix(arr):
    n = len(arr)
    prefix = [0] * (n + 1)          # prefix[0] = 0 (sentinel)
    for i in range(n):
        prefix[i + 1] = prefix[i] + arr[i]
    return prefix

# Sum of arr[l..r] inclusive:
#   prefix[r+1] - prefix[l]         O(1) query

# Example: count subarrays with sum == k
from collections import defaultdict
def subarray_sum_k(arr, k):
    count = 0
    running = 0
    seen = defaultdict(int)
    seen[0] = 1                     # empty prefix
    for x in arr:
        running += x
        count += seen[running - k]  # if (running - k) seen before, valid subarray
        seen[running] += 1
    return count
```

---

## Pattern 2 — Kadane's Algorithm (Max Subarray)

```python
# Use: maximum sum contiguous subarray — O(n) time, O(1) space

def max_subarray(arr):
    max_sum = arr[0]
    cur_sum = arr[0]
    for x in arr[1:]:
        cur_sum = max(x, cur_sum + x)   # extend or restart
        max_sum = max(max_sum, cur_sum)
    return max_sum

# Variant: track indices
def max_subarray_indices(arr):
    max_sum = arr[0]
    cur_sum = arr[0]
    start = end = best_start = 0
    for i in range(1, len(arr)):
        if arr[i] > cur_sum + arr[i]:
            cur_sum = arr[i]
            start = i
        else:
            cur_sum += arr[i]
        if cur_sum > max_sum:
            max_sum = cur_sum
            best_start = start
            end = i
    return max_sum, best_start, end
```

---

## Pattern 3 — Dutch National Flag (3-Way Partition)

```python
# Use: sort array of 0s, 1s, 2s in-place — O(n) one-pass

def dutch_flag(arr):
    lo, mid, hi = 0, 0, len(arr) - 1
    while mid <= hi:
        if arr[mid] == 0:
            arr[lo], arr[mid] = arr[mid], arr[lo]
            lo += 1
            mid += 1
        elif arr[mid] == 1:
            mid += 1
        else:                               # arr[mid] == 2
            arr[mid], arr[hi] = arr[hi], arr[mid]
            hi -= 1                         # do NOT increment mid here
    return arr

# Invariant:
#   arr[0..lo-1]  = 0s
#   arr[lo..mid-1]= 1s
#   arr[mid..hi]  = unseen
#   arr[hi+1..]   = 2s
```

---

## Pattern 4 — Rotate Array

```python
# Rotate right by k positions — O(n) time, O(1) space

def rotate(arr, k):
    n = len(arr)
    k %= n                  # handle k > n
    arr.reverse()           # reverse whole
    arr[:k] = arr[:k][::-1] # reverse first k
    arr[k:] = arr[k:][::-1] # reverse rest

# Alternative: slice trick (O(n) space)
def rotate_slice(arr, k):
    n = len(arr)
    k %= n
    return arr[-k:] + arr[:-k]
```

---

## Pattern 5 — Two Pointers on Sorted Array

```python
# Pair sum == target in sorted array — O(n)

def two_sum_sorted(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        s = arr[lo] + arr[hi]
        if s == target:
            return (lo, hi)
        elif s < target:
            lo += 1         # need larger sum
        else:
            hi -= 1         # need smaller sum
    return None

# Remove duplicates from sorted array in-place
def remove_dupes(arr):
    if not arr: return 0
    slow = 0
    for fast in range(1, len(arr)):
        if arr[fast] != arr[slow]:
            slow += 1
            arr[slow] = arr[fast]
    return slow + 1         # length of deduplicated portion
```

---

## Common Interview Patterns at a Glance

```
+-------------------------------+-------------------------------------------------+
| Problem type                  | Pattern to use                                  |
+-------------------------------+-------------------------------------------------+
| Subarray sum = k              | Prefix sum + hash map                           |
| Max/min subarray sum          | Kadane's algorithm                              |
| Two numbers sum to target     | Two pointers (sorted) or hash map               |
| Triplet sum to zero           | Sort + two pointers                             |
| Find duplicate                | Floyd's cycle (index as pointer)                |
| Rotate / shift                | Reverse trick or deque rotation                 |
| Sort 0s, 1s, 2s               | Dutch National Flag                             |
| Product except self           | Left pass + right pass prefix products          |
| Merge intervals               | Sort by start, then greedy merge                |
| Next permutation              | Find rightmost ascent, swap, reverse suffix     |
| Sliding window max            | Monotonic deque                                 |
+-------------------------------+-------------------------------------------------+
```

---

## Python Gotchas

```
1. Slice creates a copy:
   sub = arr[i:j]          # O(j-i) time AND space
   Modifying sub does NOT modify arr

2. Mutable default in 2D array:
   WRONG:  grid = [[0]*m]*n    # all rows point to SAME list
   RIGHT:  grid = [[0]*m for _ in range(n)]

3. list.pop(0) is O(n):
   Use collections.deque for O(1) popleft()

4. 'x in list' is O(n):
   Convert to set first if checking membership repeatedly

5. Negative indexing:
   arr[-1]   = last element
   arr[-2]   = second to last
   arr[:-1]  = all except last (COPY)

6. Integer overflow — Python has arbitrary precision ints, no overflow concern

7. sorted() vs .sort():
   sorted() — returns NEW list, works on any iterable
   .sort()  — in-place, only on lists, slightly faster
```

---

## When To Use Arrays

```
USE arrays when:
  - You need O(1) random access by index
  - Data is fixed-size or append-only
  - Cache locality matters (arrays are contiguous in memory)
  - You need to sort, binary search, or use two pointers

AVOID arrays when:
  - Frequent insertions/deletions at arbitrary positions (use linked list)
  - Frequent front-of-list operations (use deque)
  - Need O(1) lookup by key (use dict/hash map)
```
