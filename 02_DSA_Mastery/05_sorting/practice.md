# Sorting — Practice Questions

25 questions covering all sorting algorithms, stability, Python built-ins, and classic interview problems.

---

## Quick Index

| # | Topic | Level |
|---|-------|-------|
| [Q1](#q1) | Implement bubble sort | Basic |
| [Q2](#q2) | Implement selection sort | Basic |
| [Q3](#q3) | Implement insertion sort | Basic |
| [Q4](#q4) | `.sort()` vs `sorted()` — which to use | Basic |
| [Q5](#q5) | Sort list of tuples by second element | Basic |
| [Q6](#q6) | Sort strings case-insensitively | Basic |
| [Q7](#q7) | Implement counting sort | Basic |
| [Q8](#q8) | What is sort stability and why does it matter | Basic |
| [Q9](#q9) | Implement merge sort | Intermediate |
| [Q10](#q10) | Implement quicksort with random pivot | Intermediate |
| [Q11](#q11) | Implement heapsort using heapq | Intermediate |
| [Q12](#q12) | Sort a nearly-sorted array efficiently | Intermediate |
| [Q13](#q13) | Sort array elements by frequency | Intermediate |
| [Q14](#q14) | Find the k-th largest element | Intermediate |
| [Q15](#q15) | Custom comparator — Largest Number | Intermediate |
| [Q16](#q16) | Demonstrate stability in multi-key sort | Intermediate |
| [Q17](#q17) | Implement radix sort | Intermediate |
| [Q18](#q18) | Merge two sorted arrays in O(n) | Intermediate |
| [Q19](#q19) | Sort a dictionary by value | Intermediate |
| [Q20](#q20) | Explain and prove Timsort O(n) best case | Intermediate |
| [Q21](#q21) | Sort Colors — Dutch National Flag | Advanced |
| [Q22](#q22) | Meeting Rooms — sort by start time | Advanced |
| [Q23](#q23) | Merge Intervals | Advanced |
| [Q24](#q24) | External merge sort with a min-heap | Advanced |
| [Q25](#q25) | Choose the right sort — 5 scenarios | Advanced |

---

## Basic Questions

---

<a id="q1"></a>
### Q1 Implement Bubble Sort

**Problem:** Implement bubble sort on a list of integers. Include the early-exit optimization so the algorithm stops as soon as a pass completes with no swaps.

**Example:**
```
Input:  [5, 3, 8, 4, 1]
Output: [1, 3, 4, 5, 8]
```

<details>
<summary>Hint</summary>

On each pass, walk adjacent pairs and swap when left > right. Track whether any swap occurred. If a full pass produces zero swaps, the array is already sorted — stop early.

</details>

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False                         # ← early-exit flag
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:                         # ← no swaps = already sorted
            break
    return arr

# Tests
assert bubble_sort([5, 3, 8, 4, 1]) == [1, 3, 4, 5, 8]
assert bubble_sort([1, 2, 3])       == [1, 2, 3]   # already sorted — exits after 1 pass
assert bubble_sort([])              == []
assert bubble_sort([1])             == [1]
```

**Why:** Each pass "bubbles" the largest unsorted element to its correct position. Without the early-exit flag the algorithm always runs O(n²) passes even on a sorted array; with it, a sorted array costs only O(n) — one pass with no swaps.

**Time:** O(n²) worst/average, O(n) best (already sorted). **Space:** O(1).

---

<a id="q2"></a>
### Q2 Implement Selection Sort

**Problem:** Implement selection sort. On each iteration, find the minimum element in the unsorted portion and swap it into the next sorted position.

**Example:**
```
Input:  [64, 25, 12, 22, 11]
Output: [11, 12, 22, 25, 64]
```

<details>
<summary>Hint</summary>

Use two loops: outer loop tracks the boundary of the sorted portion, inner loop finds the index of the minimum in the remaining unsorted portion. Swap the minimum into position `i`.

</details>

```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i                             # ← assume current position is min
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j                     # ← found a smaller element
        arr[i], arr[min_idx] = arr[min_idx], arr[i]  # ← place min at position i
    return arr

# Tests
assert selection_sort([64, 25, 12, 22, 11]) == [11, 12, 22, 25, 64]
assert selection_sort([3, 2, 1])            == [1, 2, 3]
assert selection_sort([1])                  == [1]
```

**Why:** Selection sort makes exactly n swaps total (one per outer iteration), which makes it useful when swapping is expensive. However, it always scans the full unsorted portion even if the array is already sorted — no early exit possible.

**Time:** O(n²) always. **Space:** O(1).

---

<a id="q3"></a>
### Q3 Implement Insertion Sort

**Problem:** Implement insertion sort. Build a sorted left portion one element at a time by shifting larger elements right to make room for the current element.

**Example:**
```
Input:  [5, 3, 8, 4, 2]
Output: [2, 3, 4, 5, 8]
```

<details>
<summary>Hint</summary>

Keep a "key" (the element being inserted). Walk backwards through the sorted portion, shifting each element one position right while it is greater than `key`. Insert `key` where you stopped.

</details>

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]                            # ← element to insert
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]                 # ← shift right
            j -= 1
        arr[j + 1] = key                        # ← insert
    return arr

# Tests
assert insertion_sort([5, 3, 8, 4, 2]) == [2, 3, 4, 5, 8]
assert insertion_sort([1, 2, 3, 4])    == [1, 2, 3, 4]   # O(n) — no shifts
assert insertion_sort([4, 3, 2, 1])    == [1, 2, 3, 4]   # O(n²) — max shifts
```

**Why:** When the array is nearly sorted, `key` slides into place after very few comparisons — this gives O(n) best-case performance. This is why Timsort uses insertion sort for small runs: it is extremely cache-friendly and avoids the overhead of recursion.

**Time:** O(n²) worst/average, O(n) best (nearly sorted). **Space:** O(1).

---

<a id="q4"></a>
### Q4 `.sort()` vs `sorted()`

**Problem:** You have a list `nums = [3, 1, 4, 1, 5]`. Write two versions: one that sorts the list in-place and one that returns a new sorted list without modifying the original. Then explain the key API difference.

<details>
<summary>Hint</summary>

`list.sort()` mutates the list and returns `None`. `sorted()` accepts any iterable, leaves it unchanged, and returns a new list. The classic trap is writing `nums = nums.sort()` which sets `nums` to `None`.

</details>

```python
nums = [3, 1, 4, 1, 5]

# In-place — modifies nums, returns None
nums.sort()
print(nums)           # [1, 1, 3, 4, 5]

# New sorted list — original unchanged
original = [3, 1, 4, 1, 5]
result = sorted(original)
print(result)         # [1, 1, 3, 4, 5]
print(original)       # [3, 1, 4, 1, 5]  ← untouched

# Common trap:
bad = [3, 1, 2]
bad = bad.sort()      # bad is now None!
print(bad)            # None  ← BUG
```

**Why:** `sorted()` works on any iterable (sets, generators, tuples), while `.sort()` is a list-only method. Use `.sort()` when you have a list and do not need the original; use `sorted()` when you need a copy or are working with a non-list iterable.

**Time:** O(n log n) both. **Space:** O(n) for `sorted()`, O(1) extra for `.sort()`.

---

<a id="q5"></a>
### Q5 Sort by Custom Key

**Problem:** Given a list of `(name, score)` tuples, sort by score descending. When scores tie, sort by name ascending.

**Example:**
```
Input:  [("Alice", 90), ("Bob", 85), ("Carol", 90), ("Dave", 85)]
Output: [("Alice", 90), ("Carol", 90), ("Bob", 85), ("Dave", 85)]
```

<details>
<summary>Hint</summary>

Use a tuple as the `key`. To sort a field descending, negate it: `key=lambda x: (-x[1], x[0])`. The tuple is compared lexicographically — the first element decides order unless it ties, then the second decides.

</details>

```python
data = [("Alice", 90), ("Bob", 85), ("Carol", 90), ("Dave", 85)]

result = sorted(data, key=lambda x: (-x[1], x[0]))  # ← (-score, name)

print(result)
# [('Alice', 90), ('Carol', 90), ('Bob', 85), ('Dave', 85)]

assert result[0] == ("Alice", 90)
assert result[1] == ("Carol", 90)
assert result[2] == ("Bob", 85)
assert result[3] == ("Dave", 85)
```

**Why:** The negation trick `-x[1]` flips a numeric field from ascending to descending without needing `cmp_to_key`. Within a tie (same `-score`), `x[0]` (name) is compared alphabetically ascending. This is the idiomatic multi-key sort pattern in Python.

**Time:** O(n log n). **Space:** O(n).

---

<a id="q6"></a>
### Q6 Sort Strings Case-Insensitively

**Problem:** Sort a list of strings alphabetically, ignoring case differences. `"Banana"` and `"banana"` should sort as if they are the same letter.

**Example:**
```
Input:  ["Banana", "apple", "Cherry", "date"]
Output: ["apple", "Banana", "Cherry", "date"]
```

<details>
<summary>Hint</summary>

Use `key=str.lower` (or `key=str.casefold` for Unicode). The `key` function is used only for comparison — the original strings are returned unchanged.

</details>

```python
words = ["Banana", "apple", "Cherry", "date"]
result = sorted(words, key=str.lower)     # ← key=str.lower, not str.lower()

print(result)
# ['apple', 'Banana', 'Cherry', 'date']

# str.casefold is more aggressive for Unicode (handles ß → ss etc.)
result2 = sorted(words, key=str.casefold)
assert result == result2   # same result for ASCII
```

**Why:** The `key` function is called once per element before any comparisons occur. Using `str.lower` as the key means Python compares lowercase versions but stores and returns the originals — this is the **decorate-sort-undecorate** (Schwartzian transform) pattern built into Python's sort API.

**Time:** O(n log n). **Space:** O(n) for the key values.

---

<a id="q7"></a>
### Q7 Counting Sort

**Problem:** Implement counting sort for a list of non-negative integers where all values are in the range `[0, max_val]`.

**Example:**
```
Input:  [4, 2, 2, 8, 3, 3, 1],  max_val=8
Output: [1, 2, 2, 3, 3, 4, 8]
```

<details>
<summary>Hint</summary>

Allocate a `count` array of size `max_val + 1`. Increment `count[x]` for each element. Reconstruct the output by iterating through `count` and appending each index `freq` times. No comparisons needed.

</details>

```python
def counting_sort(arr, max_val):
    if not arr:
        return arr
    count = [0] * (max_val + 1)             # ← frequency table
    for x in arr:
        count[x] += 1
    result = []
    for val, freq in enumerate(count):
        result.extend([val] * freq)          # ← reconstruct
    return result

# Tests
assert counting_sort([4, 2, 2, 8, 3, 3, 1], 8) == [1, 2, 2, 3, 3, 4, 8]
assert counting_sort([0, 0, 1], 1)              == [0, 0, 1]
assert counting_sort([], 5)                     == []
```

**Why:** Counting sort sidesteps the O(n log n) comparison lower bound by not comparing elements at all. It exploits knowledge of the value range. The trade-off: it requires O(k) space where k is the range. If k >> n (e.g., sorting 100 numbers in range 0–1,000,000), the count array wastes memory.

**Time:** O(n + k). **Space:** O(k).

---

<a id="q8"></a>
### Q8 Stability Definition

**Problem:** Given the list `students = [("Alice", 90), ("Bob", 85), ("Carol", 90), ("Dave", 85)]`, demonstrate with code what **sort stability** means. Show that Python's sort preserves Alice before Carol (both score 90) and Bob before Dave (both score 85).

<details>
<summary>Hint</summary>

A stable sort preserves the original relative order of elements that compare as equal. Sort only by score (`key=lambda x: x[1]`). If the sort is stable, Alice (index 0) stays before Carol (index 2) because they have the same score and Alice appeared first.

</details>

```python
students = [("Alice", 90), ("Bob", 85), ("Carol", 90), ("Dave", 85)]

# Sort only by score — Python's Timsort is stable
result = sorted(students, key=lambda s: s[1], reverse=True)

print(result)
# [('Alice', 90), ('Carol', 90), ('Bob', 85), ('Dave', 85)]

assert result[0][0] == "Alice"   # ← Alice before Carol (same score, original order kept)
assert result[1][0] == "Carol"
assert result[2][0] == "Bob"     # ← Bob before Dave (same score, original order kept)
assert result[3][0] == "Dave"
```

**Why:** Stability matters whenever you sort by one field and rely on a previously established order for tie-breaking. A common pattern: sort by name first, then sort by department using a stable sort — employees within the same department will then be alphabetically ordered. Unstable sorts destroy that secondary ordering.

**Time:** O(n log n). **Space:** O(n).

---

## Intermediate Questions

---

<a id="q9"></a>
### Q9 Implement Merge Sort

**Problem:** Implement merge sort using divide-and-conquer. The function should return a new sorted list. Include the `merge` helper that merges two sorted lists in O(n).

**Example:**
```
Input:  [8, 3, 5, 1, 4]
Output: [1, 3, 4, 5, 8]
```

<details>
<summary>Hint</summary>

Base case: arrays of length 0 or 1 are already sorted. Recursive case: split at `mid = len(arr) // 2`, recursively sort both halves, then merge. In `merge`, use two pointers advancing through each half; always take the smaller element.

</details>

```python
def merge_sort(arr):
    if len(arr) <= 1:                           # ← base case
        return arr
    mid = len(arr) // 2
    left  = merge_sort(arr[:mid])              # ← sort left half
    right = merge_sort(arr[mid:])              # ← sort right half
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:                # ← <= preserves stability
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])                    # ← append remaining
    result.extend(right[j:])
    return result

# Tests
assert merge_sort([8, 3, 5, 1, 4])   == [1, 3, 4, 5, 8]
assert merge_sort([])                 == []
assert merge_sort([1])                == [1]
assert merge_sort([2, 1])             == [1, 2]
```

**Why:** Merge sort divides the array into two halves at each level — that is log n levels. At each level, merging all elements costs O(n). Total: O(n log n). The `<=` in the merge step is what makes this stable: equal elements from the left half are always taken first, preserving their original order.

**Time:** O(n log n) all cases. **Space:** O(n) for auxiliary arrays.

---

<a id="q10"></a>
### Q10 Implement Quicksort with Random Pivot

**Problem:** Implement quicksort using the Lomuto partition scheme. Use a random pivot to avoid O(n²) worst case on sorted input.

**Example:**
```
Input:  [10, 7, 8, 9, 1, 5]
Output: [1, 5, 7, 8, 9, 10]
```

<details>
<summary>Hint</summary>

Before partitioning, swap a randomly chosen element with `arr[high]`. The Lomuto scheme then treats `arr[high]` as the pivot. Partition so that all elements `<= pivot` end up left of the pivot index, all elements `> pivot` end up right.

</details>

```python
import random

def quicksort(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        pivot_idx = partition(arr, lo, hi)
        quicksort(arr, lo, pivot_idx - 1)
        quicksort(arr, pivot_idx + 1, hi)
    return arr

def partition(arr, lo, hi):
    rand = random.randint(lo, hi)              # ← random pivot
    arr[rand], arr[hi] = arr[hi], arr[rand]    # ← swap to end
    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1] # ← pivot to final position
    return i + 1

# Tests
assert quicksort([10, 7, 8, 9, 1, 5]) == [1, 5, 7, 8, 9, 10]
assert quicksort([1, 2, 3, 4, 5])     == [1, 2, 3, 4, 5]
assert quicksort([5, 4, 3, 2, 1])     == [1, 2, 3, 4, 5]
assert quicksort([])                   == []
```

**Why:** Without randomization, choosing the last element as pivot on an already-sorted array always produces partitions of size 0 and n-1 — O(n²) recursion depth. A random pivot makes worst-case O(n²) extremely unlikely. Quicksort is not stable (pivot swaps can reorder equal elements) but is cache-friendly and in-place.

**Time:** O(n log n) average, O(n²) worst. **Space:** O(log n) call stack.

---

<a id="q11"></a>
### Q11 Implement Heapsort Using heapq

**Problem:** Implement heapsort using Python's `heapq` module. Sort a list in ascending order by treating it as a min-heap.

**Example:**
```
Input:  [3, 1, 4, 1, 5, 9, 2, 6]
Output: [1, 1, 2, 3, 4, 5, 6, 9]
```

<details>
<summary>Hint</summary>

`heapq.heapify(arr)` converts a list to a min-heap in O(n). Then call `heapq.heappop` n times to extract elements in ascending order. Each pop is O(log n).

</details>

```python
import heapq

def heapsort(arr):
    heapq.heapify(arr)                          # ← O(n) build min-heap in-place
    return [heapq.heappop(arr) for _ in range(len(arr))]  # ← O(n log n)

# Tests
assert heapsort([3, 1, 4, 1, 5, 9, 2, 6]) == [1, 1, 2, 3, 4, 5, 6, 9]
assert heapsort([])                         == []
assert heapsort([1])                        == [1]

# Bonus: k-th largest using a size-k min-heap — O(n log k)
def kth_largest(arr, k):
    heap = arr[:k]
    heapq.heapify(heap)
    for x in arr[k:]:
        if x > heap[0]:
            heapq.heapreplace(heap, x)          # ← pop min, push x in one O(log k) op
    return heap[0]

assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
```

**Why:** Building the heap is O(n) because `heapify` uses a bottom-up sift-down strategy (not n insertions). Each of the n pops is O(log n), giving total O(n log n). Heapsort is in-place and guarantees O(n log n) worst case unlike quicksort. It is not stable — heap operations do not preserve relative order of equal elements.

**Time:** O(n log n) all cases. **Space:** O(1) in-place variant, O(n) for the pop-based version above.

---

<a id="q12"></a>
### Q12 Sort a Nearly-Sorted Array Efficiently

**Problem:** An array is "k-sorted" — each element is at most `k` positions away from its sorted position. Sort it efficiently. For example, with `k=3`, element at index 10 belongs somewhere in indices 7–13.

**Example:**
```
Input:  [6, 5, 3, 2, 8, 10, 9],  k=3
Output: [2, 3, 5, 6, 8, 9, 10]
```

<details>
<summary>Hint</summary>

Maintain a min-heap of size `k+1`. At each step, the smallest element in any window of size `k+1` must be the next element in the sorted output — it cannot be further displaced. Push elements into the heap; when heap size exceeds k, pop the minimum.

</details>

```python
import heapq

def sort_k_sorted(arr, k):
    """Sort a k-sorted array. Each element is at most k positions from its target."""
    heap = arr[:k + 1]
    heapq.heapify(heap)                         # ← seed the heap with first window
    result = []
    for i in range(k + 1, len(arr)):
        result.append(heapq.heapreplace(heap, arr[i]))  # ← pop min, push next
    while heap:
        result.append(heapq.heappop(heap))      # ← drain remaining
    return result

# Tests
assert sort_k_sorted([6, 5, 3, 2, 8, 10, 9], 3)  == [2, 3, 5, 6, 8, 9, 10]
assert sort_k_sorted([2, 1, 3, 5, 4], 1)          == [1, 2, 3, 4, 5]
assert sort_k_sorted([1, 2, 3], 0)                 == [1, 2, 3]
```

**Why:** Full sort would cost O(n log n). Since each element is at most k positions away, a sliding min-heap of size k+1 is guaranteed to contain the next output element at its root. This gives O(n log k) — far better when k is small. Timsort and insertion sort also excel here because nearly-sorted input triggers their O(n) best cases.

**Time:** O(n log k). **Space:** O(k).

---

<a id="q13"></a>
### Q13 Sort Array Elements by Frequency

**Problem:** Given a list of integers, sort them by frequency — most frequent first. Break ties by placing the smaller number first.

**Example:**
```
Input:  [1, 1, 2, 3, 3, 3, 4, 4]
Output: [3, 3, 3, 1, 1, 4, 4, 2]
```

<details>
<summary>Hint</summary>

Use `collections.Counter` to count frequencies. Sort using a tuple key: `(-frequency, value)`. Then reconstruct by repeating each value its frequency number of times.

</details>

```python
from collections import Counter

def sort_by_frequency(arr):
    freq = Counter(arr)                         # ← {value: count}
    # Sort unique values: high freq first (-freq), then by value ascending
    sorted_vals = sorted(freq.keys(), key=lambda x: (-freq[x], x))
    result = []
    for val in sorted_vals:
        result.extend([val] * freq[val])        # ← repeat val freq[val] times
    return result

# Tests
assert sort_by_frequency([1, 1, 2, 3, 3, 3, 4, 4]) == [3, 3, 3, 1, 1, 4, 4, 2]
assert sort_by_frequency([2, 3, 1, 3, 2])           == [2, 2, 3, 3, 1]
assert sort_by_frequency([1])                       == [1]
```

**Why:** `Counter` builds the frequency map in O(n). Sorting the unique values is O(d log d) where d is the number of distinct values. Reconstruction is O(n). Total: O(n + d log d). The `(-freq[x], x)` key handles both sort directions in a single `sorted()` call — no need for `cmp_to_key`.

**Time:** O(n + d log d) where d = distinct values. **Space:** O(n).

---

<a id="q14"></a>
### Q14 K-th Largest Element

**Problem:** Find the k-th largest element in an unsorted array. Do not sort the entire array — use a min-heap of size k for an O(n log k) solution.

**Example:**
```
Input:  arr=[3, 2, 1, 5, 6, 4],  k=2
Output: 5
```

<details>
<summary>Hint</summary>

Maintain a min-heap of the k largest elements seen so far. For each new element: if the heap has fewer than k elements, push it. Otherwise if the element is larger than the heap's minimum (`heap[0]`), replace the minimum with it. At the end, the heap's minimum is the k-th largest overall.

</details>

```python
import heapq

def kth_largest(arr, k):
    heap = []
    for x in arr:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)                 # ← discard smallest, keep top-k
    return heap[0]                              # ← k-th largest = min of top-k

# Tests
assert kth_largest([3, 2, 1, 5, 6, 4], 2)          == 5
assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
assert kth_largest([1], 1)                          == 1
```

**Why:** Sorting the entire array costs O(n log n) and is wasteful when we only need one value. The min-heap approach processes each element once and performs at most one heap operation per element — O(log k) per element, O(n log k) total. When k << n this is a significant win. The heap always holds the k largest elements seen so far; its minimum is therefore the k-th largest.

**Time:** O(n log k). **Space:** O(k).

---

<a id="q15"></a>
### Q15 Custom Comparator — Largest Number

**Problem:** Given a list of non-negative integers, arrange them to form the largest possible number. Return the result as a string.

**Example:**
```
Input:  [3, 30, 34, 5, 9]
Output: "9534330"
```

<details>
<summary>Hint</summary>

Comparing integers by value fails: `30 < 34` but `"3034" < "3430"`. Instead, compare by concatenation: `a` should come before `b` if `str(a) + str(b) > str(b) + str(a)`. Use `functools.cmp_to_key` to convert this comparison into a sort key.

</details>

```python
from functools import cmp_to_key

def largest_number(nums):
    def compare(a, b):
        ab, ba = str(a) + str(b), str(b) + str(a)
        if ab > ba: return -1                   # ← a before b
        if ab < ba: return  1                   # ← b before a
        return 0

    nums.sort(key=cmp_to_key(compare))
    result = "".join(map(str, nums))
    return "0" if result[0] == "0" else result  # ← edge case: [0, 0]

# Tests
assert largest_number([3, 30, 34, 5, 9]) == "9534330"
assert largest_number([10, 2])           == "210"
assert largest_number([3, 30])           == "330"
assert largest_number([0, 0])            == "0"
assert largest_number([1])              == "1"
```

**Why:** Direct numeric comparison cannot determine concatenation order. String concatenation comparison is transitive and total — it defines a valid ordering. `cmp_to_key` wraps this into the standard key-based sort API. The edge case `[0, 0]` produces `"00"` which must be returned as `"0"`.

**Time:** O(n log n) comparisons, each O(d) for d-digit numbers. **Space:** O(n).

---

<a id="q16"></a>
### Q16 Stability in Multi-Key Sort

**Problem:** You have a list of employee records `(name, department, salary)`. Sort first by department alphabetically, then within each department by salary descending. Demonstrate how to achieve this using Python's stable sort with two separate passes instead of a compound key.

<details>
<summary>Hint</summary>

Sort by the secondary key first (salary), then sort by the primary key (department) using a stable sort. Because stability preserves the salary ordering from pass 1 within each department group in pass 2.

</details>

```python
employees = [
    ("Alice",   "Engineering", 95000),
    ("Bob",     "Marketing",   70000),
    ("Carol",   "Engineering", 110000),
    ("Dave",    "Marketing",   80000),
    ("Eve",     "Engineering", 95000),
]

# Two-pass stable sort:
employees.sort(key=lambda e: e[2], reverse=True)   # pass 1: by salary desc
employees.sort(key=lambda e: e[1])                  # pass 2: by department asc (stable)

for emp in employees:
    print(emp)

# Expected: Engineering group sorted by salary desc, Marketing group sorted by salary desc
# ('Carol', 'Engineering', 110000)
# ('Alice', 'Engineering', 95000)   ← Alice before Eve (equal salary, Alice first in pass 1)
# ('Eve',   'Engineering', 95000)
# ('Dave',  'Marketing',   80000)
# ('Bob',   'Marketing',   70000)

assert employees[0][0] == "Carol"
assert employees[1][0] == "Alice"  # same salary as Eve, but Alice came first
assert employees[3][0] == "Dave"
```

**Why:** This is the classic two-pass stable sort pattern. It works because Python's sort is stable: pass 2 reorders by department but preserves the relative salary ordering within each department from pass 1. Equivalent to `key=lambda e: (e[1], -e[2])` in one pass, but the two-pass style is easier to read and debug when keys are complex.

**Time:** O(n log n) per pass. **Space:** O(n).

---

<a id="q17"></a>
### Q17 Radix Sort

**Problem:** Implement LSD (least-significant digit) radix sort for a list of non-negative integers. Process digits from least significant to most significant.

**Example:**
```
Input:  [329, 457, 657, 839, 436, 720, 355]
Output: [329, 355, 436, 457, 657, 720, 839]
```

<details>
<summary>Hint</summary>

Find the maximum value to determine the number of digit passes. For each pass (ones, tens, hundreds, ...): group numbers into 10 buckets (0–9) based on the current digit. Flatten the buckets back into the array. Each pass must be stable to preserve the ordering from previous passes.

</details>

```python
def radix_sort(arr):
    if not arr:
        return arr
    max_val = max(arr)
    exp = 1                                     # ← start at ones digit
    while max_val // exp > 0:
        arr = counting_sort_by_digit(arr, exp)
        exp *= 10
    return arr

def counting_sort_by_digit(arr, exp):
    buckets = [[] for _ in range(10)]
    for x in arr:
        digit = (x // exp) % 10                 # ← extract current digit
        buckets[digit].append(x)                # ← stable: append preserves order
    return [x for bucket in buckets for x in bucket]

# Tests
assert radix_sort([329, 457, 657, 839, 436, 720, 355]) == [329, 355, 436, 457, 657, 720, 839]
assert radix_sort([1, 10, 100, 1000])                  == [1, 10, 100, 1000]
assert radix_sort([])                                  == []
assert radix_sort([5, 3, 8, 1])                        == [1, 3, 5, 8]
```

**Why:** Radix sort makes d passes where d is the number of digits in the maximum value. Each pass is O(n + 10) = O(n). Total: O(d * n). For 32-bit integers d ≤ 10, so this is effectively O(n). The algorithm is not comparison-based — it exploits the structure of integer representation. Each pass must be stable so that previous digit orderings are preserved.

**Time:** O(d * n). **Space:** O(n + 10) per pass.

---

<a id="q18"></a>
### Q18 Merge Two Sorted Arrays

**Problem:** Given two sorted arrays `a` and `b`, merge them into one sorted array in O(m + n) time without calling sort.

**Example:**
```
Input:  a=[1, 3, 5, 7],  b=[2, 4, 6, 8]
Output: [1, 2, 3, 4, 5, 6, 7, 8]
```

<details>
<summary>Hint</summary>

Use two pointers `i` and `j` starting at 0. Compare `a[i]` and `b[j]`; append the smaller and advance its pointer. When one array is exhausted, append all remaining elements of the other.

</details>

```python
def merge_sorted(a, b):
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:                        # ← <= keeps it stable
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:])                        # ← append remaining
    result.extend(b[j:])
    return result

# Tests
assert merge_sorted([1, 3, 5, 7], [2, 4, 6, 8]) == [1, 2, 3, 4, 5, 6, 7, 8]
assert merge_sorted([], [1, 2, 3])              == [1, 2, 3]
assert merge_sorted([1, 2], [])                 == [1, 2]
assert merge_sorted([1, 1], [1, 1])             == [1, 1, 1, 1]
```

**Why:** This is the core subroutine of merge sort and external merge sort. Because both inputs are already sorted, each element is visited exactly once — O(m + n). The `<=` ensures stability: equal elements from `a` are always taken before elements from `b`. This is the same logic used in the merge step of merge sort.

**Time:** O(m + n). **Space:** O(m + n).

---

<a id="q19"></a>
### Q19 Sort a Dictionary by Value

**Problem:** Given a word-frequency dictionary, return the items sorted by frequency descending. When frequencies tie, sort by word alphabetically.

**Example:**
```
Input:  {"apple": 3, "banana": 5, "cherry": 3, "date": 1}
Output: [("banana", 5), ("apple", 3), ("cherry", 3), ("date", 1)]
```

<details>
<summary>Hint</summary>

Call `sorted(d.items(), key=...)`. Use a tuple key: `(-value, key_name)` to sort by frequency descending then by word alphabetically. Dicts are not inherently sortable — convert to items first.

</details>

```python
def sort_dict_by_value(d):
    return sorted(d.items(), key=lambda item: (-item[1], item[0]))

# Tests
d = {"apple": 3, "banana": 5, "cherry": 3, "date": 1}
result = sort_dict_by_value(d)
assert result == [("banana", 5), ("apple", 3), ("cherry", 3), ("date", 1)]

# Alternative — just sorted keys:
sorted_keys = sorted(d, key=d.get, reverse=True)
assert sorted_keys[0] == "banana"
```

**Why:** `d.items()` produces a view of `(key, value)` pairs that `sorted()` can consume. Dictionaries in Python 3.7+ maintain insertion order, but that is not sorted order — you must call `sorted()`. The `(-value, key)` tuple key sorts by value descending and breaks ties alphabetically in a single pass.

**Time:** O(n log n). **Space:** O(n).

---

<a id="q20"></a>
### Q20 Timsort O(n) Best Case

**Problem:** Explain why Python's `list.sort()` runs in O(n) on an already-sorted list. Then write a benchmark that confirms this by timing a sorted vs random input of 1,000,000 elements.

<details>
<summary>Hint</summary>

Timsort scans for "runs" (already-sorted sequences). If the entire array is one run, no merge phase is needed — Timsort just verifies the run covers the whole array in O(n). For a reverse-sorted array it reverses the single run in O(n).

</details>

```python
import time, random

def benchmark_timsort():
    n = 1_000_000
    already_sorted = list(range(n))
    random_data     = random.sample(range(n), n)

    copy1 = already_sorted.copy()
    t0 = time.perf_counter()
    copy1.sort()
    t1 = time.perf_counter()
    print(f"Already sorted: {(t1 - t0) * 1000:.1f} ms")  # ← should be << random

    copy2 = random_data.copy()
    t0 = time.perf_counter()
    copy2.sort()
    t1 = time.perf_counter()
    print(f"Random input:   {(t1 - t0) * 1000:.1f} ms")

benchmark_timsort()
# Example output:
# Already sorted: 12.3 ms   ← O(n)
# Random input:   183.7 ms  ← O(n log n)
```

**Why:** Timsort's run-detection phase is always O(n) — it walks the array once. If it finds one run that covers the entire array, it returns immediately without entering the merge phase. The merge phase is only invoked when multiple runs exist. This makes Timsort O(n) on already-sorted, reverse-sorted, and "nearly-sorted" inputs, which matches real-world data patterns.

**Time:** O(n) best, O(n log n) worst. **Space:** O(n).

---

## Advanced Questions

---

<a id="q21"></a>
### Q21 Sort Colors — Dutch National Flag

**Problem:** Given an array with only three distinct values (0, 1, 2), sort it in-place in a single pass using O(1) extra space. This is the Dutch National Flag problem.

**Example:**
```
Input:  [2, 0, 2, 1, 1, 0]
Output: [0, 0, 1, 1, 2, 2]
```

<details>
<summary>Hint</summary>

Use three pointers: `lo` (boundary of 0-zone), `mid` (current element), `hi` (boundary of 2-zone). Walk `mid` from left to right. If `arr[mid] == 0`, swap with `arr[lo]` and advance both. If `arr[mid] == 2`, swap with `arr[hi]` and retreat `hi` only. If `arr[mid] == 1`, just advance `mid`.

</details>

```python
def sort_colors(arr):
    lo, mid, hi = 0, 0, len(arr) - 1       # ← three-pointer Dutch flag
    while mid <= hi:
        if arr[mid] == 0:
            arr[lo], arr[mid] = arr[mid], arr[lo]
            lo += 1; mid += 1               # ← 0 placed, advance both
        elif arr[mid] == 2:
            arr[mid], arr[hi] = arr[hi], arr[mid]
            hi -= 1                         # ← 2 placed; DON'T advance mid
        else:
            mid += 1                        # ← 1 stays in place

# Tests
arr = [2, 0, 2, 1, 1, 0];  sort_colors(arr);  assert arr == [0, 0, 1, 1, 2, 2]
arr = [0];                  sort_colors(arr);  assert arr == [0]
arr = [2, 2, 2];            sort_colors(arr);  assert arr == [2, 2, 2]
arr = [1, 2, 0];            sort_colors(arr);  assert arr == [0, 1, 2]
```

**Why:** Counting sort would work in O(n) with O(1) space, but this three-pointer approach is a single pass — the array is sorted as the pointer advances. When `arr[mid] == 2` and we swap with `hi`, we do not advance `mid` because the swapped element needs to be evaluated. This invariant is the subtle heart of the algorithm.

**Time:** O(n). **Space:** O(1).

---

<a id="q22"></a>
### Q22 Meeting Rooms — Sort by Start Time

**Problem:** Given a list of meeting intervals `[start, end]`, determine the minimum number of conference rooms required to hold all meetings simultaneously.

**Example:**
```
Input:  [[0,30],[5,10],[15,20]]
Output: 2
```

<details>
<summary>Hint</summary>

Sort meetings by start time. Use a min-heap to track end times of ongoing meetings. For each meeting, check if the earliest-ending meeting has finished (heap min <= current start). If yes, reuse that room (replace the heap's min). Otherwise, allocate a new room.

</details>

```python
import heapq

def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[0])         # ← sort by start time
    end_times = []                              # ← min-heap of end times
    for start, end in intervals:
        if end_times and end_times[0] <= start:
            heapq.heapreplace(end_times, end)   # ← reuse room (pop old end, push new)
        else:
            heapq.heappush(end_times, end)      # ← new room needed
    return len(end_times)

# Tests
assert min_meeting_rooms([[0,30],[5,10],[15,20]])     == 2
assert min_meeting_rooms([[7,10],[2,4]])               == 1
assert min_meeting_rooms([[1,5],[2,6],[3,7],[4,8]])   == 4
assert min_meeting_rooms([])                          == 0
```

**Why:** Sorting by start time means we process meetings in the order they begin. The min-heap always gives us the meeting that will end soonest. If that meeting ends before the current one starts (`heap[0] <= start`), we can reuse its room. Otherwise every currently-active meeting overlaps with the new one, so we need a new room. The heap size at the end equals the maximum overlap count.

**Time:** O(n log n) for sort + O(n log n) for heap ops. **Space:** O(n).

---

<a id="q23"></a>
### Q23 Merge Intervals

**Problem:** Given a list of intervals, merge all overlapping intervals and return the resulting list.

**Example:**
```
Input:  [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
```

<details>
<summary>Hint</summary>

Sort by start time. Walk through intervals maintaining a `current` interval. If the next interval's start is within `current` (i.e., `<= current[1]`), extend `current[1]` to the max of both ends. Otherwise, commit `current` to the result and move on.

</details>

```python
def merge_intervals(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])         # ← sort by start time
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:              # ← overlaps with last merged
            merged[-1][1] = max(merged[-1][1], end)  # ← extend end
        else:
            merged.append([start, end])         # ← no overlap, commit new interval
    return merged

# Tests
assert merge_intervals([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]
assert merge_intervals([[1,4],[4,5]])                == [[1,5]]
assert merge_intervals([[1,4],[0,4]])                == [[0,4]]
assert merge_intervals([[1,4]])                     == [[1,4]]
```

**Why:** Sorting ensures overlapping intervals are adjacent. Without sorting, you would need O(n²) pairwise comparisons to detect all overlaps. After sorting, a single linear scan is sufficient — you only need to compare each interval against the last committed merged interval. The critical edge case is `start <= current_end` (not `<`): touching intervals like `[1,4]` and `[4,5]` should merge into `[1,5]`.

**Time:** O(n log n). **Space:** O(n) for output.

---

<a id="q24"></a>
### Q24 External Merge Sort with a Min-Heap

**Problem:** Implement the merge phase of external merge sort: given k sorted lists (representing sorted file chunks), merge them into one sorted sequence using a min-heap. This is the real-world pattern used by GNU sort, Hadoop shuffle, and Spark.

**Example:**
```
Input:  [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
Output: [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

<details>
<summary>Hint</summary>

Use a min-heap seeded with the first element from each list (value, list_index, element_index). On each iteration, pop the smallest, add it to output, and push the next element from the same list (if any). `heapq.merge` in Python's stdlib does exactly this.

</details>

```python
import heapq

def k_way_merge(sorted_lists):
    """Merge k sorted lists using a min-heap — O(n log k)."""
    heap = []
    for list_idx, lst in enumerate(sorted_lists):
        if lst:
            heapq.heappush(heap, (lst[0], list_idx, 0))  # (val, list_idx, elem_idx)

    result = []
    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        next_idx = elem_idx + 1
        if next_idx < len(sorted_lists[list_idx]):
            next_val = sorted_lists[list_idx][next_idx]
            heapq.heappush(heap, (next_val, list_idx, next_idx))

    return result

# Tests
assert k_way_merge([[1,4,7],[2,5,8],[3,6,9]])   == list(range(1, 10))
assert k_way_merge([[1],[2],[3]])               == [1, 2, 3]
assert k_way_merge([[]])                        == []
assert k_way_merge([[1,3,5],[2,4,6],[]])        == [1, 2, 3, 4, 5, 6]

# Python stdlib shortcut:
import heapq
assert list(heapq.merge(*[[1,4,7],[2,5,8],[3,6,9]])) == list(range(1, 10))
```

**Why:** With k sorted lists of total n elements, a naive merge (sort everything together) costs O(n log n). The heap-based k-way merge costs O(n log k) — crucial when k << n. The heap always holds exactly k elements (one per list), so each pop/push is O(log k). This is identical to the algorithm PostgreSQL and GNU sort use when merging sorted run files during an external sort.

**Time:** O(n log k). **Space:** O(k) for heap.

---

<a id="q25"></a>
### Q25 Choose the Right Sort — 5 Scenarios

**Problem:** For each of the five scenarios below, state which sorting algorithm to use, give the time complexity, and explain the key reason.

1. Sort 10 million user records by last name for a report. Stability required.
2. Sort a 50-element array that is 90% already sorted.
3. Sort 1 million integer ages (values 0–120) for a histogram.
4. Find the top 100 highest-scoring players from 5 million records. Do not sort everything.
5. Sort 200 GB of log files that cannot fit in RAM.

<details>
<summary>Hint</summary>

Think about: size, memory constraints, stability need, value range, and whether you need a full sort or just partial results.

</details>

```python
scenarios = {
    1: {
        "algorithm": "Python sorted() / Timsort",
        "complexity": "O(n log n)",
        "reason": (
            "Stability is required. Timsort is stable and O(n log n) worst case. "
            "For 10M records where data may have partially-ordered runs (sorted by first name "
            "already), Timsort also exploits existing order to run faster than O(n log n) in practice."
        ),
    },
    2: {
        "algorithm": "Insertion Sort (or Timsort)",
        "complexity": "O(n) to O(n*k) for k-sorted input",
        "reason": (
            "Nearly-sorted small arrays are insertion sort's sweet spot. "
            "With 90% already in order, very few shifts are needed. "
            "Timsort detects runs and falls back to insertion sort for small/nearly-sorted segments."
        ),
    },
    3: {
        "algorithm": "Counting Sort",
        "complexity": "O(n + k) where k=121",
        "reason": (
            "Integer values in a known small range (0-120). Counting sort is O(n + 121) ≈ O(n). "
            "No comparisons needed. Far better than O(n log n) comparison sort. "
            "Also directly gives the frequency histogram as a side effect."
        ),
    },
    4: {
        "algorithm": "Min-heap of size 100 (heapq.nlargest)",
        "complexity": "O(n log 100) = O(n)",
        "reason": (
            "Full sort is O(n log n) and wasteful — we only need 100 out of 5M elements. "
            "A min-heap of size 100 processes each element in O(log 100) ≈ O(1). "
            "heapq.nlargest(100, records, key=lambda r: r.score) does exactly this."
        ),
    },
    5: {
        "algorithm": "External Merge Sort",
        "complexity": "O(n log n) with O(chunk_size) RAM",
        "reason": (
            "Data exceeds RAM. Phase 1: read chunks that fit in memory, sort each with Timsort, "
            "write sorted runs to disk. Phase 2: k-way merge of sorted runs using a min-heap. "
            "Only k file pointers live in memory at once. "
            "This is how GNU sort, Hadoop MapReduce shuffle, and Spark sort work."
        ),
    },
}

for scenario_num, answer in scenarios.items():
    print(f"\nScenario {scenario_num}:")
    print(f"  Algorithm:   {answer['algorithm']}")
    print(f"  Complexity:  {answer['complexity']}")
    print(f"  Reason:      {answer['reason']}")
```

**Why:** Sorting is never one-size-fits-all. The decision tree: do you know the value range? → counting/radix sort. Do you need only partial results? → heap. Does data exceed RAM? → external merge sort. Is stability required? → merge sort / Timsort. Otherwise → quicksort (best average constants) or Timsort (Python default). Senior engineers choose based on constraints, not habit.

**Time:** Varies by scenario (O(n) to O(n log n)). **Space:** Varies by scenario.

---

**[Back to README](../README.md)**

**Prev:** [Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Searching — Theory](../06_searching/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
