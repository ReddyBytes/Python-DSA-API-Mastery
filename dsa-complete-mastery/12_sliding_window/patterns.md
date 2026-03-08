# Sliding Window — Pattern Recognition Guide

> **Core Idea**: Maintain a "window" (contiguous subarray/substring) and slide it across the
> input, expanding or shrinking one element at a time. Avoids recomputing from scratch each step.
> Reduces brute-force O(n²) or O(n³) to O(n).

---

## 1. Pattern Recognition Signals

When you see these features, think "sliding window":

| Signal | Example Phrasing |
|--------|-----------------|
| Contiguous subarray or substring | "Find subarray where…" |
| Longest / shortest with a constraint | "Longest substring without repeating characters" |
| Exactly k elements in window | "Window of size k", "k consecutive" |
| Contains / covers a set | "Minimum window containing all characters of t" |
| Frequency / count within range | "At most k distinct characters" |
| Maximum / minimum of each window | "Sliding window maximum" |

**Anti-signals** (sliding window will not work):
- Non-contiguous elements (use DP or backtracking)
- The "window" can skip elements
- Need to find global pairs (use two pointers or hash map)

**Decision rule**:
```
Is the answer a contiguous subarray/substring?
  → Yes: sliding window
  → No:  two pointers, DP, or hash map
```

---

## 2. Pattern 1: Fixed Window

**Mental model**: Window size `k` never changes. Slide by removing leftmost, adding rightmost.
Compute answer for each window position in O(1) using previously computed window state.

**When to use**:
- "Find max/min/sum of every subarray of length k"
- "First negative number in each window of size k"
- "Average of all subarrays of size k"

### Template

```python
def fixed_window(arr, k):
    n = len(arr)
    if n < k:
        return []

    # --- Build first window ---
    window_state = initial_state(arr[:k])   # e.g., sum(arr[:k])
    result = [window_state]

    # --- Slide window ---
    for i in range(k, n):
        window_state = update(window_state, arr[i], arr[i - k])
        #                                   ^ add new  ^ remove old (left boundary)
        result.append(window_state)

    return result
```

**The key insight**: `update()` is O(1). You are adding one element and removing one element,
not recomputing the entire window.

---

### Worked Example 1: Maximum Sum of K Consecutive Elements

```python
def max_sum_k(arr, k):
    n = len(arr)

    # Build first window
    window_sum = sum(arr[:k])
    max_sum = window_sum

    # Slide: add arr[i], remove arr[i-k]
    for i in range(k, n):
        window_sum += arr[i] - arr[i - k]
        max_sum = max(max_sum, window_sum)

    return max_sum

# Trace: arr=[2,1,5,1,3,2], k=3
# First window [2,1,5] → sum=8
# i=3: sum = 8 + 1 - 2 = 7   (add arr[3]=1, remove arr[0]=2)
# i=4: sum = 7 + 3 - 1 = 9   (add arr[4]=3, remove arr[1]=1)
# i=5: sum = 9 + 2 - 5 = 6   (add arr[5]=2, remove arr[2]=5)
# max_sum = 9
```

---

### Worked Example 2: First Negative in Each Window of Size K

```python
from collections import deque

def first_negative_window(arr, k):
    negatives = deque()  # stores indices of negative numbers in current window
    result = []

    for i in range(len(arr)):
        # Add: if current element is negative, track it
        if arr[i] < 0:
            negatives.append(i)

        # Remove: evict elements outside current window
        if negatives and negatives[0] < i - k + 1:
            negatives.popleft()

        # Record result only once window is fully formed
        if i >= k - 1:
            result.append(arr[negatives[0]] if negatives else 0)

    return result

# Trace: arr=[12,-1,-7,8,-15,30,16,28], k=3
# i=0: window not full yet
# i=1: negatives=[1], window not full
# i=2: negatives=[1,2], window full → first_neg = arr[1] = -1
# i=3: negatives=[1,2], evict? 1 >= 3-3+1=1? yes, popleft → [2], first_neg=arr[2]=-7
# i=4: negatives=[2,4], evict? 2 >= 2? yes → [4], first_neg=arr[4]=-15
# ...
```

---

## 3. Pattern 2: Variable Window — Expand / Shrink

**Mental model**: `right` pointer always expands the window (adds elements).
`left` pointer shrinks the window when a constraint is violated.
The window "breathes" — it's never reset, only adjusted.

**When to use**:
- Longest subarray/substring satisfying a condition
- Shortest subarray satisfying a condition
- Any problem where window size is not fixed

### Template

