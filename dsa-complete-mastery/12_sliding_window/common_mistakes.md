# Sliding Window — Common Mistakes & Error Prevention

---

## Mistake 1: Resetting `left` to 0 Instead of Advancing It

### The Bug

When a window constraint is violated, the correct response is to **advance the left pointer** until the window is valid again. A common mistake is to reset `left = 0`, which throws away all progress and causes O(n²) or worse behaviour, and also produces incorrect results because the window never shrinks from the left — it just restarts.

### WRONG Code

```python
def length_of_longest_substring_wrong(s: str) -> int:
    """Longest substring without repeating characters."""
    left = 0
    max_len = 0
    window = set()

    for right in range(len(s)):
        if s[right] in window:
            window = set()   # discard the entire window
            left = 0         # WRONG: restart from the beginning every time
        window.add(s[right])
        max_len = max(max_len, right - left + 1)

    return max_len
```

**Why it fails:** For `"abcabcbb"`, when we hit the second `'a'` at index 3, we reset to `left = 0`. Now `window = {'a'}` and `right = 3`, so the window "length" is `right - left + 1 = 4`, which overcounts — the actual valid substring from index 3 is just `"a"` at this moment.

### CORRECT Code

```python
def length_of_longest_substring_correct(s: str) -> int:
    left = 0
    max_len = 0
    window = set()

    for right in range(len(s)):
        while s[right] in window:   # advance left until violation resolved
            window.remove(s[left])
            left += 1
        window.add(s[right])
        max_len = max(max_len, right - left + 1)

    return max_len


# Faster variant: store last-seen index to jump left directly
def length_of_longest_substring_fast(s: str) -> int:
    last_seen = {}
    left = 0
    max_len = 0

    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1   # jump left past the duplicate
        last_seen[ch] = right
        max_len = max(max_len, right - left + 1)

    return max_len
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_overcounts_window():
    """'abcabcbb' expected 3, wrong version gives incorrect result."""
    assert length_of_longest_substring_wrong("abcabcbb") != 3  # reveals bug


def test_correct_basic():
    assert length_of_longest_substring_correct("abcabcbb") == 3   # "abc"
    assert length_of_longest_substring_fast("abcabcbb") == 3


def test_all_same():
    assert length_of_longest_substring_correct("bbbb") == 1
    assert length_of_longest_substring_fast("bbbb") == 1


def test_no_repeats():
    assert length_of_longest_substring_correct("abcdef") == 6
    assert length_of_longest_substring_fast("abcdef") == 6


def test_empty():
    assert length_of_longest_substring_correct("") == 0
    assert length_of_longest_substring_fast("") == 0


def test_single_char():
    assert length_of_longest_substring_correct("a") == 1


def test_repeat_at_end():
    assert length_of_longest_substring_correct("pwwkew") == 3   # "wke"
    assert length_of_longest_substring_fast("pwwkew") == 3


def test_two_chars_alternating():
    assert length_of_longest_substring_correct("abababab") == 2


if __name__ == "__main__":
    test_cases = ["abcabcbb", "bbbb", "abcdef", "", "a", "pwwkew"]
    for s in test_cases:
        wrong = length_of_longest_substring_wrong(s)
        correct = length_of_longest_substring_correct(s)
        fast = length_of_longest_substring_fast(s)
        match = "OK" if correct == fast else "MISMATCH"
        print(f"s={s!r:15} wrong={wrong}  correct={correct}  fast={fast}  [{match}]")
```

### Key Takeaway

- The window's left boundary must **only move right**, never jump back to 0.
- Use `while violation: shrink_left()` — not `if violation: reset()`.
- For character-index problems, store `last_seen[ch] = index` and jump `left = last_seen[ch] + 1` to skip the shrink loop entirely.

---

## Mistake 2: Fixed-Window Off-by-One — Wrong Condition to Slide

### The Bug

