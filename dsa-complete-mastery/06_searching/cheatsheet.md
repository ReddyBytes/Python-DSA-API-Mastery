## SEARCHING — QUICK REFERENCE CHEATSHEET

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LINEAR vs BINARY SEARCH                              │
├──────────────────┬──────────────────┬──────────────────────────────────┤
│ Property         │ Linear Search    │ Binary Search                    │
├──────────────────┼──────────────────┼──────────────────────────────────┤
│ Time (best)      │ O(1)             │ O(1)                             │
│ Time (avg/worst) │ O(n)             │ O(log n)                         │
│ Space            │ O(1)             │ O(1) iter / O(log n) recursive   │
│ Requires sorted  │ No               │ YES — mandatory                  │
│ Works on         │ Any iterable     │ Random-access array only         │
│ Implementation   │ Trivial          │ Off-by-one prone                 │
└──────────────────┴──────────────────┴──────────────────────────────────┘
```

---

## BINARY SEARCH — THREE TEMPLATES

### Template 1: Standard (find exact target)
```python
def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:                      # <= because hi is inclusive
        mid = lo + (hi - lo) // 2       # NEVER use (lo+hi)//2 — overflow risk
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1                            # not found
```

### Template 2: Left-most (first occurrence / lower bound)
```python
def lower_bound(nums, target):
    lo, hi = 0, len(nums)               # hi = len(nums), NOT len-1
    while lo < hi:                       # strict < because hi is exclusive
        mid = lo + (hi - lo) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid                     # shrink right; don't exclude mid yet
    return lo                            # insertion point; check nums[lo]==target
```

### Template 3: Right-most (last occurrence / upper bound)
```python
def upper_bound(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] <= target:          # <= moves lo past equal elements
            lo = mid + 1
        else:
            hi = mid
    return lo - 1                        # last position of target (if exists)
```

---

## BISECT MODULE (USE IN INTERVIEWS — BUILT-IN)

```python
import bisect

nums = [1, 3, 3, 5, 7]

bisect.bisect_left(nums, 3)   # → 1  (first index where 3 can be inserted)
bisect.bisect_right(nums, 3)  # → 3  (index after last 3)
bisect.insort(nums, 4)        # inserts 4 in-place, keeping sorted order O(n)

# Existence check
idx = bisect.bisect_left(nums, target)
found = idx < len(nums) and nums[idx] == target

# Count occurrences
count = bisect.bisect_right(nums, x) - bisect.bisect_left(nums, x)
```

```
┌─────────────────────────────────────────────────────────────┐
│  bisect_left  → left insertion point  (like lower_bound)    │
│  bisect_right → right insertion point (like upper_bound)    │
│  Both run in O(log n)                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## WHEN TO USE BINARY SEARCH

```
✓ Array is sorted (or rotatable to sorted)
✓ Question asks for O(log n) on a search
✓ "Find minimum/maximum X such that condition(X) is True"
✓ Monotonic function: F(x) is all-False then all-True (or vice versa)
✓ Search space is reducible by half each step
✓ Answer lies in a known numeric range (binary search on answer)
```

---

## BINARY SEARCH ON ANSWER — TEMPLATE

```python
# Pattern: minimize/maximize a value subject to a feasibility constraint
# "Find the minimum X such that feasible(X) == True"

def solve():
    lo, hi = MIN_POSSIBLE, MAX_POSSIBLE

    def feasible(mid):
        # return True if condition is satisfiable with value = mid
        pass

    while lo < hi:
        mid = lo + (hi - lo) // 2
        if feasible(mid):
            hi = mid        # try smaller (minimize)
        else:
            lo = mid + 1
    return lo               # smallest feasible value
```

**Classic examples:** Koko Eating Bananas, Minimum Days to Make Bouquets,
Split Array Largest Sum, Capacity to Ship Packages.

---

## INTERVIEW PATTERNS

### Find First and Last Occurrence
```python
def search_range(nums, target):
    def first(nums, t):
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = lo + (hi - lo) // 2
            if nums[mid] < t: lo = mid + 1
            else: hi = mid
        return lo if lo < len(nums) and nums[lo] == t else -1

    def last(nums, t):
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = lo + (hi - lo) // 2
            if nums[mid] <= t: lo = mid + 1
            else: hi = mid
        return lo - 1 if lo > 0 and nums[lo-1] == t else -1

    return [first(nums, target), last(nums, target)]
```

### Rotated Sorted Array
```python
def search_rotated(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target: return mid
        if nums[lo] <= nums[mid]:            # left half sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                # right half sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```

### Find Peak Element
```python
def find_peak(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1       # ascending → peak is to the right
        else:
            hi = mid           # descending → peak is here or to the left
    return lo
```

---

## COMMON MISTAKES / GOTCHAS

```
TRAP 1: Mid overflow
  BAD:  mid = (lo + hi) // 2       ← can overflow in other languages
  GOOD: mid = lo + (hi - lo) // 2

TRAP 2: Infinite loop with lo < hi
  Ensure lo or hi always moves: use mid+1 / mid-1 correctly.
  If feasible(mid) → hi = mid (not mid-1) when using exclusive upper bound.

TRAP 3: Wrong boundary for lower/upper bound
  lower_bound: hi = len(nums), loop condition lo < hi
  standard:    hi = len(nums)-1, loop condition lo <= hi

TRAP 4: Forgetting to validate index after bisect_left
  idx = bisect_left(nums, target)
  MUST check: idx < len(nums) and nums[idx] == target

TRAP 5: Applying binary search to unsorted data
  Sorting + binary search = O(n log n) — may not beat linear O(n).
```

---

## COMPLEXITY SUMMARY

```
┌──────────────────────────┬────────────┬───────────┐
│ Operation                │ Time       │ Space     │
├──────────────────────────┼────────────┼───────────┤
│ Binary search (iter)     │ O(log n)   │ O(1)      │
│ Binary search (recur)    │ O(log n)   │ O(log n)  │
│ bisect_left / right      │ O(log n)   │ O(1)      │
│ insort                   │ O(n)       │ O(1)      │
│ Binary search on answer  │ O(log R·f) │ O(1)      │
│   R = range, f = check   │            │           │
└──────────────────────────┴────────────┴───────────┘
```
