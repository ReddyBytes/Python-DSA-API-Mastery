# Sorting — Cheatsheet

## Sorting Algorithms Comparison Table

```
+------------------+------------------+-----------------+-------+--------+-----------------------------------+
| Algorithm        | Best       Time  | Avg       Time  | Worst | Space  | Notes                             |
+------------------+------------------+-----------------+-------+--------+-----------------------------------+
| Bubble sort      | O(n)             | O(n^2)          | O(n^2)| O(1)   | Stable. Never use in practice.    |
| Selection sort   | O(n^2)           | O(n^2)          | O(n^2)| O(1)   | NOT stable. Minimizes swaps.      |
| Insertion sort   | O(n)             | O(n^2)          | O(n^2)| O(1)   | Stable. Fast on nearly-sorted.    |
| Merge sort       | O(n log n)       | O(n log n)      | same  | O(n)   | Stable. Guaranteed O(n log n).    |
| Quick sort       | O(n log n)       | O(n log n)      | O(n^2)| O(log n)| NOT stable. Fast in practice.   |
| Heap sort        | O(n log n)       | O(n log n)      | same  | O(1)   | NOT stable. In-place.             |
| Counting sort    | O(n + k)         | O(n + k)        | same  | O(k)   | NOT comparison. k=value range.    |
| Radix sort       | O(d*(n+k))       | O(d*(n+k))      | same  | O(n+k) | NOT comparison. d=digit count.    |
| Tim sort         | O(n)             | O(n log n)      | same  | O(n)   | Stable. Python's built-in.        |
+------------------+------------------+-----------------+-------+--------+-----------------------------------+

Stability: a stable sort preserves relative order of equal elements.
```

---

## Python Sort — list.sort() vs sorted()

```python
arr = [3, 1, 4, 1, 5, 9, 2, 6]

# In-place — modifies arr, returns None
arr.sort()
arr.sort(reverse=True)

# Returns new sorted list — original unchanged
new_arr = sorted(arr)
new_arr = sorted(arr, reverse=True)

# Key differences:
#   .sort()   — only on lists, slightly faster (no new list allocation)
#   sorted()  — works on ANY iterable (tuples, generators, sets, dicts...)

# Both are TimSort: O(n log n) worst, O(n) best (nearly sorted input)
# Both are STABLE — equal elements maintain original relative order
```

---

## Python TimSort — When It's O(n)

```
TimSort detects "runs" (already sorted or reverse-sorted subsequences)
and merges them.

O(n) cases:
  - Already sorted array
  - Reverse sorted array (one run, just reverse)
  - Array made of a few sorted "runs"

O(n log n) cases:
  - Random order input

Practical implication:
  If your input is nearly sorted, Python sort is almost free.
  Mention this in interviews when relevant.
```

---

## Custom Sort with key=

```python
# Sort by string length
words = ["banana", "fig", "apple", "kiwi"]
words.sort(key=len)                         # ['fig', 'kiwi', 'apple', 'banana']

# Sort by lambda
arr = [(1, 3), (2, 1), (3, 2)]
arr.sort(key=lambda x: x[1])               # sort by second element
# => [(2,1), (3,2), (1,3)]

# Sort descending by first, ascending by second (multi-key)
arr.sort(key=lambda x: (-x[0], x[1]))

# Sort strings case-insensitive
words.sort(key=str.lower)

# Sort objects by attribute
students = [Student("Alice", 90), Student("Bob", 85)]
students.sort(key=lambda s: s.grade, reverse=True)

# Multi-key sort on tuples — tuples compare lexicographically
pairs = [(1, 2), (1, 1), (2, 0)]
pairs.sort()                                # sort by first, then second

# functools.cmp_to_key — when you need a comparator function
from functools import cmp_to_key
def compare(a, b):
    # return negative if a < b, 0 if equal, positive if a > b
    return a - b
arr.sort(key=cmp_to_key(compare))

# Largest number from array of ints (classic interview):
from functools import cmp_to_key
def largest_number(nums):
    nums = list(map(str, nums))
    nums.sort(key=cmp_to_key(lambda a, b: 1 if a+b < b+a else -1))
    return "0" if nums[0] == "0" else "".join(nums)
```