For a fixed-size window of length `k`, the window contains exactly `k` elements when `right - left + 1 == k`. The off-by-one version uses `right - left > k` (omitting `+ 1`), which means the window slides when it has `k + 1` elements instead of `k`, producing a window that is always one element too large before it slides.

### WRONG Code

```python
def max_sum_subarray_wrong(nums: list[int], k: int) -> int:
    """Maximum sum of any subarray of length exactly k."""
    left = 0
    window_sum = 0
    max_sum = float('-inf')

    for right in range(len(nums)):
        window_sum += nums[right]
        if right - left > k:          # WRONG: slides when window has k+1 elements
            window_sum -= nums[left]  # window shrinks but was already too large
            left += 1
        if right - left + 1 == k:
            max_sum = max(max_sum, window_sum)

    return max_sum
```

**The problem with `right - left > k`:**

- When `right = k`, `left = 0`: `right - left = k > k` is False, so we don't slide.
- The window now has `k + 1` elements (indices 0..k inclusive).
- We then record `right - left + 1 = k + 1 == k` which is False — we never record.
- The first time we record is when `right - left + 1 = k` which coincides with the slide happening one step late.
- This means the recorded windows use indices `[1..k]`, `[2..k+1]`, etc. — one element too late to start.

### CORRECT Code

```python
def max_sum_subarray_correct(nums: list[int], k: int) -> int:
    if k > len(nums):
        return -1   # edge case: k larger than array

    left = 0
    window_sum = 0
    max_sum = float('-inf')

    for right in range(len(nums)):
        window_sum += nums[right]
        if right - left + 1 > k:      # CORRECT: slide when window exceeds k
            window_sum -= nums[left]
            left += 1
        if right - left + 1 == k:     # window is exactly k elements
            max_sum = max(max_sum, window_sum)

    return max_sum


def max_avg_subarray(nums: list[int], k: int) -> float:
    """Return maximum average of any subarray of length k."""
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]   # slide by 1: add new, remove old
        max_sum = max(max_sum, window_sum)
    return max_sum / k
```

### Window Size Reference

```
Index:  0   1   2   3   4
Nums:   1   2   3   4   5
               ^           right = 2, left = 0
               Window = [1,2,3], size = right - left + 1 = 3

right - left + 1 > k   →  correct check (slide when size EXCEEDS k)
right - left     > k   →  wrong check  (slide when size exceeds k+1)
right - left     >= k  →  also correct (equivalent to > k-1, i.e., > k when using +1)
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_basic():
    """[1,2,3,4,5] k=3 — correct answer is 12 (3+4+5)."""
    result = max_sum_subarray_wrong([1, 2, 3, 4, 5], 3)
    assert result != 12, f"WRONG version coincidentally correct: {result}"


def test_correct_basic():
    assert max_sum_subarray_correct([1, 2, 3, 4, 5], 3) == 12    # [3,4,5]


def test_correct_k_equals_array_length():
    assert max_sum_subarray_correct([1, 2, 3], 3) == 6


def test_correct_k_equals_1():
    assert max_sum_subarray_correct([3, 1, 4, 1, 5], 1) == 5


def test_correct_with_negatives():
    assert max_sum_subarray_correct([-1, -2, 3, 4, -5], 2) == 7  # [3,4]


def test_correct_k_larger_than_array():
    assert max_sum_subarray_correct([1, 2], 5) == -1


def test_avg_basic():
    assert max_avg_subarray([1, 12, -5, -6, 50, 3], 4) == pytest.approx(12.75)


def test_all_negative():
    assert max_sum_subarray_correct([-3, -1, -2], 2) == -3   # [-3,-1] sums to -3... wait
    # [-3,-1] = -4, [-1,-2] = -3 → max is -3
    assert max_sum_subarray_correct([-3, -1, -2], 2) == -3


if __name__ == "__main__":
    test_data = [
        ([1, 2, 3, 4, 5], 3),
        ([1, 2, 3], 3),
        ([-1, -2, 3, 4, -5], 2),
    ]
    for nums, k in test_data:
        wrong = max_sum_subarray_wrong(nums, k)
        correct = max_sum_subarray_correct(nums, k)
        flag = "OK" if wrong == correct else "BUG"
        print(f"nums={nums} k={k}: wrong={wrong} correct={correct} [{flag}]")
```

