# 💻 Heaps — Practice

> 25 questions covering heap property, Python heapq module, max-heap via negation, top-K patterns, merge K sorted lists, median of data stream, task scheduler, heap sort, and common mistakes.

---

## Quick Index

| # | Difficulty | Topic |
|---|---|---|
| [Q1](#q1) | 🟢 Basic | Min-heap property check |
| [Q2](#q2) | 🟢 Basic | Max-heap property check |
| [Q3](#q3) | 🟢 Basic | heapq push and pop |
| [Q4](#q4) | 🟢 Basic | heapq heapify — O(n) batch build |
| [Q5](#q5) | 🟢 Basic | nlargest and nsmallest |
| [Q6](#q6) | 🟢 Basic | Max-heap via negation |
| [Q7](#q7) | 🟢 Basic | Peek without popping — heap[0] |
| [Q8](#q8) | 🟢 Basic | Heap sort |
| [Q9](#q9) | 🟡 Intermediate | Kth largest element |
| [Q10](#q10) | 🟡 Intermediate | Kth smallest element |
| [Q11](#q11) | 🟡 Intermediate | Top-K largest elements |
| [Q12](#q12) | 🟡 Intermediate | Top-K most frequent elements |
| [Q13](#q13) | 🟡 Intermediate | Merge K sorted lists |
| [Q14](#q14) | 🟡 Intermediate | K closest points to origin |
| [Q15](#q15) | 🟡 Intermediate | Task scheduler with cooldown |
| [Q16](#q16) | 🟡 Intermediate | When heap beats sorted array |
| [Q17](#q17) | 🟡 Intermediate | Sliding window maximum — heap approach |
| [Q18](#q18) | 🟡 Intermediate | Heap as priority queue |
| [Q19](#q19) | 🟡 Intermediate | Tuple tiebreaker for non-comparable items |
| [Q20](#q20) | 🟡 Intermediate | heapify in loop — O(n²) mistake |
| [Q21](#q21) | 🔴 Advanced | Median of data stream — two heaps |
| [Q22](#q22) | 🔴 Advanced | Sliding median with lazy deletion |
| [Q23](#q23) | 🔴 Advanced | Reorganize string — greedy max-heap |
| [Q24](#q24) | 🔴 Advanced | Median stream with remove support |
| [Q25](#q25) | 🔴 Advanced | Design a streaming top-K tracker |

---

<a id="q1"></a>
### Q1 🟢 · Min-heap property check

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)



**Problem:** Write `is_min_heap(arr: list[int]) -> bool` that returns `True` if the array satisfies the min-heap property. Test it on `[1, 3, 5, 7, 9, 8]` (valid) and `[1, 3, 5, 2, 9, 8]` (invalid — `arr[3]=2` violates `parent=3`).

<details>
<summary>💡 Hint</summary>

For every index `i` from 1 to `len(arr)-1`, check that `arr[(i-1)//2] <= arr[i]`. If any parent is greater than its child, the property is broken.
</details>

<details>
<summary>✅ Answer</summary>

```python
def is_min_heap(arr):
    for i in range(1, len(arr)):
        parent = (i - 1) // 2
        if arr[parent] > arr[i]:
            return False
    return True

print(is_min_heap([1, 3, 5, 7, 9, 8]))   # True
print(is_min_heap([1, 3, 5, 2, 9, 8]))   # False — arr[1]=3 > arr[3]=2
```

**Why:** The min-heap property says every parent must be ≤ both children. Checking from index 1 upward covers every parent-child pair exactly once. The root (index 0) has no parent, so we start at 1.

**Time:** O(n). **Space:** O(1).
</details>

---

<a id="q2"></a>
### Q2 🟢 · Max-heap property check

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)



**Problem:** Write `is_max_heap(arr: list[int]) -> bool` that returns `True` if the array satisfies the max-heap property. Test on `[9, 7, 8, 3, 5, 6]` (valid) and `[9, 7, 8, 10, 5, 6]` (invalid).

<details>
<summary>💡 Hint</summary>

Same index math as Q1, but the condition flips: the parent must be `>=` the child, not `<=`.
</details>

<details>
<summary>✅ Answer</summary>

```python
def is_max_heap(arr):
    for i in range(1, len(arr)):
        parent = (i - 1) // 2
        if arr[parent] < arr[i]:
            return False
    return True

print(is_max_heap([9, 7, 8, 3, 5, 6]))    # True
print(is_max_heap([9, 7, 8, 10, 5, 6]))   # False — arr[1]=7 < arr[3]=10
```

**Why:** The max-heap property requires every parent ≥ both children. The index math is identical to a min-heap — only the comparison direction changes. Python's `heapq` never gives you a max-heap natively; it always enforces the min property.

**Time:** O(n). **Space:** O(1).
</details>

---

<a id="q3"></a>
### Q3 🟢 · heapq push and pop

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)



**Problem:** Using `heapq`, push the values `[5, 1, 8, 3, 9, 2]` one at a time into an empty heap, then pop all elements and confirm they come out in ascending order.

<details>
<summary>💡 Hint</summary>

`heapq.heappush(h, val)` adds a value and fixes the heap in O(log n). `heapq.heappop(h)` always removes and returns the minimum.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

h = []
for val in [5, 1, 8, 3, 9, 2]:
    heapq.heappush(h, val)

result = []
while h:
    result.append(heapq.heappop(h))

print(result)   # [1, 2, 3, 5, 8, 9]
assert result == sorted([5, 1, 8, 3, 9, 2])
```

**Why:** heappush maintains the heap invariant after each insertion by "bubbling up" the new element until its parent is smaller. heappop swaps the root with the last element, removes the last, then "sifts down" to restore the property. Each operation is O(log n).

**Time:** O(n log n) total. **Space:** O(n).
</details>

---

<a id="q4"></a>
### Q4 🟢 · heapq heapify — O(n) batch build

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)



**Problem:** Given `data = [7, 3, 1, 9, 4, 6, 2]`, use `heapq.heapify` to convert it to a heap in-place. Then assert that `data[0]` equals the minimum (1) and that the original list reference has been modified.

<details>
<summary>💡 Hint</summary>

`heapq.heapify(lst)` works in-place and runs in O(n) — not O(n log n). The trick is that half the nodes are leaves and need zero sifting; the rest need progressively less sifting as you work up from the bottom.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

data = [7, 3, 1, 9, 4, 6, 2]
heapq.heapify(data)          # modifies data in-place

print(data[0])               # 1 — guaranteed minimum at root
assert data[0] == 1

# The list is still the same object, just rearranged
print(data)                  # e.g. [1, 3, 2, 9, 4, 6, 7]
```

**Why:** heapify starts from the last non-leaf (index `n//2 - 1`) and sifts down toward the root. Leaves do zero work. The total operations sum to O(n) via a geometric series argument — this is why heapify is faster than pushing n items one at a time (which costs O(n log n)).

**Time:** O(n). **Space:** O(1) extra.
</details>

---

<a id="q5"></a>
### Q5 🟢 · nlargest and nsmallest

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)



**Problem:** Given `nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]`, use `heapq.nlargest` and `heapq.nsmallest` to find the 3 largest and 3 smallest values. Then explain when you should use `sorted()` instead.

<details>
<summary>💡 Hint</summary>

`heapq.nlargest(k, iterable)` and `heapq.nsmallest(k, iterable)` both run in O(n log k). If k is close to n, plain `sorted()` is equally fast and simpler.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]

top3    = heapq.nlargest(3, nums)    # [9, 6, 5]
bottom3 = heapq.nsmallest(3, nums)  # [1, 1, 2]

print("Largest 3: ", top3)
print("Smallest 3:", bottom3)

# Rule of thumb: if k > n/10, just sort
# sorted() is O(n log n) regardless of k, but has lower constant
```

**Why:** For k << n, a heap of size k scans the array doing O(log k) work per element — far cheaper than sorting everything. When k approaches n, sorting is simpler and comparable in speed. Python's built-in `nlargest`/`nsmallest` use this exact heap approach internally.

**Time:** O(n log k). **Space:** O(k).
</details>

---

<a id="q6"></a>
### Q6 🟢 · Max-heap via negation

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)



**Problem:** Python's `heapq` is always a min-heap. Simulate a max-heap by negating values. Push `[4, 7, 2, 9, 1]` into a max-heap and pop them in descending order.

<details>
<summary>💡 Hint</summary>

Negate on push: `heapq.heappush(h, -val)`. Negate again on pop: `-heapq.heappop(h)`. The min-heap of negated values behaves exactly like a max-heap of original values.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

h = []
for val in [4, 7, 2, 9, 1]:
    heapq.heappush(h, -val)   # store negated

result = []
while h:
    result.append(-heapq.heappop(h))  # un-negate on pop

print(result)   # [9, 7, 4, 2, 1]
assert result == sorted([4, 7, 2, 9, 1], reverse=True)
```

**Why:** Python has no built-in max-heap. The standard trick is to negate every value before pushing. Since the min-heap always pops the smallest value, negating turns the smallest negated value into the largest original value. Common interview pattern: `heapq.heappush(h, (-priority, item))`.

**Time:** O(n log n) total. **Space:** O(n).
</details>

---

<a id="q7"></a>
### Q7 🟢 · Peek without popping — heap[0]

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)



**Problem:** Build a min-heap from `[5, 3, 8, 1, 6]`. Show how to read the minimum element without removing it. Then show what changes if you use `heappop` instead of `heap[0]`.

<details>
<summary>💡 Hint</summary>

`heap[0]` is O(1) and does not modify the heap. `heappop` is O(log n) and removes the minimum. They are not interchangeable.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

h = [5, 3, 8, 1, 6]
heapq.heapify(h)

# Peek — O(1), heap unchanged
min_val = h[0]
print(f"Min: {min_val}, heap size still: {len(h)}")   # 1, size=5

# Pop — O(log n), removes minimum
popped = heapq.heappop(h)
print(f"Popped: {popped}, heap size now: {len(h)}")   # 1, size=4

assert min_val == popped   # both give 1, but pop changed the heap
```

**Why:** Peek (`heap[0]`) is a read-only O(1) operation — the heap structure is untouched. Pop is a destructive O(log n) operation that removes the root and re-heapifies. Using pop when you only need to inspect the minimum is a common mistake that silently destroys data.

**Time:** Peek O(1), Pop O(log n). **Space:** O(1).
</details>

---

<a id="q8"></a>
### Q8 🟢 · Heap sort

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)



**Problem:** Implement `heap_sort(arr: list[int]) -> list[int]` using only `heapq` operations. Do not use Python's built-in `sorted()`. Test on `[5, 3, 8, 1, 9, 2, 7, 4, 6]`.

<details>
<summary>💡 Hint</summary>

heapify the array in O(n), then repeatedly `heappop` to extract elements in ascending order. Each pop is O(log n), so total extraction is O(n log n).
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

def heap_sort(arr):
    h = arr[:]           # copy to avoid mutating input
    heapq.heapify(h)     # O(n)
    return [heapq.heappop(h) for _ in range(len(h))]   # O(n log n)

result = heap_sort([5, 3, 8, 1, 9, 2, 7, 4, 6])
print(result)   # [1, 2, 3, 4, 5, 6, 7, 8, 9]
assert result == list(range(1, 10))
```

**Why:** heapify rearranges the array into a valid min-heap in O(n). Each heappop always extracts the current minimum, so successive pops produce the fully sorted sequence. Total time is O(n) + O(n log n) = O(n log n). Heap sort is not stable (equal elements may reorder) and is rarely used in practice versus Timsort, but it demonstrates the heap's sorting capability.

**Time:** O(n log n). **Space:** O(n) for the copy.
</details>

---

<a id="q9"></a>
### Q9 🟡 · Kth largest element

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)



**Problem:** Given `nums = [3, 2, 1, 5, 6, 4]` and `k = 2`, find the 2nd largest element. Implement using a min-heap of size k. Expected output: `5`.

<details>
<summary>💡 Hint</summary>

Maintain a min-heap of exactly k elements. As you scan: push every new element, then if the heap exceeds size k, pop the minimum. When done, `heap[0]` is the kth largest — it is the smallest of the top-k.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

def find_kth_largest(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)   # evict the weakest of current top-k
    return heap[0]   # smallest of the top-k = kth largest overall

print(find_kth_largest([3, 2, 1, 5, 6, 4], 2))   # 5
print(find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))   # 4
```

**Why:** A min-heap of size k always keeps the k largest elements seen so far. The root is the smallest of those k elements — which is exactly the kth largest. The heap "evicts" any smaller element that loses its spot in the top-k. This is O(n log k) vs O(n log n) for sorting.

**Time:** O(n log k). **Space:** O(k).
</details>

---

<a id="q10"></a>
### Q10 🟡 · Kth smallest element

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)



**Problem:** Given `nums = [7, 10, 4, 3, 20, 15]` and `k = 3`, find the 3rd smallest element. Expected: `7`. Use a max-heap of size k (via negation).

<details>
<summary>💡 Hint</summary>

Mirror of Q9 but flipped. Maintain a max-heap of size k (negate values). The root of the max-heap is the largest of the bottom-k — which is the kth smallest.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

def find_kth_smallest(nums, k):
    max_heap = []
    for num in nums:
        heapq.heappush(max_heap, -num)   # negate for max-heap
        if len(max_heap) > k:
            heapq.heappop(max_heap)      # evict the largest of bottom-k
    return -max_heap[0]   # un-negate: largest of bottom-k = kth smallest

print(find_kth_smallest([7, 10, 4, 3, 20, 15], 3))   # 7
print(find_kth_smallest([1, 2, 3], 1))                # 1
```

**Why:** The max-heap of size k holds the k smallest elements seen so far. Its root (the maximum of those k) is the kth smallest overall. When a new element arrives that is smaller than the current kth smallest, it pushes the previous kth out. Negation is the standard Python pattern for simulating max-heaps.

**Time:** O(n log k). **Space:** O(k).
</details>

---

<a id="q11"></a>
### Q11 🟡 · Top-K largest elements

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)



**Problem:** Given `nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]` and `k = 4`, return the 4 largest values (any order). Expected: `{5, 5, 6, 9}`. Implement with a min-heap of size k and compare to `heapq.nlargest`.

<details>
<summary>💡 Hint</summary>

The approach is identical to Q9, but you return the whole heap instead of just the root. `heapq.nlargest(k, nums)` gives the same result as a shortcut.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

def top_k_largest(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted(heap, reverse=True)

nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
print(top_k_largest(nums, 4))          # [9, 6, 5, 5]
print(heapq.nlargest(4, nums))         # [9, 6, 5, 5]  ← same result
```

**Why:** The min-heap of size k acts as a "gate": only elements larger than the current weakest top-k candidate can enter. The heap never grows beyond k elements, so memory usage is O(k) regardless of n. For k << n this is much faster than sorting everything.

**Time:** O(n log k). **Space:** O(k).
</details>

---

<a id="q12"></a>
### Q12 🟡 · Top-K most frequent elements

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)



**Problem:** Given `nums = [1, 1, 1, 2, 2, 3]` and `k = 2`, return the 2 most frequent elements. Expected: `[1, 2]`. Use `Counter` for frequencies and a min-heap of size k on `(frequency, value)` pairs.

<details>
<summary>💡 Hint</summary>

Count frequencies with `Counter`. Then use a min-heap of size k where each entry is `(count, value)`. The heap evicts the least frequent element, keeping the k most frequent.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq
from collections import Counter

def top_k_frequent(nums, k):
    freq = Counter(nums)
    heap = []
    for val, count in freq.items():
        heapq.heappush(heap, (count, val))
        if len(heap) > k:
            heapq.heappop(heap)   # evict least frequent
    return [val for count, val in heap]

print(top_k_frequent([1, 1, 1, 2, 2, 3], 2))    # [1, 2]
print(top_k_frequent([1], 1))                    # [1]
```

**Why:** We push `(count, value)` tuples so the heap compares by frequency first. The min-heap of size k keeps the k most frequent elements — anything with a lower frequency gets evicted. Counter gives frequencies in O(n); the heap pass is O(m log k) where m = unique elements.

**Time:** O(n + m log k) where m = unique elements. **Space:** O(m + k).
</details>

---

<a id="q13"></a>
### Q13 🟡 · Merge K sorted lists

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)



**Problem:** Given `lists = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]`, merge all lists into one sorted list using a min-heap. Expected: `[1, 2, 3, 4, 5, 6, 7, 8, 9]`.

<details>
<summary>💡 Hint</summary>

Seed the heap with the first element from each list as `(value, list_index, element_index)`. Each pop advances to the next element in that same list. The heap always holds at most k elements — one per list.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

def merge_k_sorted_lists(lists):
    result = []
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))   # (value, list_idx, elem_idx)

    while heap:
        val, i, j = heapq.heappop(heap)
        result.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))

    return result

print(merge_k_sorted_lists([[1, 4, 7], [2, 5, 8], [3, 6, 9]]))
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

**Why:** At every step, the heap's root is the globally smallest element not yet added to the result. We always advance the pointer in the same list we just consumed from, keeping the heap at most size k. The tuple `(value, list_idx, elem_idx)` gives the heap enough information to find the next element. Adding `list_idx` as tiebreaker prevents `TypeError` when values are equal.

**Time:** O(N log k) where N = total elements. **Space:** O(k).
</details>

---

<a id="q14"></a>
### Q14 🟡 · K closest points to origin

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)



**Problem:** Given `points = [[1, 3], [-2, 2], [5, 8], [0, 1]]` and `k = 2`, return the 2 closest points to the origin `(0,0)` by Euclidean distance. Expected: `[[-2, 2], [0, 1]]` (order not required).

<details>
<summary>💡 Hint</summary>

Use a max-heap of size k storing `(-distance_squared, point)`. The root is the farthest of the current k candidates. When a closer point arrives, it displaces the farthest.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

def k_closest_points(points, k):
    max_heap = []   # (-dist_sq, point)
    for x, y in points:
        dist_sq = x * x + y * y
        heapq.heappush(max_heap, (-dist_sq, [x, y]))
        if len(max_heap) > k:
            heapq.heappop(max_heap)   # evict the farthest
    return [pt for _, pt in max_heap]

result = sorted(k_closest_points([[1, 3], [-2, 2], [5, 8], [0, 1]], 2))
print(result)   # [[-2, 2], [0, 1]]
```

**Why:** This is the mirror of top-k largest. To find the k *smallest* distances, maintain a max-heap of size k. The root is the largest (farthest) of the current candidates — when a point arrives that is closer, it evicts the farthest. We skip `sqrt` because distance ordering is preserved under squaring.

**Time:** O(n log k). **Space:** O(k).
</details>

---

<a id="q15"></a>
### Q15 🟡 · Task scheduler with cooldown

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)



**Problem:** Given `tasks = ["A","A","A","B","B","B"]` and cooldown `n = 2`, find the minimum CPU intervals to finish all tasks. The same task can't run again within `n` intervals. Expected: `8`.

<details>
<summary>💡 Hint</summary>

Use a max-heap of task frequencies. Always run the most frequent available task. Track cooling tasks in a deque as `(available_at_time, neg_freq)`. When the heap is empty but the cooldown queue is not, idle until the next task is ready.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq
from collections import Counter, deque

def least_interval(tasks, n):
    count = Counter(tasks)
    max_heap = [-freq for freq in count.values()]
    heapq.heapify(max_heap)

    time = 0
    cooldown = deque()   # (available_at, neg_freq)

    while max_heap or cooldown:
        time += 1
        if max_heap:
            freq = heapq.heappop(max_heap) + 1   # use one instance
            if freq < 0:                          # still has remaining runs
                cooldown.append((time + n, freq))
        else:
            time = cooldown[0][0]   # idle: jump to next available task

        if cooldown and cooldown[0][0] <= time:
            _, freq = cooldown.popleft()
            heapq.heappush(max_heap, freq)

    return time

print(least_interval(["A","A","A","B","B","B"], 2))   # 8
print(least_interval(["A","A","A","B","B","B"], 0))   # 6
```

**Why:** Greedy insight — always schedule the most frequent remaining task first. This minimizes idle time because the task most likely to cause bottlenecks is tackled immediately. The max-heap gives O(log k) access to the most frequent task; the deque manages the cooldown window in FIFO order.

**Time:** O(T log k) where T = total tasks, k = unique task types. **Space:** O(k).
</details>

---

<a id="q16"></a>
### Q16 🟡 · When heap beats sorted array

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)



**Problem:** Write a function `benchmark_heap_vs_sort(n, k)` that compares the time to find the top-k largest elements using (a) `sorted()` and (b) `heapq.nlargest()`. Run it for `n=1_000_000, k=10`. Print both times and explain when you'd choose each approach.

<details>
<summary>💡 Hint</summary>

Use `time.perf_counter()` for timing. Repeat each approach 3 times and take the minimum to reduce noise. Heap wins when k << n; sort wins when k is close to n.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq, time, random

def benchmark_heap_vs_sort(n, k):
    data = [random.randint(1, 10**9) for _ in range(n)]

    t0 = time.perf_counter()
    sort_result = sorted(data, reverse=True)[:k]
    sort_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    heap_result = heapq.nlargest(k, data)
    heap_time = time.perf_counter() - t0

    print(f"sort: {sort_time:.3f}s | heap: {heap_time:.3f}s")
    assert sort_result == heap_result
    return sort_time, heap_time

benchmark_heap_vs_sort(1_000_000, 10)
# heap is typically 5-10x faster for k=10, n=1M
```

**Why:** `sorted()` is always O(n log n) regardless of k. `heapq.nlargest` uses a min-heap of size k — O(n log k). When k=10 and n=1,000,000, that's `log(10) ≈ 3.3` vs `log(1,000,000) ≈ 20` operations per element — a 6x theoretical speedup. When k approaches n (e.g. k=500,000, n=1,000,000), sort is comparable or faster due to lower constant factors.

**Time:** Sort O(n log n), Heap O(n log k). **Space:** O(n) sort, O(k) heap.
</details>

---

<a id="q17"></a>
### Q17 🟡 · Sliding window maximum — heap approach

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)



**Problem:** Given `nums = [1, 3, -1, -3, 5, 3, 6, 7]` and `k = 3`, return the maximum of each sliding window. Expected: `[3, 3, 5, 5, 6, 7]`. Use a max-heap with lazy deletion.

<details>
<summary>💡 Hint</summary>

Push `(-value, index)` onto a max-heap. Before recording the window maximum, pop any entries whose index has fallen outside the current window `[i-k+1, i]`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

def max_sliding_window(nums, k):
    heap = []   # (-val, index)
    result = []
    for i, val in enumerate(nums):
        heapq.heappush(heap, (-val, i))
        # Lazy delete: skip entries outside window
        while heap[0][1] < i - k + 1:
            heapq.heappop(heap)
        if i >= k - 1:
            result.append(-heap[0][0])
    return result

print(max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3))
# [3, 3, 5, 5, 6, 7]
```

**Why:** We cannot remove arbitrary elements from a heap efficiently, so we use "lazy deletion" — only evict an element when it reaches the top and we discover its index is stale. The index stored alongside the value tells us whether the element is still inside the current window. Note: a monotonic deque achieves O(n) for this problem; the heap approach is O(n log n) but simpler to remember.

**Time:** O(n log n). **Space:** O(n).
</details>

---

<a id="q18"></a>
### Q18 🟡 · Heap as priority queue

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)



**Problem:** Design a `PriorityQueue` class with `push(priority, item)`, `pop()` (returns item with lowest priority number first), and `peek()`. Use a counter to break ties so no `TypeError` occurs when priorities are equal.

<details>
<summary>💡 Hint</summary>

Store tuples `(priority, counter, item)` in the heap. The counter is a monotonically increasing integer from `itertools.count()`. Since counter is always unique, Python never needs to compare the `item` field.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq, itertools

class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._counter = itertools.count()

    def push(self, priority, item):
        heapq.heappush(self._heap, (priority, next(self._counter), item))

    def pop(self):
        _, _, item = heapq.heappop(self._heap)
        return item

    def peek(self):
        if self._heap:
            return self._heap[0][2]   # item field
        return None

    def __len__(self):
        return len(self._heap)

pq = PriorityQueue()
pq.push(3, "low")
pq.push(1, "high")
pq.push(2, "medium")
print(pq.pop())   # "high"
print(pq.pop())   # "medium"
print(pq.pop())   # "low"
```

**Why:** The `(priority, counter, item)` tuple is the canonical Python priority queue pattern. Without the counter, if two items share the same priority, Python tries to compare the `item` field and crashes with `TypeError` if items are non-comparable (dicts, custom objects). The counter guarantees uniqueness so the comparison never reaches `item`.

**Time:** push/pop O(log n), peek O(1). **Space:** O(n).
</details>

---

<a id="q19"></a>
### Q19 🟡 · Tuple tiebreaker for non-comparable items

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)



**Problem:** Show that `heapq.heappush(h, (1, {"name": "a"}))` followed by `heapq.heappush(h, (1, {"name": "b"}))` raises `TypeError`. Then fix it with a counter tiebreaker.

<details>
<summary>💡 Hint</summary>

Python compares tuple elements left to right. If the first elements are equal (both priority=1), it tries to compare the second elements (the dicts). Dicts do not support `<`, so Python raises `TypeError`. A unique counter as the second element prevents the comparison from reaching the dict.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq, itertools

# Broken — crashes when priorities tie
h_broken = []
try:
    heapq.heappush(h_broken, (1, {"name": "a"}))
    heapq.heappush(h_broken, (1, {"name": "b"}))   # TypeError!
    heapq.heappop(h_broken)
except TypeError as e:
    print(f"Error: {e}")

# Fixed — counter prevents dict comparison
h_fixed = []
counter = itertools.count()
heapq.heappush(h_fixed, (1, next(counter), {"name": "a"}))
heapq.heappush(h_fixed, (1, next(counter), {"name": "b"}))
_, _, item = heapq.heappop(h_fixed)
print(item)   # {"name": "a"}  — same priority, FIFO order
```

**Why:** Python compares tuples lexicographically. With `(priority, item)`, equal priorities force a comparison of `item`. Dicts, lists, and custom objects without `__lt__` all crash. The `itertools.count()` counter is always unique and comparable, so Python never reaches the third element.

**Time:** push/pop O(log n). **Space:** O(1) overhead.
</details>

---

<a id="q20"></a>
### Q20 🟡 · heapify in loop — O(n²) mistake

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)



**Problem:** Show why calling `heapq.heapify()` inside a for loop is an O(n²) mistake. Write the broken version and the correct fix using `heapq.heappush()` for streaming data.

<details>
<summary>💡 Hint</summary>

`heapify` is designed for a fully-populated list — it does O(n) work. If you call it after every append in a loop of n elements, you do O(1) + O(2) + ... + O(n) = O(n²) total work.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq, time, random

data = list(range(50_000))
random.shuffle(data)

# WRONG — O(n^2): heapify re-scans entire heap on every iteration
def build_heap_wrong(stream):
    heap = []
    for item in stream:
        heap.append(item)
        heapq.heapify(heap)   # O(len(heap)) every time
    return heap

# CORRECT — O(n log n): heappush is O(log n) per element
def build_heap_correct(stream):
    heap = []
    for item in stream:
        heapq.heappush(heap, item)   # O(log n) each
    return heap

# BEST — O(n): heapify once after all data is collected
def build_heap_best(data):
    heap = list(data)
    heapq.heapify(heap)   # O(n) single pass
    return heap

t0 = time.perf_counter()
h1 = build_heap_correct(data)
print(f"heappush loop: {time.perf_counter()-t0:.3f}s")

t0 = time.perf_counter()
h2 = build_heap_best(data)
print(f"heapify once:  {time.perf_counter()-t0:.3f}s")

assert h1[0] == h2[0] == 0
```

**Why:** `heapify` is a batch operation meant for a static list. Using it after each insertion is like re-sorting the whole array after every push. `heappush` is the correct streaming tool: O(log n) per insert. If you have all the data up front, `heapify` once is optimal at O(n).

**Time:** Wrong O(n²), heappush loop O(n log n), heapify once O(n). **Space:** O(n).
</details>

---

<a id="q21"></a>
### Q21 🔴 · Median of data stream — two heaps

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)



**Problem:** Design a `MedianFinder` class that supports `add_num(num)` in O(log n) and `find_median()` in O(1). Use two heaps: a max-heap for the lower half and a min-heap for the upper half.

Test sequence: add `[5, 10, 1, 4, 8]` one at a time and print the running median after each insertion.

<details>
<summary>💡 Hint</summary>

Invariant 1 (order): every element in `low` (max-heap) ≤ every element in `high` (min-heap). Invariant 2 (size): `len(low) == len(high)` or `len(low) == len(high) + 1`. The median is `low[0]` when sizes differ, else the average of both tops.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.low  = []   # max-heap (negated) — lower half
        self.high = []   # min-heap — upper half

    def add_num(self, num):
        heapq.heappush(self.low, -num)   # always push to lower half first

        # Fix order: max of low must be <= min of high
        if self.high and (-self.low[0]) > self.high[0]:
            heapq.heappush(self.high, -heapq.heappop(self.low))

        # Fix size: low can have at most 1 more element
        if len(self.low) > len(self.high) + 1:
            heapq.heappush(self.high, -heapq.heappop(self.low))
        elif len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def find_median(self):
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0

mf = MedianFinder()
for num in [5, 10, 1, 4, 8]:
    mf.add_num(num)
    print(f"added {num} → median = {mf.find_median()}")
# 5.0 → 7.5 → 5.0 → 4.5 → 5.0
```

**Why:** The sorted stream splits cleanly at the median boundary. The max-heap top (largest of the lower half) and min-heap top (smallest of the upper half) are always the two candidates for the median. By keeping the heaps size-balanced (differing by at most 1), the median is always available at the tops in O(1).

**Time:** add O(log n), find_median O(1). **Space:** O(n).
</details>

---

<a id="q22"></a>
### Q22 🔴 · Sliding median with lazy deletion

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)



**Problem:** Given `nums = [1, 3, -1, -3, 5, 3, 6, 7]` and `k = 3`, compute the median of each sliding window. Expected: `[1.0, -1.0, -1.0, 3.0, 5.0, 6.0]`.

Extend the two-heap `MedianFinder` with a `remove_num` method that uses lazy deletion and a virtual-size counter.

<details>
<summary>💡 Hint</summary>

When removing, increment a `to_remove` counter for that value. Before reading the top of either heap, purge any elements that are marked for removal. Track `low_size` and `high_size` separately from the actual heap lengths so balance checks stay correct.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq
from collections import defaultdict

class SlidingMedianFinder:
    def __init__(self):
        self.low  = []
        self.high = []
        self.to_remove = defaultdict(int)
        self.low_size  = 0
        self.high_size = 0

    def _purge_low(self):
        while self.low and self.to_remove[-self.low[0]] > 0:
            self.to_remove[-self.low[0]] -= 1
            heapq.heappop(self.low)

    def _purge_high(self):
        while self.high and self.to_remove[self.high[0]] > 0:
            self.to_remove[self.high[0]] -= 1
            heapq.heappop(self.high)

    def add_num(self, num):
        if not self.low or num <= -self.low[0]:
            heapq.heappush(self.low, -num)
            self.low_size += 1
        else:
            heapq.heappush(self.high, num)
            self.high_size += 1
        self._rebalance()

    def remove_num(self, num):
        self.to_remove[num] += 1
        if num <= -self.low[0]:
            self.low_size -= 1
        else:
            self.high_size -= 1
        self._rebalance()

    def _rebalance(self):
        if self.low_size > self.high_size + 1:
            self._purge_low()
            self.high_size += 1
            heapq.heappush(self.high, -heapq.heappop(self.low))
            self.low_size -= 1
        elif self.high_size > self.low_size:
            self._purge_high()
            self.low_size += 1
            heapq.heappush(self.low, -heapq.heappop(self.high))
            self.high_size -= 1

    def find_median(self):
        self._purge_low()
        self._purge_high()
        if self.low_size > self.high_size:
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0

def sliding_median(nums, k):
    mf = SlidingMedianFinder()
    result = []
    for i, num in enumerate(nums):
        mf.add_num(num)
        if i >= k - 1:
            result.append(mf.find_median())
            mf.remove_num(nums[i - k + 1])
    return result

print(sliding_median([1, 3, -1, -3, 5, 3, 6, 7], 3))
# [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]
```

**Why:** Lazy deletion avoids the O(n) cost of finding and removing an arbitrary element from a heap. By tracking a separate "virtual size" that decrements on removal, the balance invariant stays correct even when stale entries remain physically in the heap. Elements are only truly removed when they bubble to the top and are matched against the `to_remove` map.

**Time:** add/remove O(log n) amortized, find_median O(log n) worst case. **Space:** O(n).
</details>

---

<a id="q23"></a>
### Q23 🔴 · Reorganize string — greedy max-heap

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)



**Problem:** Given a string `s`, rearrange its characters so no two adjacent characters are the same. Return any valid arrangement, or `""` if impossible. Example: `"aab"` → `"aba"`, `"aaab"` → `""`.

<details>
<summary>💡 Hint</summary>

Use a max-heap of `(-count, char)` pairs. At each step, pop the most frequent character. If it equals the last placed character, pop the second most frequent instead and push the first back. If the heap is empty at that point, return `""`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq
from collections import Counter

def reorganize_string(s):
    freq = Counter(s)
    max_heap = [(-count, ch) for ch, count in freq.items()]
    heapq.heapify(max_heap)

    result = []
    prev_count, prev_char = 0, ""

    while max_heap:
        count, ch = heapq.heappop(max_heap)
        result.append(ch)
        # Push back the character we held from last round
        if prev_count < 0:
            heapq.heappush(max_heap, (prev_count, prev_char))
        # Hold current character for next round (can't place same twice)
        prev_count, prev_char = count + 1, ch   # count + 1 because it's negative

    return "".join(result) if len(result) == len(s) else ""

print(reorganize_string("aab"))    # "aba"
print(reorganize_string("aaab"))   # ""
print(reorganize_string("vvvlo"))  # "vlvov" or similar
```

**Why:** The greedy strategy of always placing the most frequent remaining character minimizes the chance of two identical characters becoming adjacent. After placing a character, it is temporarily "held" for one cycle (cooldown of 1) before being eligible again. If the most frequent character has count > ceil(n/2), it is impossible to avoid adjacency.

**Time:** O(n log k) where k = unique characters. **Space:** O(k).
</details>

---

<a id="q24"></a>
### Q24 🔴 · Median stream with remove support

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)



**Problem:** Design a `DynamicMedianFinder` supporting `add_num(num)`, `remove_num(num)`, and `find_median()`. Demonstrate it with: add `[1, 2, 3, 4, 5]`, then remove `3`, then find the median (should be `2.5`).

<details>
<summary>💡 Hint</summary>

This is a direct application of the lazy deletion technique from Q22. The key insight: when you call `remove_num`, you don't need to find where the element is in the heap. You just record the intent in a `to_remove` map and let elements be purged lazily when they reach the top.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq
from collections import defaultdict

class DynamicMedianFinder:
    """Supports add, remove, and O(1) median with lazy deletion."""

    def __init__(self):
        self.low  = []   # max-heap (negated)
        self.high = []   # min-heap
        self.to_remove = defaultdict(int)
        self.low_size = self.high_size = 0

    def _purge(self, heap, sign):
        """Remove marked elements from heap top. sign=1 for high, -1 for low."""
        while heap and self.to_remove[sign * heap[0]] > 0:
            self.to_remove[sign * heap[0]] -= 1
            heapq.heappop(heap)

    def add_num(self, num):
        if not self.low or num <= -self.low[0]:
            heapq.heappush(self.low, -num); self.low_size += 1
        else:
            heapq.heappush(self.high, num); self.high_size += 1
        self._balance()

    def remove_num(self, num):
        self.to_remove[num] += 1
        if num <= -self.low[0]:
            self.low_size -= 1
        else:
            self.high_size -= 1
        self._balance()

    def _balance(self):
        if self.low_size > self.high_size + 1:
            self._purge(self.low, -1)
            heapq.heappush(self.high, -heapq.heappop(self.low))
            self.low_size -= 1; self.high_size += 1
        elif self.high_size > self.low_size:
            self._purge(self.high, 1)
            heapq.heappush(self.low, -heapq.heappop(self.high))
            self.high_size -= 1; self.low_size += 1

    def find_median(self):
        self._purge(self.low, -1); self._purge(self.high, 1)
        if self.low_size > self.high_size:
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0

dmf = DynamicMedianFinder()
for n in [1, 2, 3, 4, 5]:
    dmf.add_num(n)
print(f"Median of [1,2,3,4,5]: {dmf.find_median()}")   # 3.0
dmf.remove_num(3)
print(f"After removing 3:      {dmf.find_median()}")   # 2.5
```

**Why:** Heaps do not support efficient removal of arbitrary elements. Lazy deletion is the standard workaround: mark an element as "to be removed" and only pay the O(log n) cost of cleaning it up when it naturally reaches the top. This avoids an O(n) linear search through the heap. The virtual size counters ensure the balance invariant is maintained correctly even when stale elements lurk inside the heap.

**Time:** add/remove O(log n) amortized, find_median O(log n) worst case. **Space:** O(n).
</details>

---

<a id="q25"></a>
### Q25 🔴 · Design a streaming top-K tracker

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)



**Problem:** Design a `TopKTracker(k)` class that processes a stream of `(item, score)` pairs and always answers "what are the current top-k items by score?" in O(log k) per update and O(k) per query. Items can be updated (their scores can increase).

Test: track top-3 from the stream `[("a",5), ("b",3), ("c",7), ("d",2), ("a",9), ("b",8)]`. Expected top-3: `[("a",9), ("b",8), ("c",7)]`.

<details>
<summary>💡 Hint</summary>

Maintain a `scores` dict for O(1) score lookup and a min-heap of `(score, item)` pairs of size k. When an item is re-inserted with a higher score, add the new entry and mark the old entry for lazy deletion using a `stale` set keyed by `(old_score, item)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

class TopKTracker:
    def __init__(self, k):
        self.k = k
        self.heap = []       # min-heap of (score, item) — smallest score at top
        self.scores = {}     # item -> current best score
        self.stale = {}      # (score, item) -> True if this entry is outdated

    def update(self, item, score):
        if item in self.scores:
            old_score = self.scores[item]
            if score <= old_score:
                return   # no improvement
            self.stale[(old_score, item)] = True   # mark old entry stale

        self.scores[item] = score
        heapq.heappush(self.heap, (score, item))

        # Evict stale entries from the top before trimming
        while self.heap and self.stale.get((self.heap[0][0], self.heap[0][1])):
            entry = heapq.heappop(self.heap)
            del self.stale[(entry[0], entry[1])]

        # Keep heap size <= k
        if len(self.heap) > self.k:
            evicted = heapq.heappop(self.heap)
            # If the evicted item has no better entry, remove from scores
            if self.scores.get(evicted[1]) == evicted[0]:
                del self.scores[evicted[1]]

    def top_k(self):
        # Rebuild clean snapshot — heap may contain stale entries inside
        clean = [(s, i) for s, i in self.heap
                 if not self.stale.get((s, i))]
        return sorted(clean, reverse=True)[:self.k]

tracker = TopKTracker(3)
for item, score in [("a",5), ("b",3), ("c",7), ("d",2), ("a",9), ("b",8)]:
    tracker.update(item, score)

print(tracker.top_k())
# [(9, 'a'), (8, 'b'), (7, 'c')]
```

**Why:** Real streaming systems (Twitter trending, live leaderboards) must handle score updates efficiently. A naive approach rebuilds the whole heap on every update — O(n log n). Lazy deletion with a stale-entry map lets us push the updated entry in O(log k) and defer cleanup. The min-heap's root is always the weakest top-k candidate, making admission/eviction O(log k).

**Time:** update O(log k) amortized, top_k O(k log k). **Space:** O(n) for scores dict, O(k) for heap.
</details>

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Trie — Theory →](../17_trie/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