```python
def variable_window(s):
    left = 0
    window_state = initial_state()   # e.g., empty set, counter=0
    result = 0   # track best window size or start index

    for right in range(len(s)):
        # --- EXPAND: include s[right] in window ---
        update_state_on_add(window_state, s[right])

        # --- SHRINK: fix constraint violation ---
        while constraint_violated(window_state):
            update_state_on_remove(window_state, s[left])
            left += 1

        # --- RECORD: window [left..right] is now valid ---
        result = max(result, right - left + 1)   # or min, or collect answer

    return result
```

**Two flavors**:
- **Longest**: `while` loop shrinks until valid → record after shrink
- **Shortest**: `while` loop shrinks while valid → record inside shrink loop

---

### Worked Example 1: Longest Substring Without Repeating Characters

```python
def length_of_longest_substring(s):
    left = 0
    char_set = set()    # tracks characters in current window
    max_len = 0

    for right in range(len(s)):
        # EXPAND: try to add s[right]
        # SHRINK: if duplicate found, remove from left until no duplicate
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1

        char_set.add(s[right])
        max_len = max(max_len, right - left + 1)

    return max_len

# Trace: s="abcabcbb"
# right=0: add 'a', window="a",    max_len=1
# right=1: add 'b', window="ab",   max_len=2
# right=2: add 'c', window="abc",  max_len=3
# right=3: 'a' in set → remove 'a'(left=0), left=1 → add 'a', window="bca", max_len=3
# right=4: 'b' in set → remove 'b'(left=1), left=2 → add 'b', window="cab", max_len=3
# right=5: 'c' in set → remove 'c'(left=2), left=3 → add 'c', window="abc", max_len=3
# right=6: 'b' in set → remove 'a'(3), remove 'b'(4), left=5 → window="cb", max_len=3
# right=7: 'b' in set → remove 'c'(5), left=6 → 'b' still in? yes → remove 'b'(6), left=7
#          → add 'b', window="b", max_len=3
```

---

### Worked Example 2: Minimum Size Subarray Sum

**Problem**: Find the minimal length subarray with sum >= target.

```python
def min_subarray_len(target, nums):
    left = 0
    window_sum = 0
    min_len = float('inf')

    for right in range(len(nums)):
        window_sum += nums[right]   # EXPAND

        # SHRINK while constraint is satisfied (not violated!)
        # For "shortest" problems: shrink while valid, record inside
        while window_sum >= target:
            min_len = min(min_len, right - left + 1)   # record before shrinking
            window_sum -= nums[left]
            left += 1

    return 0 if min_len == float('inf') else min_len

# Trace: nums=[2,3,1,2,4,3], target=7
# right=0: sum=2  < 7, no shrink
# right=1: sum=5  < 7, no shrink
# right=2: sum=6  < 7, no shrink
# right=3: sum=8  >= 7 → record len=4, remove 2→sum=6, left=1. sum<7, stop
# right=4: sum=10 >= 7 → record len=4, remove 3→sum=7, left=2
#                       sum=7  >= 7 → record len=3, remove 1→sum=6, left=3. stop
# right=5: sum=9  >= 7 → record len=3, remove 2→sum=7, left=4
#                       sum=7  >= 7 → record len=2, remove 4→sum=3, left=5. stop
# min_len = 2
```

---

## 4. Pattern 3: Window with Counter (Hash Map Tracking)

**Mental model**: The window state is not a simple sum but a frequency map.
Use `collections.Counter` or `defaultdict(int)` to track what's inside the window.
A separate `formed` counter avoids iterating the map to check validity.

**When to use**:
- "Permutation of t in s"
- "Longest substring with at most k distinct characters"
- "Minimum window substring covering all characters of t"

### Template

```python
from collections import Counter, defaultdict

def window_with_counter(s, t):
    need = Counter(t)               # characters needed and their counts
    have = defaultdict(int)         # characters in current window
    formed = 0                      # how many chars in `need` are fully satisfied
    required = len(need)            # total distinct chars we need to satisfy

    left = 0
    result = (float('inf'), 0, 0)   # (length, left, right)

    for right in range(len(s)):
        # EXPAND: add s[right] to window
        char = s[right]
        have[char] += 1

        # Check if this character's count just met the requirement
        if char in need and have[char] == need[char]:
            formed += 1

        # SHRINK: while all requirements met, try to minimize window
        while formed == required:
            # Record current valid window
            if right - left + 1 < result[0]:
                result = (right - left + 1, left, right)

            # Remove s[left] from window
            left_char = s[left]
            have[left_char] -= 1
            if left_char in need and have[left_char] < need[left_char]:
                formed -= 1
            left += 1

    _, l, r = result
    return s[l:r+1] if result[0] != float('inf') else ""
```