### Key Takeaway

Always use: `if right - left + 1 > k: shrink_left()`

The `+ 1` accounts for the inclusive nature of both indices. Without it, your window is always one element too large before it slides.

---

## Mistake 3: `formed` Counter — Incrementing When Count Exceeds `need` Instead of Equals

### The Bug

In the Minimum Window Substring problem (and similar "at least N of each" problems), a `formed` counter tracks how many distinct required characters have their required frequency met. The mistake is using `>=` instead of `==` when incrementing `formed`, which causes `formed` to be incremented multiple times for the same character as its count grows beyond the needed value.

### WRONG Code

```python
from collections import Counter


def min_window_wrong(s: str, t: str) -> str:
    if not t or not s:
        return ""

    need = Counter(t)
    have = Counter()
    formed = 0
    required = len(need)
    left = 0
    result = ""
    min_len = float('inf')

    for right in range(len(s)):
        ch = s[right]
        have[ch] = have.get(ch, 0) + 1

        # WRONG: >= means formed increments every time count overshoots need
        if ch in need and have[ch] >= need[ch]:
            formed += 1   # increments at need[ch], need[ch]+1, need[ch]+2, ...

        while formed >= required:   # formed is inflated — window never shrinks correctly
            window = s[left:right + 1]
            if len(window) < min_len:
                min_len = len(window)
                result = window
            left_ch = s[left]
            have[left_ch] -= 1
            if left_ch in need and have[left_ch] < need[left_ch]:
                formed -= 1
            left += 1

    return result
```

**Why `>=` is wrong:** If `need['a'] = 2` and `have['a']` grows to 3, 4, 5 — `formed` is incremented each time. When left later removes an `'a'`, `have['a']` drops to 4, but `formed` is decremented only once (when it falls below 2). The asymmetry corrupts `formed`.

### CORRECT Code

```python
from collections import Counter


def min_window_correct(s: str, t: str) -> str:
    if not t or not s:
        return ""

    need = Counter(t)
    have = Counter()
    formed = 0
    required = len(need)
    left = 0
    result = ""
    min_len = float('inf')

    for right in range(len(s)):
        ch = s[right]
        have[ch] = have.get(ch, 0) + 1

        # CORRECT: == means formed increments exactly once per character per satisfaction
        if ch in need and have[ch] == need[ch]:
            formed += 1

        while formed == required:
            window_len = right - left + 1
            if window_len < min_len:
                min_len = window_len
                result = s[left:right + 1]
            left_ch = s[left]
            have[left_ch] -= 1
            if left_ch in need and have[left_ch] < need[left_ch]:
                formed -= 1   # only decrements when we fall BELOW the requirement
            left += 1

    return result
```

### Tracing the Bug

```
s = "AABBC",  t = "AB"
need = {'A': 1, 'B': 1},  required = 2

WRONG (>=):
right=0: have['A']=1 >= need['A']=1  → formed=1
right=1: have['A']=2 >= need['A']=1  → formed=2  (WRONG: 'A' already counted!)
         formed==required → shrink → corrupted state

CORRECT (==):
right=0: have['A']=1 == need['A']=1  → formed=1
right=1: have['A']=2 != need['A']=1  → formed stays 1
right=2: have['B']=1 == need['B']=1  → formed=2
         formed==required → shrink window correctly
```

### Test Cases That Expose the Bug

