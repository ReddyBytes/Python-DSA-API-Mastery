<a id="top"></a>
# 📘 12 – Sliding Window in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is Sliding Window?](#1-what-is-sliding-window)
  - [Visual: Fixed Window Maximum Sum](#visual-fixed-max)
- [2. Fixed Size Window](#2-fixed-window)
- [3. Variable Size Window](#3-variable-window)
  - [Visual: Longest Substring Without Repeats](#visual-longest-substring)
- [4. Why Sliding Window Is Powerful](#4-why-powerful)
- [5. Sliding Window in Strings](#5-strings)
- [6. Common Sliding Window Problems](#6-common-problems)
  - [Visual: Minimum Window Substring](#visual-min-window)
- [7. Sliding Window Maximum — Deque](#7-deque-max)
  - [Visual: Deque Window Step by Step](#visual-deque)
  - [Visual: Pattern Summary](#visual-pattern-summary)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
fixed-size window · variable-size window · window expansion and contraction

**Should Learn** — Important for real projects, comes up regularly:
state maintenance in window · longest substring without repeating chars · minimum window substring

**Good to Know** — Useful in specific situations, not always tested:
sliding window maximum (deque optimization) · window vs two pointers distinction

**Reference** — Know it exists, look up syntax when needed:
categorical sliding window · multi-pointer variants

Lena is a photographer. She looks at the world through her camera's viewfinder — a frame that captures only a portion of the scene. As she pans the camera, old scenery leaves the left edge and new scenery enters from the right. She never rebuilds the entire scene from scratch — she just updates what entered and what left. That is **sliding window**: maintaining a running calculation over a moving portion of data, updating incrementally instead of recomputing from zero.

<a id="1-what-is-sliding-window"></a>
# 1. What Is Sliding Window?

Lena is looking at a night sky through a telescope that shows exactly 3 stars at a time. She wants to find the brightest patch — the window of 3 stars with the most total light. Brute force: close her eyes, open at each position, count all 3 stars. Sliding window: she is already looking at stars 1-2-3. To see stars 2-3-4, she just slides one step — remove star 1's brightness, add star 4's. One subtraction. One addition. Instant.

Instead of rebuilding the subarray every time, you:
1. Maintain a window with two pointers (left, right)
2. Expand right boundary
3. Shrink left boundary when needed
4. Maintain some property (sum, count, max, set)

```
Initial window:          [★ ★ ★] ○ ○ ○ ○ ○
Slide right:              ○ [★ ★ ★] ○ ○ ○ ○
Slide right:              ○  ○ [★ ★ ★] ○ ○ ○
                                      ↑
                         Always: remove left star, add right star
```

<a id="visual-fixed-max"></a>
## Visual: Fixed Window Maximum Sum

**Problem:** Find max sum of any 3 consecutive elements.
**Input:** `[2, 1, 5, 1, 3, 2]`, k = 3

```
Step 1: Build first window.
  Sum first k=3 elements: 2+1+5 = 8

  [ 2,  1,  5,  1,  3,  2 ]
    ├────────┤
    window = [2,1,5], sum = 8, max_sum = 8

Step 2: Slide right.
  Remove 2, add 1. New sum = 8 - 2 + 1 = 7

  [ 2,  1,  5,  1,  3,  2 ]
         ├────────┤
         sum = 7, max_sum = 8

Step 3: Slide right.
  Remove 1, add 3. New sum = 7 - 1 + 3 = 9

  [ 2,  1,  5,  1,  3,  2 ]
              ├────────┤
              sum = 9, max_sum = 9

Step 4: Slide right.
  Remove 5, add 2. New sum = 9 - 5 + 2 = 6

  [ 2,  1,  5,  1,  3,  2 ]
                   ├────────┤
                   sum = 6, max_sum = 9

Answer: 9
```

Formula: `new_sum = old_sum - arr[left] + arr[right]`. Never re-sum the whole window.

> [↑ Back to Top](#top)

<a id="2-fixed-window"></a>
# 2. Fixed Size Window

Lena's viewfinder has a fixed width — she always captures exactly k frames. The window only slides forward, never grows or shrinks.

```python
def max_sum_subarray(arr, k):
    window_sum = sum(arr[:k])
    max_sum = window_sum

    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]  # add right, remove left
        max_sum = max(max_sum, window_sum)

    return max_sum
```

Time: O(n). Space: O(1).

**Common mistake — fixed-window off-by-one:** The correct slide condition is `right - left + 1 > k`, not `right - left > k`. The missing `+1` means your window has `k+1` elements before it shrinks.

> 📝 **Practice:** [Q24 · sliding-window-fixed](../dsa_practice_questions_100.md#q24--code--sliding-window-fixed)
> 📝 **Practice:** [Q1 — Max Sum Subarray of Size K](./practice.md#q1--max-sum-subarray-of-size-k) · [Q2 — Average of All Subarrays](./practice.md#q2--average-of-all-subarrays-of-size-k) · [Q6 — First Negative in Window](./practice.md#q6--first-negative-in-each-window-of-size-k)

> [↑ Back to Top](#top)

<a id="3-variable-window"></a>
# 3. Variable Size Window

Lena switches to a zoom lens — her viewfinder can grow and shrink. She expands until a condition is met, then shrinks to find the optimal answer. This is more powerful than fixed windows.

Example: smallest subarray with sum ≥ 7

```
[2, 3, 1, 2, 4, 3]

Add 2 → sum=2
Add 3 → sum=5
Add 1 → sum=6
Add 2 → sum=8 (≥7!) → record window size = 4
Shrink: remove 2 → sum=6 (<7, stop shrinking)
Continue expanding...
```

The grow-shrink behavior: expand right until condition satisfied, then shrink left to optimize.

```
EXPAND when: adding arr[right] doesn't break invariant
SHRINK when: invariant satisfied, try to minimize window
UPDATE answer: after each valid state
```

<a id="visual-longest-substring"></a>
## Visual: Longest Substring Without Repeating Characters

**Input:** `"abcabcbb"`. Find longest substring with all unique characters.

```
String: a  b  c  a  b  c  b  b
Index:  0  1  2  3  4  5  6  7

Step 1: lo=0, hi=0, set={a}, max=1
  a  b  c  a  b  c  b  b
  ↑
  No repeat → expand

Step 2: lo=0, hi=1, set={a,b}, max=2

Step 3: lo=0, hi=2, set={a,b,c}, max=3
  a  b  c  a  b  c  b  b
  ↑     ↑
  lo    hi

Step 4: hi=3, new char 'a' already in set!
  Shrink: remove 'a', lo=1. Set={b,c}
  Add new 'a'. Set={b,c,a}, max=3

Step 5: hi=4, new char 'b' in set!
  Shrink: remove 'b', lo=2. Set={c,a}
  Add new 'b'. Set={c,a,b}, max=3

...continue, max never exceeds 3.

Answer: 3 ("abc")
```

Window invariant: `[lo, hi]` always contains unique characters. When violated, shrink until fixed.

**Common mistake — resetting left to 0:** When a collision occurs, advance `left` one step at a time. Resetting `left = 0` throws away all progress and gives O(n²) behavior.

> 📝 **Practice:** [Q25 · sliding-window-variable](../dsa_practice_questions_100.md#q25--thinking--sliding-window-variable)
> 📝 **Practice:** [Q9 — Longest Substring No Repeat](./practice.md#q9--longest-substring-without-repeating-characters) · [Q11 — Longest Subarray Sum ≤ K](./practice.md#q11--longest-subarray-with-sum--k) · [Q15 — Min Size Subarray Sum](./practice.md#q15--minimum-size-subarray-sum)

> [↑ Back to Top](#top)

<a id="4-why-powerful"></a>
# 4. Why Sliding Window Is Powerful

Lena understands why her technique is so efficient: each star enters the viewfinder once and leaves once. No element is processed more than twice.

Without sliding window: nested loops → O(n²)
With sliding window: each element enters once, leaves once → ≤ 2n operations → O(n)

```
Why O(n):
  left pointer:  moves right at most n times total
  right pointer: moves right at most n times total
  Total moves:   ≤ 2n = O(n)
```

> [↑ Back to Top](#top)

<a id="5-strings"></a>
# 5. Sliding Window in Strings

Lena discovers that string problems are the natural home of sliding window. Any time you see "longest substring with..." or "smallest substring containing...", the sliding window template applies directly.

Common string patterns:
- Longest substring without repeating characters
- Longest substring with at most k distinct characters
- Minimum window substring (contains all chars of target)
- Permutation in string

The key: maintain a frequency map (Counter/dict) as your window state. Expand right to include new chars, shrink left to restore validity.

> [↑ Back to Top](#top)

<a id="6-common-problems"></a>
# 6. Common Sliding Window Problems

<a id="visual-min-window"></a>
## Visual: Minimum Window Substring

**Problem:** Find smallest substring of `s` that contains all characters of `t`.
**Input:** s = `"ADOBECODEBANC"`, t = `"ABC"`

```
need: {A:1, B:1, C:1}  (characters we must have)
have: 0                  (how many of need are satisfied)
required: 3              (total distinct chars needed)

Expand right until all chars found, then shrink left to minimize.

Window trace (key moments):

"ADOBEC" → contains A,B,C → valid! length=6
 "DOBEC"  → still has A? No → invalid, expand again
...
"ECODEBA" → no C → invalid
"ECODEBANC" → has A,B,C → valid! length=9, worse
"BANC" → has A,B,C → valid! length=4 ← answer!
```

```python
from collections import Counter

def min_window(s, t):
    if not t or not s:
        return ""
    need = Counter(t)
    required = len(need)
    have = 0
    window = {}
    left = 0
    result = (float('inf'), 0, 0)  # (length, left, right)

    for right, ch in enumerate(s):
        window[ch] = window.get(ch, 0) + 1
        if ch in need and window[ch] == need[ch]:
            have += 1

        while have == required:
            # update answer
            if right - left + 1 < result[0]:
                result = (right - left + 1, left, right)
            # shrink from left
            left_ch = s[left]
            window[left_ch] -= 1
            if left_ch in need and window[left_ch] < need[left_ch]:
                have -= 1
            left += 1

    length, l, r = result
    return s[l:r+1] if length != float('inf') else ""
```

> [↑ Back to Top](#top)

<a id="7-deque-max"></a>
# 7. Sliding Window Maximum — Deque

Lena faces her hardest problem: for each window position, find the maximum element. Brute force scans all k elements per window → O(nk). A **monotonic deque** maintains the max in O(1) per step, giving O(n) total.

The idea: maintain a deque of indices where values are in DECREASING order. The front always holds the window's maximum.

<a id="visual-deque"></a>
## Visual: Deque Window Step by Step

**Input:** `[1, 3, -1, -3, 5, 3, 6, 7]`, k=3

```
i=0, val=1:  deque=[0]               window not full
i=1, val=3:  3>1, pop 0. deque=[1]   window not full
i=2, val=-1: -1<3, keep. deque=[1,2] OUTPUT: arr[1]=3
i=3, val=-3: -3<-1,keep. deque=[1,2,3]
             front=1, still in window? 3-1+1=3, yes.
             OUTPUT: arr[1]=3
i=4, val=5:  5>-3, pop 3. 5>-1, pop 2. 5>3, pop 1.
             deque=[4]. OUTPUT: arr[4]=5
i=5, val=3:  3<5, keep. deque=[4,5]  OUTPUT: arr[4]=5
i=6, val=6:  6>3, pop 5. 6>5, pop 4.
             deque=[6]. OUTPUT: arr[6]=6
i=7, val=7:  7>6, pop 6. deque=[7]   OUTPUT: arr[7]=7

Result: [3, 3, 5, 5, 6, 7]
```

```python
from collections import deque

def sliding_window_max(nums, k):
    dq = deque()
    result = []
    for i, val in enumerate(nums):
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        while dq and nums[dq[-1]] < val:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

Why O(n)? Each index is pushed once and popped once. Total: 2n operations.

<a id="visual-pattern-summary"></a>
## Visual: Pattern Summary

```
┌─────────────────────────────────────────────────────────────┐
│  SLIDING WINDOW DECISION TREE                                │
├──────────────────────────────┬──────────────────────────────┤
│  Window size fixed (k)?      │  → Fixed window template      │
│  Window grows/shrinks?       │  → Variable window template   │
│  Need max/min in window?     │  → Monotonic deque            │
│  String with char freq?      │  → Counter + variable window  │
└──────────────────────────────┴──────────────────────────────┘

Template comparison:

Fixed:    slide = add right, remove left (always)
Variable: expand right, shrink left ONLY when condition met
Deque:    fixed window + maintain monotonic structure for O(1) max
```

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

| Concept | Key Takeaway |
|---------|-------------|
| Sliding window | Incremental update over a moving subarray/substring |
| Fixed window | Size k, slide right: O(n) |
| Variable window | Expand + shrink: O(n), finds optimal window |
| Why O(n) | Each element enters once, leaves once → 2n operations |
| Monotonic deque | O(1) window max/min → O(n) total |
| Strings | Counter + variable window solves most substring problems |

**Sliding Window vs Two Pointers:**
- Two pointers: converging from ends, finding pairs in sorted data
- Sliding window: same direction, maintaining a continuous subarray/substring
- Sliding window IS a type of two pointers (same direction, both move right)

**Maintaining window state:**
- Sum: add entering element, subtract leaving element
- Frequency: increment on enter, decrement on leave
- Unique count: hash set, add/remove as window moves
- Max/min: use monotonic deque for O(1) per query

**Real-world applications:**
- Network traffic monitoring (bytes per second in a time window)
- Stock price analytics (rolling averages)
- Rate limiting (requests per minute)
- Streaming data processing

**Mental model:** You are on a train. The window shows part of the scenery. As the train moves, old scenery leaves, new scenery enters. You never rebuild the full scene — you just track what changed.

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [11_two_pointers → theory.md](../11_two_pointers/theory.md) |
| ➡ Next Module | [13_binary_search → theory.md](../13_binary_search/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[11 Two Pointers →](../11_two_pointers/theory.md) · [13 Binary Search →](../13_binary_search/theory.md) · [03 Strings →](../03_strings/theory.md) · [09 Queue →](../09_queue/theory.md)

**Jump to specific topics in other files:**
- Two pointers foundation → [11_two_pointers § theory.md](../11_two_pointers/theory.md)
- Longest substring (string version) → [03_strings § Sliding Window](../03_strings/theory.md#sliding-window)
- Monotonic deque → [09_queue § Monotonic Deque](../09_queue/theory.md#visual-monotonic-deque)
- Deque data structure → [09_queue § Double-Ended Queue](../09_queue/theory.md#5-deque)

> [↑ Back to Top](#top)