---

## Template 1 — Merge Sort

```python
# Stable | O(n log n) all cases | O(n) space

def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left  = merge_sort(arr[:mid])       # sort left half
    right = merge_sort(arr[mid:])       # sort right half
    return _merge(left, right)

def _merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:         # <= preserves stability
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Use merge sort when:
#   - Need guaranteed O(n log n)
#   - Need stable sort
#   - Sorting linked lists (no random access needed)
#   - External sort (data larger than memory)
```

---

## Template 2 — Quick Sort

```python
# NOT stable | O(n log n) avg | O(n^2) worst | O(log n) space avg

def quick_sort(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        pivot_idx = _partition(arr, lo, hi)
        quick_sort(arr, lo, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, hi)

def _partition(arr, lo, hi):
    pivot = arr[hi]                     # choose last element as pivot
    i = lo - 1                          # pointer for smaller elements
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i+1], arr[hi] = arr[hi], arr[i+1]
    return i + 1

# Randomized pivot (avoids O(n^2) worst case on sorted input):
import random
def _partition_random(arr, lo, hi):
    rand = random.randint(lo, hi)
    arr[rand], arr[hi] = arr[hi], arr[rand]
    return _partition(arr, lo, hi)

# Use quick sort when:
#   - In-place sort needed (O(log n) space vs O(n) for merge sort)
#   - Average case performance matters
#   - NOT when worst-case O(n^2) is unacceptable
```

---

## Template 3 — Heap Sort (using heapq)

```python
import heapq

# NOT stable | O(n log n) | O(1) extra space (in-place variant)

# Using heapq (min-heap) — returns new sorted list:
def heap_sort_asc(arr):
    heapq.heapify(arr)              # O(n) in-place
    return [heapq.heappop(arr) for _ in range(len(arr))]  # O(n log n)

# For descending, negate values (Python only has min-heap):
def heap_sort_desc(arr):
    neg = [-x for x in arr]
    heapq.heapify(neg)
    return [-heapq.heappop(neg) for _ in range(len(neg))]

# heapq utility functions:
heapq.nlargest(k, arr)              # O(n log k) — top k largest
heapq.nsmallest(k, arr)             # O(n log k) — top k smallest
heapq.nlargest(k, arr, key=lambda x: x[1])  # with key function

# Use heap sort / heapq when:
#   - Only need top-k elements (nlargest/nsmallest >> full sort)
#   - Building a priority queue
#   - Streaming data (push as data arrives, pop min/max)
```

---

## Template 4 — Counting Sort

```python
# NOT comparison | O(n + k) time | O(k) space
# k = range of input values (max_val - min_val + 1)

def counting_sort(arr):
    if not arr: return arr
    lo, hi = min(arr), max(arr)
    count = [0] * (hi - lo + 1)

    for x in arr:
        count[x - lo] += 1              # frequency count

    result = []
    for i, c in enumerate(count):
        result.extend([i + lo] * c)     # reconstruct
    return result

# Stable counting sort (preserves original order of equal elements):
def counting_sort_stable(arr, key=lambda x: x):
    lo = min(key(x) for x in arr)
    hi = max(key(x) for x in arr)
    buckets = [[] for _ in range(hi - lo + 1)]
    for x in arr:
        buckets[key(x) - lo].append(x)
    return [x for bucket in buckets for x in bucket]

# Use counting sort when:
#   - Values are bounded integers in a small range (k << n)
#   - e.g., ages 0-100, scores 0-10, characters a-z
#   - Need linear time sort guarantee
```

---

## Sorting Objects / Multi-Key Sort