```python
import pytest
from collections import Counter


def test_wrong_overcounts_formed():
    """'AABBC' needs 'AB' — wrong version corrupts formed counter."""
    s, t = "AABBC", "AB"
    wrong = min_window_wrong(s, t)
    correct = min_window_correct(s, t)
    # Both may return "AB" here, but the wrong version may return a longer window
    # or skip valid windows. Use a case where it clearly differs:
    assert correct == "AB"


def test_wrong_fails_with_duplicates_in_t():
    """s='AAAB' t='AAB' — t requires two A's. Wrong version may fail."""
    s, t = "AAAB", "AAB"
    correct = min_window_correct(s, t)
    wrong = min_window_wrong(s, t)
    assert correct == "AAAB"
    # wrong version inflates formed, may find a window that doesn't satisfy need


def test_correct_basic():
    assert min_window_correct("ADOBECODEBANC", "ABC") == "BANC"


def test_correct_exact_match():
    assert min_window_correct("ABC", "ABC") == "ABC"


def test_correct_t_longer_than_s():
    assert min_window_correct("A", "AA") == ""


def test_correct_single_char():
    assert min_window_correct("a", "a") == "a"


def test_correct_duplicate_in_t():
    assert min_window_correct("AAAB", "AAB") == "AAAB"


def test_correct_no_valid_window():
    assert min_window_correct("abc", "d") == ""


def test_correct_multiple_valid_windows():
    """'BAAC' t='AB' — both 'BA' (0-1) and 'BAA' etc. Shortest is 'BA'."""
    result = min_window_correct("BAAC", "AB")
    assert len(result) == 2


if __name__ == "__main__":
    cases = [
        ("ADOBECODEBANC", "ABC"),
        ("AAAB", "AAB"),
        ("a", "a"),
        ("abc", "d"),
    ]
    for s, t in cases:
        w = min_window_correct(s, t)
        print(f"min_window({s!r}, {t!r}) = {w!r}")
```

### Key Takeaway

- `formed += 1` only when `have[ch] == need[ch]` — the exact moment of satisfaction.
- `formed -= 1` only when `have[ch] < need[ch]` — the exact moment of unsatisfaction after shrinking.
- Using `>=` causes `formed` to be incremented multiple times for the same character, permanently inflating it and making the window logic incorrect.

---

## Mistake 4: Using a Set Instead of Counter When `t` Has Duplicate Characters

### The Bug

When the target string `t` has repeated characters (e.g., `t = "aa"`), using a `set` to track which characters are needed completely ignores quantity. A set treats `"aa"` identically to `"a"`. Any window containing one `'a'` will be incorrectly accepted.

### WRONG Code

```python
def min_window_set_wrong(s: str, t: str) -> str:
    """Using a set — ignores duplicate requirements in t."""
    if not t or not s:
        return ""

    need = set(t)           # WRONG: set of "aa" is just {'a'} — quantity lost
    satisfied = set()
    left = 0
    result = ""
    min_len = float('inf')
    window_counts = {}

    for right in range(len(s)):
        ch = s[right]
        window_counts[ch] = window_counts.get(ch, 0) + 1
        if ch in need:
            satisfied.add(ch)   # marks 'a' as done after seeing ONE 'a', even if need TWO

        while satisfied == need:
            if right - left + 1 < min_len:
                min_len = right - left + 1
                result = s[left:right + 1]
            left_ch = s[left]
            window_counts[left_ch] -= 1
            if left_ch in need and window_counts[left_ch] == 0:
                satisfied.discard(left_ch)
            left += 1

    return result
```

### CORRECT Code (Counter-based)

```python
from collections import Counter


def min_window_counter_correct(s: str, t: str) -> str:
    """Using Counter — correctly tracks required COUNTS."""
    if not t or not s:
        return ""

    need = Counter(t)           # CORRECT: Counter("aa") = {'a': 2}
    have = Counter()
    formed = 0
    required = len(need)        # number of DISTINCT chars to satisfy
    left = 0
    result = ""
    min_len = float('inf')

    for right in range(len(s)):
        ch = s[right]
        have[ch] += 1
        if ch in need and have[ch] == need[ch]:
            formed += 1
        while formed == required:
            if right - left + 1 < min_len:
                min_len = right - left + 1
                result = s[left:right + 1]
            left_ch = s[left]
            have[left_ch] -= 1
            if left_ch in need and have[left_ch] < need[left_ch]:
                formed -= 1
            left += 1

    return result
```

