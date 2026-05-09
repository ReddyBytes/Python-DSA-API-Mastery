# Sliding Window — Practice Questions

> 25 questions covering fixed-size windows, variable-size windows, frequency maps,
> shrink vs expand logic, when to use sliding window, common mistakes, and strings vs arrays.

---

## Quick Index

**Basic (Q1–Q8)**
- [Q1](#q1)
- [Q2](#q2)
- [Q3](#q3)
- [Q4](#q4)
- [Q5](#q5)
- [Q6](#q6)
- [Q7](#q7)
- [Q8](#q8)

**Intermediate (Q9–Q20)**
- [Q9](#q9)
- [Q10](#q10)
- [Q11](#q11)
- [Q12](#q12)
- [Q13](#q13)
- [Q14](#q14)
- [Q15](#q15)
- [Q16](#q16)
- [Q17](#q17)
- [Q18](#q18)
- [Q19](#q19)
- [Q20](#q20)

**Advanced (Q21–Q25)**
- [Q21](#q21)
- [Q22](#q22)
- [Q23](#q23)
- [Q24](#q24)
- [Q25](#q25)

---

## Basic Questions

---

<a id="q1"></a>
### Q1 — Max Sum Subarray of Size K

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Given `arr = [2, 1, 5, 1, 3, 2]` and `k = 3`, find the maximum sum of any contiguous subarray of size `k`.

<details>
<summary>Hint</summary>
Build the first window sum. Then slide: subtract the element leaving on the left, add the element entering on the right. No need to recompute from scratch.
</details>

<details>
<summary>Answer</summary>

```python
def max_sum_k(arr: list[int], k: int) -> int:
    if len(arr) < k:
        return -1
    window_sum = sum(arr[:k])
    max_sum = window_sum
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum

# arr=[2,1,5,1,3,2], k=3
# First window [2,1,5] → 8
# Slide: 8-2+1=7, 7-1+3=9, 9-5+2=6
# Answer: 9
```

**Why:** Each slide is one addition and one subtraction, so the whole pass is O(n) instead of O(nk). The formula `new_sum = old_sum - arr[i-k] + arr[i]` is the core insight.

**Time:** O(n) | **Space:** O(1)
</details>

---

<a id="q2"></a>
### Q2 — Average of All Subarrays of Size K

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Given `arr = [1, 3, 2, 6, -1, 4, 1, 8, 2]` and `k = 5`, return a list of the average of each contiguous subarray of size `k`.

<details>
<summary>Hint</summary>
Same as max sum, but divide the running sum by k at each window position. Build the first window, then slide.
</details>

<details>
<summary>Answer</summary>

```python
def avg_subarrays(arr: list[int], k: int) -> list[float]:
    result = []
    window_sum = sum(arr[:k])
    result.append(window_sum / k)
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]
        result.append(window_sum / k)
    return result

# [1,3,2,6,-1,4,1,8,2], k=5
# [2.2, 2.8, 2.4, 3.6, 2.8]
```

**Why:** Running sum avoids recomputing k elements every time. Division by k at each step gives the average. Output list has `len(arr) - k + 1` entries.

**Time:** O(n) | **Space:** O(n) for output
</details>

---

<a id="q3"></a>
### Q3 — Identify the Sliding Window Pattern

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


For each problem below, say whether sliding window applies and which type (fixed, variable-longest, variable-shortest, or does not apply):

1. "Find max sum of any 5 consecutive elements."
2. "Longest substring where no character repeats."
3. "Find two numbers in an unsorted array that sum to a target."
4. "Minimum length subarray with sum ≥ target."
5. "Count subarrays where elements are not necessarily contiguous and sum to k."

<details>
<summary>Hint</summary>
Ask: is the answer always a contiguous block? Can the window property be maintained incrementally without restarting?
</details>

<details>
<summary>Answer</summary>

1. **Fixed window** — size 5, slide, track max sum.
2. **Variable window (longest)** — expand right, shrink left when duplicate found.
3. **Does not apply** — non-contiguous pair search; use hash map or two-pointer on sorted array.
4. **Variable window (shortest)** — expand until sum ≥ target, shrink to minimize length.
5. **Does not apply** — elements need not be contiguous; use prefix sums + hash map.

**Why:** The sliding window requires: (a) contiguous subarray/substring, and (b) a property that can be updated incrementally in O(1) or O(alphabet) when one element enters or leaves.

**Time:** O(1) to classify | **Space:** O(1)
</details>

---

<a id="q4"></a>
### Q4 — Fixed Window Off-by-One

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Why does `if right - left > k:` produce wrong results for a fixed window of size `k`? What is the correct condition?

<details>
<summary>Hint</summary>
Count how many indices are inclusive in `[left, right]`. Remember that both ends are included.
</details>

<details>
<summary>Answer</summary>

`right - left > k` slides the window when it has `k + 1` elements, not `k`. The window grows one step too large before shrinking.

The window `[left, right]` contains `right - left + 1` elements (both indices inclusive). It has exactly `k` elements when `right - left + 1 == k`. It needs to shrink when `right - left + 1 > k`.

```python
# WRONG — slides 1 step late
if right - left > k:
    window_sum -= arr[left]
    left += 1

# CORRECT — slides when window first exceeds k
if right - left + 1 > k:
    window_sum -= arr[left]
    left += 1
```

**Why:** Forgetting the `+ 1` is the single most common fixed-window bug. Internalize: window size = `right - left + 1`.

**Time:** O(1) | **Space:** O(1)
</details>

---

<a id="q5"></a>
### Q5 — Why O(n) Not O(nk)?

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Explain in plain English why sliding window is O(n) even though it processes windows of size k.

<details>
<summary>Hint</summary>
Think about each individual element — how many times does it enter the window? How many times does it leave?
</details>

<details>
<summary>Answer</summary>

Each element enters the window exactly once (when `right` reaches it) and leaves the window at most once (when `left` passes it). Total operations on elements = at most 2n, which is O(n).

```
arr = [a, b, c, d, e], k=3

Element 'a':  enters at right=0, leaves at left=1 (1 enter + 1 leave)
Element 'b':  enters at right=1, leaves at left=2 (1 enter + 1 leave)
...

Total: n enters + n leaves = 2n operations → O(n)
```

**Why:** Brute force recomputes k elements per window, giving O(nk). Sliding window avoids recomputation by maintaining state incrementally — one subtraction and one addition per step.

**Time:** O(n) | **Space:** O(1)
</details>

---

<a id="q6"></a>
### Q6 — First Negative in Each Window of Size K

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Given `arr = [12, -1, -7, 8, -15, 30, 16, 28]` and `k = 3`, return the first negative element in each window of size `k`. Return 0 if no negative exists in a window.

<details>
<summary>Hint</summary>
Maintain a deque of indices of negative numbers in the current window. Evict any index that falls outside the window boundary before recording the answer.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

def first_negative_window(arr: list[int], k: int) -> list[int]:
    neg_indices = deque()  # indices of negatives in current window
    result = []
    for i in range(len(arr)):
        if arr[i] < 0:
            neg_indices.append(i)
        # evict indices outside current window
        if neg_indices and neg_indices[0] < i - k + 1:
            neg_indices.popleft()
        if i >= k - 1:  # window is full
            result.append(arr[neg_indices[0]] if neg_indices else 0)
    return result

# arr=[12,-1,-7,8,-15,30,16,28], k=3
# Output: [-1, -1, -7, -15, -15, 0]
```

**Why:** A deque of indices lets us check the front (oldest negative) in O(1) and evict it in O(1) when it slides out. Without a deque we would scan the window each time — O(k) per window, O(nk) total.

**Time:** O(n) | **Space:** O(k)
</details>

---

<a id="q7"></a>
### Q7 — Sliding Window vs Two Pointers

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


What is the difference between sliding window and two pointers? Give one example of each.

<details>
<summary>Hint</summary>
Think about direction of movement and whether internal state is maintained inside the window.
</details>

<details>
<summary>Answer</summary>

**Two pointers:** Two indices that move (often toward each other or both left-to-right) without maintaining internal state. The pointers alone determine the answer.

Example: Two Sum in sorted array — `left` starts at 0, `right` at end, converge based on current sum.

**Sliding window:** Two pointers both moving left-to-right, plus a maintained state (sum, set, frequency map) that tracks what is inside `[left, right]`.

Example: Longest substring without repeating chars — same direction pointers, plus a `set` of characters currently in the window.

```python
# Two pointers — no window state
def two_sum_sorted(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        s = arr[left] + arr[right]
        if s == target: return [left, right]
        elif s < target: left += 1
        else: right -= 1

# Sliding window — maintains a set inside the window
def longest_unique(s):
    seen = set()
    left = res = 0
    for right in range(len(s)):
        while s[right] in seen:
            seen.remove(s[left]); left += 1
        seen.add(s[right])
        res = max(res, right - left + 1)
    return res
```

**Why:** Sliding window is an enhanced two-pointer where the window's internal state is tracked and updated incrementally.

**Time:** O(n) both | **Space:** O(1) two-ptr, O(k) sliding
</details>

---

<a id="q8"></a>
### Q8 — When Sliding Window Fails

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Give two concrete cases where sliding window cannot solve the problem. Explain why.

<details>
<summary>Hint</summary>
Think about what happens when elements are non-contiguous or when the window property cannot be maintained incrementally.
</details>

<details>
<summary>Answer</summary>

**Case 1 — Non-contiguous elements:** "Count pairs with sum = target." Pairs can come from any two positions, not adjacent. No window contains both elements consistently. Use a hash map instead.

**Case 2 — Negatives break monotonicity:** "Minimum length subarray with sum ≥ target" when array has negative numbers. When we shrink the window, removing an element might increase or decrease the sum unpredictably — shrinking is no longer safe. Use prefix sums + monotonic deque instead.

```python
# Fails with negatives:
arr = [2, -1, 2], target = 3
# Window [2,-1,2] sum=3 → shrink → remove 2 → sum=1 < 3 → stop
# But window [2,-1,2] length 3 is wrong; answer is the whole array, length 3.
# Luckily this one works — but arr=[3, -2, 4], target=4:
# [3,-2,4] sum=5 → shrink: remove 3 → sum=2 < 4 → stop. Result=3.
# Correct: window [-2,4] doesn't work, [3] doesn't work either. Only [3,-2,4] or [4] (len=1). Bug.
```

**Why:** Sliding window relies on the invariant that adding elements to the right always "helps" and removing from the left always "hurts" (or vice versa). Negative numbers break this monotonicity.

**Time:** depends on alternative | **Space:** depends on alternative
</details>

---

## Intermediate Questions

---

<a id="q9"></a>
### Q9 — Longest Substring Without Repeating Characters

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Given a string `s`, return the length of the longest substring that contains no repeated characters.

Example: `s = "abcabcbb"` → `3` (substring `"abc"`)

<details>
<summary>Hint</summary>
Use a set to track characters currently in the window. Expand `right`. If `s[right]` is already in the set, shrink `left` until the duplicate is gone, then add `s[right]`.
</details>

<details>
<summary>Answer</summary>

```python
def length_of_longest_substring(s: str) -> int:
    seen = {}   # char → last seen index
    left = 0
    max_len = 0
    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1   # jump left past the old occurrence
        seen[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len

# "abcabcbb"
# right=3 ('a'): seen['a']=0 >= left=0 → left=1
# right=4 ('b'): seen['b']=1 >= left=1 → left=2
# right=5 ('c'): seen['c']=2 >= left=2 → left=3
# right=6 ('b'): seen['b']=4 >= left=3 → left=5
# right=7 ('b'): seen['b']=6 >= left=5 → left=7
# max_len stays 3
```

**Why:** Storing the last index of each character and jumping `left = seen[ch] + 1` avoids the inner `while` loop. Each character is processed once — O(n). The invariant: `[left, right]` always contains unique characters.

**Time:** O(n) | **Space:** O(min(n, alphabet_size))
</details>

---

<a id="q10"></a>
### Q10 — Minimum Window Substring

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Given strings `s` and `t`, return the shortest substring of `s` that contains all characters of `t` (including duplicates). Return `""` if impossible.

Example: `s = "ADOBECODEBANC"`, `t = "ABC"` → `"BANC"`

<details>
<summary>Hint</summary>
Use `Counter(t)` for `need` and a `have` counter. Track `formed` — the number of distinct characters in `need` whose count in `have` meets the requirement. Expand right until `formed == required`, then shrink left to minimize, recording the window each time.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter

def min_window(s: str, t: str) -> str:
    if not t or not s:
        return ""
    need = Counter(t)
    have = Counter()
    formed = 0
    required = len(need)
    left = 0
    best = (float('inf'), 0, 0)

    for right in range(len(s)):
        ch = s[right]
        have[ch] += 1
        if ch in need and have[ch] == need[ch]:
            formed += 1
        while formed == required:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right)
            lch = s[left]
            have[lch] -= 1
            if lch in need and have[lch] < need[lch]:
                formed -= 1
            left += 1

    return s[best[1]:best[2] + 1] if best[0] != float('inf') else ""
```

**Why:** `formed` uses `==` not `>=` — this is critical. If `need['A'] = 2` and `have['A']` grows to 3, we must not count it twice. We only increment `formed` the moment `have[ch]` exactly hits `need[ch]`.

**Time:** O(|s| + |t|) | **Space:** O(|t|)
</details>

---

<a id="q11"></a>
### Q11 — Longest Subarray with Sum ≤ K

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Given `arr = [3, 1, 2, 7, 4, 2, 1, 1, 5]` and `k = 8`, find the length of the longest contiguous subarray with sum ≤ k.

<details>
<summary>Hint</summary>
Variable window. Expand right unconditionally. When the running sum exceeds k, shrink from the left until it is valid again. Record the window length after each expansion.
</details>

<details>
<summary>Answer</summary>

```python
def longest_subarray_sum_leq_k(arr: list[int], k: int) -> int:
    left = 0
    window_sum = 0
    max_len = 0
    for right in range(len(arr)):
        window_sum += arr[right]           # expand
        while window_sum > k:              # shrink until valid
            window_sum -= arr[left]
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len

# arr=[3,1,2,7,4,2,1,1,5], k=8
# right=3 (val=7): sum=13 > 8 → shrink: remove 3→10, remove 1→9, remove 2→7 (left=3)
# right=4 (val=4): sum=11 > 8 → shrink: remove 7→4 (left=4)
# ...
# Max window of length 4: [4,2,1,1] or [2,1,1,5] etc.
```

**Why:** This works because all values are non-negative — adding an element can only increase the sum. When we remove from the left, sum decreases predictably. This monotonicity is what allows sliding window shrink logic.

**Time:** O(n) | **Space:** O(1)
</details>

---

<a id="q12"></a>
### Q12 — Find All Anagrams in a String

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Given strings `s` and `p`, return all starting indices of `p`'s anagrams in `s`.

Example: `s = "cbaebabacd"`, `p = "abc"` → `[0, 6]`

<details>
<summary>Hint</summary>
Fixed window of size `len(p)`. Slide and compare character frequencies. Use a `formed` counter to avoid comparing two full dictionaries each step.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter

def find_anagrams(s: str, p: str) -> list[int]:
    if len(p) > len(s):
        return []
    need = Counter(p)
    have = Counter()
    formed = 0
    required = len(need)
    result = []
    left = 0

    for right in range(len(s)):
        ch = s[right]
        have[ch] += 1
        if ch in need and have[ch] == need[ch]:
            formed += 1
        if right - left + 1 > len(p):
            lch = s[left]
            if lch in need and have[lch] == need[lch]:
                formed -= 1
            have[lch] -= 1
            if have[lch] == 0:
                del have[lch]
            left += 1
        if formed == required:
            result.append(left)
    return result
```

**Why:** This is a fixed window (size = `len(p)`) with a frequency map. By tracking `formed`, we avoid comparing two Counter objects per step — that would add O(26) = O(1) constant but hides the intent. The `formed` pattern is the canonical anagram/permutation technique.

**Time:** O(|s| + |p|) | **Space:** O(|p|)
</details>

---

<a id="q13"></a>
### Q13 — Permutation in String

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Given strings `s1` and `s2`, return `True` if `s2` contains any permutation of `s1`.

Example: `s1 = "ab"`, `s2 = "eidbaooo"` → `True` (window `"ba"`)

<details>
<summary>Hint</summary>
A permutation check is the same as an anagram check. Use a fixed window of size `len(s1)` and track `formed`. Return True as soon as `formed == required`.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter, defaultdict

def check_inclusion(s1: str, s2: str) -> bool:
    if len(s1) > len(s2):
        return False
    need = Counter(s1)
    have = defaultdict(int)
    formed = 0
    required = len(need)
    left = 0

    for right in range(len(s2)):
        ch = s2[right]
        have[ch] += 1
        if ch in need and have[ch] == need[ch]:
            formed += 1
        if right - left + 1 > len(s1):
            lch = s2[left]
            if lch in need and have[lch] == need[lch]:
                formed -= 1
            have[lch] -= 1
            left += 1
        if formed == required:
            return True
    return False
```

**Why:** Permutation = anagram = same character frequency in a window. The fixed-window frequency-map pattern handles this in O(n). No sorting needed — sorting each window would be O(n * k log k).

**Time:** O(|s1| + |s2|) | **Space:** O(|s1|)
</details>

---

<a id="q14"></a>
### Q14 — Longest Repeating Character Replacement

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


Given string `s` and integer `k`, you can replace at most `k` characters in a window. Return the length of the longest substring you can form where all characters are the same.

Example: `s = "AABABBA"`, `k = 1` → `4`

<details>
<summary>Hint</summary>
The number of characters to replace in a window = `window_size - max_frequency_char`. If this exceeds `k`, shrink. Note: `max_freq` can only increase (or stay the same) as you slide, which is an optimization.
</details>

<details>
<summary>Answer</summary>

```python
def character_replacement(s: str, k: int) -> int:
    counts = {}
    left = 0
    max_freq = 0
    res = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        max_freq = max(max_freq, counts[ch])
        # chars to replace = window_size - max_freq
        while (right - left + 1) - max_freq > k:
            counts[s[left]] -= 1
            left += 1
        res = max(res, right - left + 1)
    return res

# "AABABBA", k=1
# At right=4 (val='B'): window="AABAB", max_freq=3 (A), replacements=5-3=2>1 → shrink
# left moves to 1: "ABAB", max_freq=3? No, still 2. 4-2=2>1 → shrink again
# left=2: "BAB", 3-2=1 ≤ 1 → valid, len=3
# Continue → answer=4
```

**Why:** `(window_size - max_freq) > k` is the shrink condition. `max_freq` is never decremented even after shrinking — this is a known optimization: we only care about windows larger than the current best, and those need at least `max_freq + 1` of the dominant character.

**Time:** O(n) | **Space:** O(26) = O(1)
</details>

---

<a id="q15"></a>
### Q15 — Minimum Size Subarray Sum

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


Given a positive integer `target` and array `nums`, find the minimal length of a contiguous subarray whose sum ≥ `target`. Return 0 if none exists.

Example: `nums = [2,3,1,2,4,3]`, `target = 7` → `2` (subarray `[4,3]`)

<details>
<summary>Hint</summary>
Variable window (shortest). Expand right unconditionally. Whenever the running sum ≥ target, record the window length, then shrink from the left and check again.
</details>

<details>
<summary>Answer</summary>

```python
def min_subarray_len(target: int, nums: list[int]) -> int:
    left = 0
    window_sum = 0
    min_len = float('inf')
    for right in range(len(nums)):
        window_sum += nums[right]
        while window_sum >= target:
            min_len = min(min_len, right - left + 1)
            window_sum -= nums[left]
            left += 1
    return 0 if min_len == float('inf') else min_len
```

**Why:** Record inside the `while` (before shrinking) because the window is valid right now. Keep shrinking as long as the sum stays valid — this finds the minimal window ending at each `right`. All values are positive so shrinking always reduces the sum predictably.

**Time:** O(n) | **Space:** O(1)
</details>

---

<a id="q16"></a>
### Q16 — Longest Substring with At Most K Distinct Characters

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Given string `s` and integer `k`, return the length of the longest substring with at most `k` distinct characters.

Example: `s = "eceba"`, `k = 2` → `3` (substring `"ece"`)

<details>
<summary>Hint</summary>
Maintain a frequency map. Expand right, adding each character. If `len(freq_map) > k`, shrink from the left, removing characters until at most k distinct remain.
</details>

<details>
<summary>Answer</summary>

```python
from collections import defaultdict

def longest_k_distinct(s: str, k: int) -> int:
    if k == 0:
        return 0
    freq = defaultdict(int)
    left = 0
    max_len = 0
    for right, ch in enumerate(s):
        freq[ch] += 1
        while len(freq) > k:
            freq[s[left]] -= 1
            if freq[s[left]] == 0:
                del freq[s[left]]
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len

# "eceba", k=2
# right=2: freq={'e':2,'c':1}, len=2 ≤ 2, max=3
# right=3 ('b'): freq={'e':2,'c':1,'b':1}, len=3 > 2
#   → shrink: remove 'e'(left=0) → {'e':1,'c':1,'b':1} still 3
#   → shrink: remove 'c'(left=1) → {'e':1,'b':1} len=2, left=2, max stays 3
```

**Why:** Delete keys from the dict when their count hits 0 — otherwise `len(freq)` gives wrong distinct count. The invariant: at every step, `freq` contains exactly the characters in `[left, right]`, with correct counts.

**Time:** O(n) | **Space:** O(k)
</details>

---

<a id="q17"></a>
### Q17 — Shrink vs Expand — Which Loop?

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


Explain the difference between these two shrink patterns:

```python
# Pattern A
while constraint_violated(window):
    remove(s[left]); left += 1
result = max(result, right - left + 1)

# Pattern B
while constraint_satisfied(window):
    result = min(result, right - left + 1)
    remove(s[left]); left += 1
```

When do you use Pattern A vs Pattern B?

<details>
<summary>Hint</summary>
Think about whether you are looking for the longest or shortest window. Where in the loop do you record the answer?
</details>

<details>
<summary>Answer</summary>

**Pattern A — use for longest window:**
Shrink until the window is valid again, then record. You record after shrinking because you want the valid window.

```python
# Longest substring without repeating chars
while s[right] in window_set:
    window_set.remove(s[left]); left += 1
window_set.add(s[right])
max_len = max(max_len, right - left + 1)  # record after fix
```

**Pattern B — use for shortest window:**
The window is valid right now. Record it, then shrink to try to find something smaller. Continue shrinking as long as the window remains valid.

```python
# Minimum size subarray with sum >= target
while window_sum >= target:
    min_len = min(min_len, right - left + 1)  # record while valid
    window_sum -= arr[left]; left += 1
```

**Why:** The key insight is: for "longest", validity is the goal, so record after restoring validity. For "shortest", you have a valid window and want to shrink it further, so record before shrinking.

**Time:** O(n) both | **Space:** O(1) or O(k)
</details>

---

<a id="q18"></a>
### Q18 — Max Consecutive Ones III

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Given binary array `nums` and integer `k`, return the max number of consecutive 1s if you can flip at most `k` zeros.

Example: `nums = [1,1,1,0,0,0,1,1,1,1,0]`, `k = 2` → `6`

<details>
<summary>Hint</summary>
Track the number of zeros in the current window. Shrink when zeros exceed k. This is equivalent to "longest subarray with at most k zeros."
</details>

<details>
<summary>Answer</summary>

```python
def longest_ones(nums: list[int], k: int) -> int:
    left = 0
    zeros = 0
    max_len = 0
    for right in range(len(nums)):
        if nums[right] == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len

# [1,1,1,0,0,0,1,1,1,1,0], k=2
# When zeros > 2: shrink left
# Longest valid window: [0,0,1,1,1,1] with 2 zeros → length 6
```

**Why:** Flipping zeros = tolerating zeros in the window. The shrink condition is `zeros > k`. This is Pattern A (longest window). Clean, no frequency map needed since we only track one type.

**Time:** O(n) | **Space:** O(1)
</details>

---

<a id="q19"></a>
### Q19 — Subarray Product Less Than K

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Given `nums` and `k`, count the number of contiguous subarrays where the product of all elements is strictly less than `k`.

Example: `nums = [10, 5, 2, 6]`, `k = 100` → `8`

<details>
<summary>Hint</summary>
Variable window with a running product. Expand right. When product ≥ k, shrink left. After shrinking, the number of valid subarrays ending at `right` is `right - left + 1`.
</details>

<details>
<summary>Answer</summary>

```python
def num_subarray_product_less_than_k(nums: list[int], k: int) -> int:
    if k <= 1:
        return 0
    product = 1
    left = 0
    count = 0
    for right in range(len(nums)):
        product *= nums[right]
        while product >= k and left <= right:
            product //= nums[left]
            left += 1
        count += right - left + 1   # subarrays ending at right, starting from left..right
    return count

# [10,5,2,6], k=100
# right=0: product=10 < 100, count += 1 (just [10])
# right=1: product=50 < 100, count += 2 ([5],[10,5])
# right=2: product=100 ≥ 100 → shrink: /10 → 10, left=1. count += 2 ([2],[5,2])
# right=3: product=60 < 100, count += 3 ([6],[2,6],[5,2,6])
# total = 1+2+2+3 = 8
```

**Why:** After shrinking, the window `[left, right]` is valid. All subarrays ending at `right` that start at any position from `left` to `right` are valid — that's `right - left + 1` subarrays. This counting trick avoids enumerating each subarray.

**Time:** O(n) | **Space:** O(1)
</details>

---

<a id="q20"></a>
### Q20 — Count Distinct Characters in Every Window

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


Given string `s = "aabacbebebe"` and `k = 5`, return the maximum number of distinct characters in any window of size `k`.

<details>
<summary>Hint</summary>
Fixed window with a frequency map. `len(freq_map)` gives the count of distinct characters. Expand until window is full, slide by removing left and adding right.
</details>

<details>
<summary>Answer</summary>

```python
def max_distinct_in_window(s: str, k: int) -> int:
    freq = {}
    for ch in s[:k]:
        freq[ch] = freq.get(ch, 0) + 1
    max_distinct = len(freq)

    for i in range(k, len(s)):
        # add new right character
        new_ch = s[i]
        freq[new_ch] = freq.get(new_ch, 0) + 1
        # remove old left character
        old_ch = s[i - k]
        freq[old_ch] -= 1
        if freq[old_ch] == 0:
            del freq[old_ch]
        max_distinct = max(max_distinct, len(freq))

    return max_distinct

# s="aabacbebebe", k=5
# Windows of 5 chars, track distinct count
# "aabac" → {a:3,b:1,c:1} → 3 distinct
# "abacb" → {a:2,b:2,c:1} → 3 distinct
# "bacbe" → {b:2,a:1,c:1,e:1} → 4 distinct
# ...
```

**Why:** Deleting keys when count hits 0 is essential — `len(freq)` must equal the number of currently present distinct characters. Fixed-window sliding: add right element, remove left element, update answer.

**Time:** O(n) | **Space:** O(k)
</details>

---

## Advanced Questions

---

<a id="q21"></a>
### Q21 — Sliding Window Maximum (Deque)

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Given `nums = [1, 3, -1, -3, 5, 3, 6, 7]` and `k = 3`, return the maximum value in each window of size `k`.

Expected output: `[3, 3, 5, 5, 6, 7]`

<details>
<summary>Hint</summary>
Use a monotonic decreasing deque of indices. Before adding `i` to the deque, pop from the back any index whose value is strictly less than `nums[i]` — those values can never be a future maximum. Always evict indices from the front that fall outside the window.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

def sliding_window_maximum(nums: list[int], k: int) -> list[int]:
    dq = deque()   # indices, monotonically decreasing value
    result = []
    for i in range(len(nums)):
        # evict from back: values smaller than current can never be max
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()
        dq.append(i)
        # evict from front: index outside current window
        if dq[0] < i - k + 1:
            dq.popleft()
        # record once window is full
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result

# i=0: dq=[0]
# i=1: nums[0]=1 < 3 → pop 0. dq=[1]
# i=2: nums[1]=3 > -1 → keep. dq=[1,2]. Full → result=[3]
# i=3: nums[2]=-1 > -3 → keep. dq=[1,2,3]. Front ok. result=[3,3]
# i=4: pop 3(-3<5), pop 2(-1<5), pop 1(3<5). dq=[4]. result=[3,3,5]
# ...
```

**Why:** Pop with `<` (strictly less), not `<=`. Keeping equals preserves the earlier index at the front, which correctly represents the maximum when both values are equal. Each element is pushed and popped once — O(n).

**Time:** O(n) | **Space:** O(k)
</details>

---

<a id="q22"></a>
### Q22 — Minimum Window Substring with Duplicates in T

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


Why does using `set(t)` instead of `Counter(t)` fail for `t = "AA"`? Show the bug and the fix.

<details>
<summary>Hint</summary>
A set records presence but not quantity. `set("AA")` gives `{'A'}` — it cannot distinguish "need one A" from "need two As."
</details>

<details>
<summary>Answer</summary>

```python
# BUGGY — using set ignores duplicate requirement
def min_window_wrong(s: str, t: str) -> str:
    need = set(t)          # set("AA") = {'A'} — quantity lost
    satisfied = set()
    window_counts = {}
    left = 0
    result, min_len = "", float('inf')
    for right in range(len(s)):
        ch = s[right]
        window_counts[ch] = window_counts.get(ch, 0) + 1
        if ch in need:
            satisfied.add(ch)   # marks 'A' done after seeing ONE, even if need TWO
        while satisfied == need:
            if right - left + 1 < min_len:
                min_len = right - left + 1
                result = s[left:right + 1]
            lch = s[left]
            window_counts[lch] -= 1
            if lch in need and window_counts[lch] == 0:
                satisfied.discard(lch)
            left += 1
    return result

# s="XAAX", t="AA" → need={'A'}, sees first 'A' → satisfied → returns "XA" (WRONG)
# Correct answer is "AA"

# CORRECT — using Counter tracks quantities
from collections import Counter
def min_window_correct(s: str, t: str) -> str:
    need = Counter(t)          # Counter("AA") = {'A': 2}
    have = Counter()
    formed = 0
    required = len(need)
    left = 0
    best = (float('inf'), 0, 0)
    for right in range(len(s)):
        ch = s[right]
        have[ch] += 1
        if ch in need and have[ch] == need[ch]:
            formed += 1
        while formed == required:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right)
            lch = s[left]
            have[lch] -= 1
            if lch in need and have[lch] < need[lch]:
                formed -= 1
            left += 1
    return s[best[1]:best[2]+1] if best[0] != float('inf') else ""
```

**Why:** `set` answers "which characters?" — `Counter` answers "how many of each?" Always use `Counter(t)` when the problem involves required frequencies. This is a silent bug: the code runs without error but returns wrong results.

**Time:** O(|s| + |t|) | **Space:** O(|t|)
</details>

---

<a id="q23"></a>
### Q23 — Longest Subarray After Deleting One Element

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Given a binary array `nums`, return the length of the longest subarray of 1s after deleting exactly one element.

Example: `nums = [1,1,0,1]` → `3`

<details>
<summary>Hint</summary>
You must delete exactly one element, so you can have at most one 0 in your window. This is similar to Max Consecutive Ones III with k=1, but the deleted element counts against the window size (subtract 1 from the final answer).
</details>

<details>
<summary>Answer</summary>

```python
def longest_subarray(nums: list[int]) -> int:
    # Allow at most 1 zero in window (the element we'll delete)
    left = 0
    zeros = 0
    max_len = 0
    for right in range(len(nums)):
        if nums[right] == 0:
            zeros += 1
        while zeros > 1:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        # subtract 1 because we must delete one element
        max_len = max(max_len, right - left)  # right - left, not +1
    return max_len

# [1,1,0,1]: window [1,1,0,1] has 1 zero, length 4-1=3 ✓
# [0,1,1,1,0,1,1,0,1]: longest window with ≤1 zero has length 5
#   e.g. [1,1,1,0,1] → delete the 0 → 4 ones
```

**Why:** The window with at most 1 zero has length `right - left + 1`. But we must delete exactly one element (the 0 or any 1). Subtracting 1 accounts for the mandatory deletion. If the window has no zeros (all 1s), we still delete one — hence `right - left` not `right - left + 1`.

**Time:** O(n) | **Space:** O(1)
</details>

---

<a id="q24"></a>
### Q24 — Sliding Window + Binary Search

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


The array `nums` is sorted. Find the smallest window size `w` such that there exists a contiguous subarray of length `w` with sum ≥ target. Use binary search on `w`, with a fixed sliding window to check feasibility.

<details>
<summary>Hint</summary>
Binary search on the answer `w` from 1 to n. For each candidate `w`, use a fixed-size sliding window to check if any window of that size has sum ≥ target. The feasibility check is monotonic: if `w` works, `w+1` also works.
</details>

<details>
<summary>Answer</summary>

```python
def smallest_window_size(nums: list[int], target: int) -> int:
    n = len(nums)

    def feasible(w: int) -> bool:
        # Check if any window of size w has sum >= target
        window_sum = sum(nums[:w])
        if window_sum >= target:
            return True
        for i in range(w, n):
            window_sum += nums[i] - nums[i - w]
            if window_sum >= target:
                return True
        return False

    lo, hi = 1, n
    if not feasible(n):
        return 0   # impossible
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo

# nums=[1,2,3,4,5], target=11
# feasible(1): max single element 5 < 11 → False
# feasible(2): max [4,5]=9 < 11 → False
# feasible(3): max [3,4,5]=12 >= 11 → True
# Binary search finds 3
```

**Why:** The feasibility is monotonic — if a window of size `w` works, any larger window also works. Binary search on monotonic predicates is O(log n). Each feasibility check is O(n). Total: O(n log n). This is worse than the direct variable-window O(n) for positive arrays, but demonstrates the combination pattern for cases where direct variable windows don't work (e.g., mixed positives/negatives).

**Time:** O(n log n) | **Space:** O(1)
</details>

---

<a id="q25"></a>
### Q25 — Number of Subarrays with Bounded Maximum

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


Given `nums`, `left_bound`, and `right_bound`, count subarrays where the maximum element is between `left_bound` and `right_bound` inclusive.

Example: `nums = [2, 1, 4, 3]`, `left_bound = 2`, `right_bound = 3` → `3`

<details>
<summary>Hint</summary>
Use the formula: count(max ≤ right_bound) - count(max ≤ left_bound - 1). For "count of subarrays with max ≤ limit", use a sliding window: reset left pointer whenever an element exceeds the limit.
</details>

<details>
<summary>Answer</summary>

```python
def num_subarray_bounded_max(nums: list[int], left_bound: int, right_bound: int) -> int:

    def count_at_most(limit: int) -> int:
        """Count subarrays where max element <= limit."""
        count = 0
        left = 0
        for right in range(len(nums)):
            if nums[right] > limit:
                left = right + 1   # reset: any subarray including this is invalid
            count += right - left + 1  # valid subarrays ending at right
        return count

    return count_at_most(right_bound) - count_at_most(left_bound - 1)

# nums=[2,1,4,3], L=2, R=3
# count_at_most(3): 4 appears at index 2 → left resets to 3
#   right=0: [2], count+=1=1
#   right=1: [1],[2,1], count+=2=3
#   right=2: 4>3 → left=3. count+=0=3
#   right=3: [3], count+=1=4
# count_at_most(1): 2 at index 0 → left=1, 4 at index 2 → left=3, 3 at index 3 → left=4
#   right=0: 2>1 → left=1. count+=0=0
#   right=1: [1], count+=1=1
#   right=2: 4>1 → left=3. count+=0=1
#   right=3: 3>1 → left=4. count+=0=1
# Answer: 4 - 1 = 3
```

**Why:** Direct enumeration is O(n²). The "at most" trick converts a range problem into two simpler "at most limit" problems. The sliding window resets `left` whenever an element exceeds the limit, making each subarray ending at `right` countable in O(1).

**Time:** O(n) | **Space:** O(1)
</details>

---

## Navigation

**[Back to README](../README.md)**

**Prev:** [Interview Q&A](./interview.md) | **Next:** [Binary Search — Theory](../13_binary_search/theory.md)

**Related:** [Theory](./theory.md) · [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Common Mistakes](./common_mistakes.md) · [Practice Local](./practice_local.py)