```python
# Dataclass example
from dataclasses import dataclass

@dataclass
class Student:
    name: str
    grade: int
    age: int

students = [Student("Alice", 90, 20), Student("Bob", 90, 19), Student("Charlie", 85, 21)]

# Sort by grade desc, then name asc:
students.sort(key=lambda s: (-s.grade, s.name))

# Sort tuples — lexicographic by default:
records = [(90, "Alice"), (85, "Bob"), (90, "Charlie")]
records.sort()                          # (85, Bob), (90, Alice), (90, Charlie)
records.sort(key=lambda x: (-x[0], x[1]))  # grade desc, name asc

# Sort dict by value:
d = {"a": 3, "b": 1, "c": 2}
sorted_items = sorted(d.items(), key=lambda x: x[1])
sorted_keys  = sorted(d, key=d.get)

# Sort with None values (put None last):
arr = [3, None, 1, None, 2]
arr.sort(key=lambda x: (x is None, x))  # False < True so non-None first
```

---

## heapq Quick Reference

```python
import heapq

h = []
heapq.heappush(h, 5)           # push element
heapq.heappop(h)                # pop smallest
h[0]                            # peek smallest (no pop)
heapq.heapify(lst)              # convert list to heap in-place O(n)
heapq.heappushpop(h, x)        # push then pop (faster than separate calls)
heapq.heapreplace(h, x)        # pop then push (heap must be non-empty)

# Max-heap: negate values
heapq.heappush(h, -val)
max_val = -heapq.heappop(h)

# Heap of tuples (sorts by first element):
heapq.heappush(h, (priority, item))

# k-th largest element (heap approach O(n log k)):
def kth_largest(arr, k):
    heap = arr[:k]
    heapq.heapify(heap)                 # min-heap of size k
    for x in arr[k:]:
        if x > heap[0]:
            heapq.heapreplace(heap, x)
    return heap[0]                      # smallest in heap = k-th largest
```

---

## Interview: Key Points to Mention

```
Stable sort guarantee:
  Python's sort IS stable (TimSort).
  Merge sort IS stable.
  Quick sort and heap sort are NOT stable by default.
  When interviewer asks "is your sort stable?" — if using Python built-in: YES.

Sort by multiple criteria:
  Use tuples as sort key: key=lambda x: (primary, secondary)
  Negation trick for descending: key=lambda x: (-primary, secondary)
  functools.cmp_to_key for complex comparison logic

When to avoid comparison sort:
  If values are bounded integers -> counting sort O(n+k)
  If sorting strings of fixed length -> radix sort O(d*n)
  Lower bound for comparison sorts is O(n log n) — cannot do better

Common interview patterns using sort:
  - Meeting rooms (sort by start time)
  - Merge intervals (sort by start, greedy merge)
  - Largest number (custom comparator)
  - K closest points (sort by distance, or heap)
  - Minimum platforms (sort arrivals + departures)
```

---

## Gotchas / Traps

```
1. list.sort() returns None — common mistake:
   WRONG:  arr = arr.sort()        # arr is now None
   RIGHT:  arr.sort()

2. sorted() works on any iterable but returns a LIST, not the original type:
   sorted({3,1,2})  => [1,2,3] (list, not set)

3. Sorting with key= does NOT change stored values — only affects comparison:
   arr.sort(key=abs)  — original negative values stay negative

4. Quick sort worst case on sorted input without randomization:
   Always use random pivot or median-of-3 for production code

5. heapq is a MIN-heap — negate values for max-heap behavior

6. heapq with tuples: (priority, item) — if priorities equal,
   Python will compare items next, which may fail if items are not comparable
   Fix: (priority, counter, item) with a unique counter

7. Counting sort requires integer keys in a known range — not for floats/strings

8. Stable sort + key= is very powerful:
   First sort by secondary key, then stable-sort by primary key
   (two-pass stable sort achieves multi-key sort)
```