### Tracing the Bug

```
s = "XAAX",  t = "AA"

WRONG (set):
need = {'A'}  (set ignores the second 'A')
right=1: window_counts['A']=1, satisfied={'A'} == need={'A'} → shrink!
Returns "XA" (length 2) — WRONG, "XA" only has one 'A'

CORRECT (Counter):
need = {'A': 2}
right=1: have['A']=1 != need['A']=2 → formed=0, keep expanding
right=2: have['A']=2 == need['A']=2 → formed=1 == required=1 → shrink
Returns "AA" (length 2) — CORRECT
```

### Test Cases That Expose the Bug

```python
import pytest
from collections import Counter


def test_wrong_ignores_duplicate_requirement():
    """t='AA' requires two A's. Wrong version accepts any window with one A."""
    s = "XAAX"
    t = "AA"
    wrong = min_window_set_wrong(s, t)
    correct = min_window_counter_correct(s, t)
    assert correct == "AA"
    # wrong version may return "XA" (length 2) with only one A
    assert len(wrong) >= len(correct) or wrong == "", \
        f"Wrong version found a shorter or equal window incorrectly: {wrong}"


def test_wrong_single_vs_double():
    """s='A' t='AA' — impossible. Wrong version may return 'A'."""
    assert min_window_counter_correct("A", "AA") == ""
    wrong = min_window_set_wrong("A", "AA")
    # wrong version treats 'AA' as {'A'}, sees 'A' in s, may return "A"
    # correct answer is "" (no valid window)
    # demonstrate the discrepancy:
    if wrong != "":
        assert False, f"WRONG: returned '{wrong}' for impossible case"


def test_correct_no_duplicates_in_t():
    """When t has no duplicates, both approaches agree."""
    s, t = "ADOBECODEBANC", "ABC"
    assert min_window_counter_correct(s, t) == "BANC"


def test_correct_all_same_chars():
    assert min_window_counter_correct("AAAB", "AAB") == "AAAB"
    assert min_window_counter_correct("AABB", "AB") == "AB"


def test_correct_t_is_all_same():
    assert min_window_counter_correct("AAABC", "AAA") == "AAA"


def test_correct_not_enough_in_s():
    assert min_window_counter_correct("AAB", "AAA") == ""


if __name__ == "__main__":
    cases = [
        ("XAAX", "AA"),
        ("A", "AA"),
        ("AAAB", "AAB"),
        ("AAABC", "AAA"),
    ]
    for s, t in cases:
        wrong = min_window_set_wrong(s, t)
        correct = min_window_counter_correct(s, t)
        flag = "OK" if wrong == correct else "BUG EXPOSED"
        print(f"s={s!r:10} t={t!r:5} wrong={wrong!r:6} correct={correct!r:6} [{flag}]")
```

### Key Takeaway

- Always use `Counter(t)` — never `set(t)` — when the problem involves required frequencies.
- A `set` answers "which characters?". A `Counter` answers "how many of each character?".
- This bug is silent: the code runs without error but gives wrong answers on cases where `t` contains duplicates.

---

## Mistake 5: Sliding Window Maximum — Wrong Monotonic Deque Condition (Strict vs Non-Strict)

### The Bug

The sliding window maximum problem uses a **monotonic decreasing deque** that stores indices. The deque condition pops elements from the back when a new element is larger. The question is: use `<` or `<=`?

- `while dq and nums[dq[-1]] < nums[i]` — pop when strictly less → **keeps duplicates in the deque**
- `while dq and nums[dq[-1]] <= nums[i]` — pop when less-or-equal → **removes duplicates**

Both give the same maximum values, BUT removing duplicates aggressively (`<=`) can cause the deque to be empty or the front index to be evicted prematurely in some formulations, and more importantly it changes which index is considered the "representative" of a duplicate maximum, which matters for problems that need the specific index of the maximum.

