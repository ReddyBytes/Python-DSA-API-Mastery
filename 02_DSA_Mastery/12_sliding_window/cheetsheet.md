# Sliding Window — Cheatsheet

---

## Fixed vs Variable Window

| Dimension        | Fixed Window                        | Variable Window                          |
|------------------|-------------------------------------|------------------------------------------|
| Window size      | Constant k                          | Shrinks/expands based on condition       |
| Shrink trigger   | Always drop leftmost when size > k  | Drop left when constraint violated       |
| Typical ask      | Max/min sum of subarray of size k   | Longest/shortest subarray satisfying X  |
| Template style   | for-loop with single index          | while-loop or two-pointer               |
| Common data str  | Running sum / counter               | Hash map (char/element frequencies)     |

---

## Complexity

| Approach         | Time   | Space                     |
|------------------|--------|---------------------------|
| Fixed window     | O(n)   | O(1) or O(k)              |
| Variable window  | O(n)   | O(k) — at most k distinct |
| Deque window max | O(n)   | O(k)                      |

Each element enters and exits the window at most once → O(n) total.

---

## Template 1: Fixed Window

```python
def fixed_window(arr, k):
    # --- build first window ---
    window_sum = sum(arr[:k])
    best = window_sum

    # --- slide: add right, remove left ---
    for i in range(k, len(arr)):
        window_sum += arr[i]            # add incoming right element
        window_sum -= arr[i - k]        # remove outgoing left element
        best = max(best, window_sum)    # update answer

    return best
```

### Fixed Window — Count With Condition

```python
def fixed_window_count(s, k):
    counts = {}
    left = 0
    res = 0

    for right in range(len(s)):
        counts[s[right]] = counts.get(s[right], 0) + 1   # expand

        if right - left + 1 == k:                          # window full
            if satisfies(counts):                          # check condition
                res += 1
            counts[s[left]] -= 1                           # shrink exactly 1
            if counts[s[left]] == 0:
                del counts[s[left]]
            left += 1

    return res
```

---

## Template 2: Variable Window (Longest)

Goal: find longest window satisfying a constraint.

```python
def variable_window_longest(s):
    counts = {}                         # track window contents
    left = 0
    res = 0

    for right in range(len(s)):
        # 1. Expand: add s[right] to window
        counts[s[right]] = counts.get(s[right], 0) + 1

        # 2. Shrink: while constraint violated, remove s[left]
        while not valid(counts):        # define valid() per problem
            counts[s[left]] -= 1
            if counts[s[left]] == 0:
                del counts[s[left]]
            left += 1

        # 3. Update answer (window is valid here)
        res = max(res, right - left + 1)

    return res
```

---

## Template 3: Variable Window (Shortest)

Goal: find shortest window satisfying a constraint.

```python
def variable_window_shortest(s, target):
    counts = {}
    left = 0
    res = float('inf')
    formed = 0                          # elements satisfying requirement

    for right in range(len(s)):
        counts[s[right]] = counts.get(s[right], 0) + 1
        # update formed if this character now meets requirement
        if counts[s[right]] == target.get(s[right], 0):
            formed += 1

        # shrink as long as window is valid
        while formed == len(target):
            res = min(res, right - left + 1)
            counts[s[left]] -= 1
            if counts[s[left]] < target.get(s[left], 0):
                formed -= 1
            left += 1

    return res if res != float('inf') else 0
```

---

## Window Shrink Conditions

```
Problem type                         When to shrink (move left)
─────────────────────────────────────────────────────────────────
Longest without repeating chars      counts[char] > 1
Longest with at most k distinct      len(counts) > k
Longest with at most k replacements  (window - max_freq) > k
Minimum window substring             all required chars covered
Fixed window                         window size > k  (always 1 step)
```

---

## Template 4: With Hash Map (Character Counting)

```python
# Longest Substring Without Repeating Characters
def length_of_longest_substring(s):
    seen = {}                           # char → last seen index
    left = 0
    res = 0
    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1         # jump left past duplicate
        seen[ch] = right
        res = max(res, right - left + 1)
    return res
```

```python
# Longest Substring with At Most K Distinct Characters
def longest_k_distinct(s, k):
    counts = {}
    left = res = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        while len(counts) > k:
            counts[s[left]] -= 1
            if counts[s[left]] == 0:
                del counts[s[left]]
            left += 1
        res = max(res, right - left + 1)
    return res
```

---

## Template 5: Deque for Sliding Window Max / Min

```
Window slides right, deque holds indices in decreasing order (for max).
Front of deque is always the max of the current window.

arr =  [1, 3, -1, -3,  5,  3,  6,  7], k=3
         ^        ^
        left    right
```