---

### Worked Example: Permutation in String

**Problem**: Return true if s2 contains a permutation of s1.

```python
def check_inclusion(s1, s2):
    if len(s1) > len(s2):
        return False

    need = Counter(s1)
    have = defaultdict(int)
    formed = 0
    required = len(need)
    left = 0

    for right in range(len(s2)):
        char = s2[right]
        have[char] += 1
        if char in need and have[char] == need[char]:
            formed += 1

        # Fixed window size: shrink when window exceeds len(s1)
        if right - left + 1 > len(s1):
            left_char = s2[left]
            if left_char in need and have[left_char] == need[left_char]:
                formed -= 1
            have[left_char] -= 1
            left += 1

        if formed == required:
            return True

    return False

# s1="ab", s2="eidbaooo"
# need={'a':1,'b':1}, required=2
# Window slides with fixed size 2:
# "ei" → no, "id" → no, "db" → no, "ba" → formed=2! return True
```

---

### Worked Example: Longest Substring with At Most K Distinct Characters

```python
def longest_k_distinct(s, k):
    char_count = defaultdict(int)
    left = 0
    max_len = 0

    for right in range(len(s)):
        char_count[s[right]] += 1   # EXPAND

        # SHRINK: more than k distinct characters in window
        while len(char_count) > k:
            char_count[s[left]] -= 1
            if char_count[s[left]] == 0:
                del char_count[s[left]]   # remove from map when count hits 0
            left += 1

        max_len = max(max_len, right - left + 1)

    return max_len

# s="eceba", k=2
# right=0: {'e':1}, len=1 ≤ 2, max=1
# right=1: {'e':1,'c':1}, len=2 ≤ 2, max=2
# right=2: {'e':2,'c':1}, len=2 ≤ 2, max=3
# right=3: {'e':2,'c':1,'b':1}, len=3 > 2 → shrink:
#           remove 'e'(left=0) → {'e':1,'c':1,'b':1} still 3 > 2
#           remove 'c'(left=1) → {'e':1,'b':1} len=2, left=2
#           max = max(3, 3-2+1=2) = 3 (window "eba" isn't counted yet, right=3-left=2, len=2)
# right=4: {'e':1,'b':1,'a':1}, len=3 > 2 → remove 'e'(left=2), left=3
#           {'b':1,'a':1}, max = max(3,2) = 3
```

---

## 5. Pattern 4: Sliding Window Maximum (Monotonic Deque)

**Mental model**: A deque stores indices of "useful" candidates for the maximum.
The deque is always **monotonically decreasing** (front = max of current window).
Elements that can never be the maximum are evicted immediately.

**When to use**:
- Maximum (or minimum) of every window of size k
- Problems requiring O(n) window extremum queries

**Why not just use max(window)?** — That's O(k) per step → O(nk) total.
The deque gives O(1) amortized per step → O(n) total.

### Template

```python
from collections import deque

def sliding_window_maximum(nums, k):
    dq = deque()    # stores INDICES, values are monotonically decreasing
    result = []

    for i in range(len(nums)):
        # EVICT from back: remove indices whose values are smaller than current
        # (they can never be the max while current element is in the window)
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()

        dq.append(i)

        # EVICT from front: remove indices outside current window
        if dq[0] < i - k + 1:
            dq.popleft()

        # Window fully formed: record maximum (front of deque)
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result

# Trace: nums=[1,3,-1,-3,5,3,6,7], k=3
# i=0: dq=[0]
# i=1: nums[0]=1 < nums[1]=3 → pop 0, dq=[1]
# i=2: nums[1]=3 > nums[2]=-1 → keep, dq=[1,2]. Window full → max=nums[1]=3
# i=3: nums[2]=-1 > nums[3]=-3 → keep, dq=[1,2,3]. Front=1 >= 3-3+1=1 → max=nums[1]=3
# i=4: nums[3]=-3 < 5 → pop 3, nums[2]=-1 < 5 → pop 2, nums[1]=3 < 5 → pop 1, dq=[4]
#       Front=4 >= 4-3+1=2 → max=nums[4]=5
# i=5: nums[4]=5 > 3 → keep, dq=[4,5]. max=nums[4]=5
# i=6: pop 5 (3<6), pop 4 (5<6), dq=[6]. max=nums[6]=6
# i=7: pop 6 (6<7), dq=[7]. max=nums[7]=7
# Result: [3,3,5,5,6,7]
```

---

## 6. Pattern Evolution Map

Understanding which pattern to reach for based on problem complexity:

```
Problem: "max sum of subarray of size k"
  → Pattern 1: Fixed Window (simple sum tracking)

Problem: "longest subarray with sum ≤ k"
  → Pattern 2: Variable Window (expand/shrink)

Problem: "longest substring with at most k distinct chars"
  → Pattern 3: Window + Counter (freq map needed)

Problem: "minimum window covering all chars of t"
  → Pattern 3: Window + Counter (with `formed` optimization)

Problem: "max element in every window of size k"
  → Pattern 4: Monotonic Deque (O(n) needed)
```

---

## 7. Problem → Pattern Mapping Table

| Problem | Pattern | Key State |
|---------|---------|-----------|
| Max sum of k elements | Fixed Window | running sum |
| Average of k elements | Fixed Window | running sum |
| First negative in each window | Fixed Window | deque of indices |
| Longest substring no repeat | Variable Window | set |
| Minimum size subarray sum | Variable Window | running sum |
| Longest subarray sum ≤ k | Variable Window | running sum |
| Permutation in string | Window + Counter | freq map + `formed` |
| Minimum window substring | Window + Counter | freq map + `formed` |
| Longest k distinct chars | Window + Counter | freq map + len() |
| Sliding window maximum | Monotonic Deque | deque of indices |
| Sliding window minimum | Monotonic Deque | deque (increasing) |

---

## 8. Common Mistakes and How to Avoid Them

### Mistake 1: Resetting the window instead of sliding

```python
# WRONG: resets left to 0 on each violation
for right in range(n):
    if violated:
        left = 0   # throws away all progress!

# CORRECT: only advance left
while violated:
    remove(s[left])
    left += 1
```

### Mistake 2: Off-by-one in fixed window

```python
# Window [left..right] has size: right - left + 1
# For fixed window of size k, shrink when: right - left + 1 > k
# Equivalently: shrink when right - left >= k
# Or: shrink when right >= left + k

if right - left + 1 > k:   # time to slide
    remove(s[left])
    left += 1
```

### Mistake 3: Not handling the `formed` counter correctly

```python
# WRONG: checking formed when adding might be wrong direction
have[char] += 1
if have[char] == need[char]:     # only increment when EXACTLY meeting requirement
    formed += 1

# When removing:
have[char] -= 1
if have[char] == need[char] - 1: # was exactly meeting, now falls short
    formed -= 1
# Equivalently: if char in need and have[char] < need[char]: formed -= 1
```

---

## 9. Sliding Window + Other Patterns

### Sliding Window + Two Pointers

The sliding window IS two pointers (left and right). The distinction:
- "Two pointers" usually means converging from both ends
- "Sliding window" means both move left to right (same direction, different speeds)

### Sliding Window + Binary Search

When the window size itself is the answer and it has monotonic property:

```python
# "Find smallest window size k such that condition holds"
# Binary search on k, check feasibility with fixed window
def smallest_k(arr, target):
    def feasible(k):
        # Fixed window check: can window of size k satisfy target?
        window_sum = sum(arr[:k])
        if window_sum >= target:
            return True
        for i in range(k, len(arr)):
            window_sum += arr[i] - arr[i - k]
            if window_sum >= target:
                return True
        return False

    lo, hi = 1, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

### Sliding Window + Prefix Sum

For subarray sum problems with negative numbers (variable window shrink doesn't work):

```python
# When array has negatives, use prefix sums + hash map
# "Number of subarrays with sum == k"
def subarray_sum(nums, k):
    from collections import defaultdict
    prefix_count = defaultdict(int)
    prefix_count[0] = 1
    prefix_sum = 0
    count = 0

    for num in nums:
        prefix_sum += num
        count += prefix_count[prefix_sum - k]
        prefix_count[prefix_sum] += 1

    return count
```

---

## Quick Reference Cheat Sheet

```
Fixed Window (size k):
  init: process arr[0..k-1]
  slide: add arr[i], remove arr[i-k]
  when: "every window of size k"

Variable Window (longest):
  expand: right += 1, update state
  shrink: while invalid: left += 1, update state
  record: after shrink (window is valid)
  when: "longest/maximum subarray satisfying..."

Variable Window (shortest):
  expand: right += 1, update state
  shrink: while valid: record, left += 1, update state
  when: "shortest/minimum subarray satisfying..."

Counter Window:
  need = Counter(t), formed tracks satisfied chars
  expand adds to `have`, may increment `formed`
  shrink removes from `have`, may decrement `formed`
  when: character frequency constraints

Monotonic Deque:
  back-evict smaller elements before appending
  front-evict out-of-window elements
  front of deque = current window max
  when: "max/min of every window of size k"
```