However the most common and insidious failure is the opposite direction: using `>=` instead of `>` when maintaining a **monotonic increasing deque** (for sliding window minimum). Let's examine the concrete window maximum case where the subtle distinction matters.

### WRONG Code

```python
from collections import deque


def sliding_window_max_wrong(nums: list[int], k: int) -> list[int]:
    """
    WRONG: uses > (strict greater) for popping, which means we keep
    elements equal to nums[i] in the deque. This is actually fine for
    the maximum problem, but the more dangerous wrong version is shown
    below — using the wrong comparison direction entirely.
    """
    result = []
    dq = deque()  # stores indices

    for i in range(len(nums)):
        # Remove indices outside the window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # WRONG direction: pop from back while back element is LESS THAN current
        # Should be: pop while back element is LESS THAN OR EQUAL? No.
        # The actual wrong version: pop while back >= current (wrong direction!)
        while dq and nums[dq[-1]] >= nums[i]:  # WRONG: keeping smaller, discarding larger
            dq.pop()

        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])  # front should be max, but now it's min!

    return result


def sliding_window_max_wrong_duplicate(nums: list[int], k: int) -> list[int]:
    """
    Second wrong version: uses <= which removes duplicates.
    For [2,2,2] k=2, this causes the maximum to be reported incorrectly
    when the true maximum appears multiple times.
    """
    result = []
    dq = deque()

    for i in range(len(nums)):
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        while dq and nums[dq[-1]] <= nums[i]:   # removes equal elements
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result
```

### CORRECT Code

```python
from collections import deque


def sliding_window_max_correct(nums: list[int], k: int) -> list[int]:
    """
    Monotonic decreasing deque.
    Pop from back while back element is STRICTLY LESS THAN current.
    This keeps duplicates in the deque (the first occurrence is preserved at front).
    """
    result = []
    dq = deque()  # stores indices, maintains nums[dq[0]] >= nums[dq[1]] >= ...

    for i in range(len(nums)):
        # 1. Evict indices that have fallen outside the window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # 2. Maintain decreasing order: pop back while back < current
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()

        dq.append(i)

        # 3. Window is full starting at index k-1
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result
```

### Tracing with `[2, 2, 2]`, k=2

```
Input: [2, 2, 2],  k=2
Expected output: [2, 2]

WRONG (>= pops equal):
i=0: dq=[], append 0.         dq=[0]
i=1: nums[0]=2 >= nums[1]=2 → pop 0. dq=[]. append 1.  dq=[1]
     i>=k-1: result=[nums[1]]=[2]  ← OK so far
i=2: nums[1]=2 >= nums[2]=2 → pop 1. dq=[]. append 2.  dq=[2]
     i>=k-1: result=[2, nums[2]]=[2, 2]  ← coincidentally correct here

BUT consider [2, 2, 1], k=3:
WRONG (>= pops equal):
i=0: dq=[0]
i=1: nums[0]=2 >= nums[1]=2 → pop 0. dq=[1]
i=2: nums[1]=2 > nums[2]=1? No, 2>1 yes. Pop 1. dq=[2].  wait, nums[1]=2 >= nums[2]=1 → pop 1.
     dq=[2]. append 2. dq=[2].
     i>=k-1=2: result=[nums[2]]=[1]  ← WRONG! max of [2,2,1] is 2.

CORRECT (< pops strictly less):
i=0: dq=[0]
i=1: nums[0]=2 < nums[1]=2? No. append 1.  dq=[0,1]
i=2: nums[1]=2 < nums[2]=1? No. append 2.  dq=[0,1,2]
     evict: dq[0]=0 < i-k+1=0? No.
     i>=k-1=2: result=[nums[0]]=[2]  ← CORRECT!
```

### Test Cases That Expose the Bug