```python
from collections import deque

def sliding_window_max(nums, k):
    dq = deque()                        # indices, decreasing value order
    res = []

    for i, num in enumerate(nums):
        # remove elements outside window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # remove smaller elements from back (they can never be max)
        while dq and nums[dq[-1]] < num:
            dq.pop()

        dq.append(i)

        if i >= k - 1:                  # first full window reached
            res.append(nums[dq[0]])     # front is always max

    return res
# Time: O(n)  — each element pushed/popped once
# Space: O(k) — deque holds at most k indices
```

---

## Recognition Signals

```
"subarray/substring of length k"                → Fixed window
"max/min sum of k consecutive elements"         → Fixed window
"longest subarray/substring with [condition]"   → Variable window (longest)
"minimum subarray/substring with [condition]"   → Variable window (shortest)
"contains all characters of pattern"            → Variable + hash map
"sliding window maximum/minimum"                → Deque
```

---

## Common Problems Reference

### Fixed Window
| Problem                               | Key Idea                                  |
|---------------------------------------|-------------------------------------------|
| Max sum subarray of size k            | Running sum: +right, -left                |
| Average of all subarrays of size k    | Same, divide by k                         |
| Count anagrams in string              | Fixed window + char frequency match       |
| Find all anagrams (LC 438)            | counts match == target_counts             |

### Variable Window (Longest)
| Problem                               | Shrink Condition                          |
|---------------------------------------|-------------------------------------------|
| Longest substring no repeating (LC 3) | counts[ch] > 1                            |
| Longest substring k distinct (LC 340) | len(window) > k                           |
| Longest repeating char replace (LC 424)| (size - max_freq) > k                    |
| Max consecutive ones III (LC 1004)    | zeros_in_window > k                       |

### Variable Window (Shortest)
| Problem                               | Shrink Condition                          |
|---------------------------------------|-------------------------------------------|
| Min window substring (LC 76)          | all required chars covered                |
| Shortest subarray with sum >= k       | Use deque (handles negatives)             |
| Min size subarray sum (LC 209)        | running sum >= target                     |

---

## Longest Repeating Character Replacement (Template)

```python
def character_replacement(s, k):
    counts = {}
    left = max_freq = res = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        max_freq = max(max_freq, counts[ch])
        # window_size - max_freq = chars to replace
        while (right - left + 1) - max_freq > k:
            counts[s[left]] -= 1
            left += 1
        res = max(res, right - left + 1)
    return res
# Note: max_freq never decreases — this is an optimization, still correct
```

---

## Minimum Window Substring (Full Template)

```python
def min_window(s, t):
    from collections import Counter
    need = Counter(t)
    missing = len(t)                    # total chars still needed
    left = start = 0
    res = ""

    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1               # one more required char found
        need[ch] -= 1

        if missing == 0:               # valid window
            # shrink from left
            while need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            if not res or right - left + 1 < len(res):
                res = s[left:right+1]
            # move left one more to find next candidate
            need[s[left]] += 1
            missing += 1
            left += 1
    return res
```

---

## Common Mistakes

| Mistake                                   | Fix                                              |
|-------------------------------------------|--------------------------------------------------|
| Forgetting to shrink the window           | Add `while not valid(window): left += 1`         |
| Off-by-one in window size check           | Window size = `right - left + 1`                |
| Not removing key from dict when count=0  | `if counts[ch] == 0: del counts[ch]`             |
| Deque: not removing out-of-range indices  | `while dq and dq[0] < i - k + 1: dq.popleft()` |
| Fixed window: forgetting first window     | Seed first window before the sliding loop        |
| Shrinking too aggressively (shortest)     | Shrink only while window is still valid          |
| Using set instead of Counter             | Sets can't track duplicate character counts      |

---

## Python Tricks

```python
from collections import Counter, deque

# Check if two windows are anagrams
Counter(s[i:i+k]) == Counter(t)         # O(k) per check — use sliding instead

# Efficient frequency comparison for fixed window
def matches(have, need, formed, required):
    return formed == required

# collections.Counter subtract
c1 = Counter("abc")
c1.subtract(Counter("a"))               # in-place subtract

# deque operations
dq = deque()
dq.append(x)                            # add right  O(1)
dq.appendleft(x)                        # add left   O(1)
dq.pop()                                # remove right O(1)
dq.popleft()                            # remove left  O(1)
dq[0]                                   # peek left
dq[-1]                                  # peek right
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Visual Explanation](./visual_explanation.md) &nbsp;|&nbsp; **Next:** [Patterns →](./patterns.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