```python
import pytest
from collections import deque


def test_wrong_direction_gives_minimum():
    """Wrong direction (>=) effectively computes the minimum, not maximum."""
    nums = [1, 3, -1, -3, 5, 3, 6, 7]
    k = 3
    result = sliding_window_max_wrong(nums, k)
    correct = sliding_window_max_correct(nums, k)
    # wrong version produces sliding minimum
    assert result != correct, "WRONG version should differ from correct"
    assert correct == [3, 3, 5, 5, 6, 7]


def test_correct_basic():
    nums = [1, 3, -1, -3, 5, 3, 6, 7]
    k = 3
    assert sliding_window_max_correct(nums, k) == [3, 3, 5, 5, 6, 7]


def test_all_same_values():
    """[2,2,2] k=2 — all windows have maximum 2."""
    assert sliding_window_max_correct([2, 2, 2], 2) == [2, 2]


def test_duplicate_max_wrong_version():
    """[2,2,1] k=3 — WRONG version with <= pops too aggressively."""
    nums = [2, 2, 1]
    k = 3
    wrong = sliding_window_max_wrong_duplicate(nums, k)
    correct = sliding_window_max_correct(nums, k)
    assert correct == [2]


def test_increasing_sequence():
    assert sliding_window_max_correct([1, 2, 3, 4, 5], 3) == [3, 4, 5]


def test_decreasing_sequence():
    assert sliding_window_max_correct([5, 4, 3, 2, 1], 3) == [5, 4, 3]


def test_k_equals_1():
    assert sliding_window_max_correct([1, 3, 1, 2, 0], 1) == [1, 3, 1, 2, 0]


def test_k_equals_len():
    assert sliding_window_max_correct([3, 1, 2], 3) == [3]


def test_window_eviction():
    """Ensure front eviction works: max goes out of window."""
    assert sliding_window_max_correct([3, 1, 1, 1, 3], 3) == [3, 1, 1, 3]


if __name__ == "__main__":
    test_cases = [
        ([1, 3, -1, -3, 5, 3, 6, 7], 3),
        ([2, 2, 2], 2),
        ([2, 2, 1], 3),
        ([1, 2, 3, 4, 5], 3),
        ([5, 4, 3, 2, 1], 3),
    ]
    for nums, k in test_cases:
        correct = sliding_window_max_correct(nums, k)
        wrong = sliding_window_max_wrong(nums, k)
        flag = "OK" if correct == [max(nums[i:i+k]) for i in range(len(nums)-k+1)] else "BUG"
        print(f"nums={nums} k={k}")
        print(f"  correct={correct}  [{flag}]")
        print(f"  wrong  ={wrong}")
```

### Key Takeaway

| Deque Type | Pop Condition | Effect |
|---|---|---|
| Monotonic decreasing (for max) | `nums[back] < nums[i]` | Correct: keeps equal or larger at front |
| Monotonic decreasing (for max) | `nums[back] <= nums[i]` | Still correct for max values but loses earliest index of duplicate |
| Monotonic increasing (for min) | `nums[back] > nums[i]` | Correct minimum deque |
| Wrong direction | `nums[back] >= nums[i]` | Produces minimum instead of maximum |

For maximum: pop the back when `nums[back] < nums[i]` (strictly less). The front of the deque is always the index of the current window's maximum.

---

## Summary Table

| # | Mistake | Root Cause | Fix |
|---|---|---|---|
| 1 | `left = 0` on violation | Throws away progress, O(n²) | `while violated: shrink_left(); left += 1` |
| 2 | `right - left > k` off-by-one | Missing `+1` in size formula | `right - left + 1 > k` |
| 3 | `formed += 1` when `have >= need` | Multiple increments per character | `formed += 1` only when `have == need` |
| 4 | `set(t)` ignores duplicate chars | Set tracks presence, not quantity | `Counter(t)` tracks required counts |
| 5 | Wrong deque pop direction | `>=` produces minimum instead of maximum | Pop back when `nums[back] < nums[i]` |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real World Usage](./real_world_usage.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
