<a id="top"></a>
# 📘 13 – Binary Search in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. The Guessing Game](#1-guessing-game)
  - [Visual: The Hot/Cold Game](#visual-hot-cold)
- [2. Core Idea and Why O(log n)](#2-core-idea)
  - [Visual: Finding 37 Step-by-Step](#visual-finding-37)
  - [Visual: O(log n) — The Math](#visual-log-n)
- [3. The Three Templates](#3-three-templates)
  - [Template 1: Exact Match](#template-1)
  - [Template 2: Left Boundary (First True)](#template-2)
  - [Template 3: Right Boundary (Last True)](#template-3)
  - [Side-by-Side Comparison](#templates-comparison)
- [4. Common Mistakes and Boundaries](#4-common-mistakes)
  - [Pre-Submission Checklist](#pre-submission-checklist)
- [5. Binary Search Variations](#5-variations)
  - [Lower Bound and Upper Bound](#lower-upper-bound)
  - [First and Last Occurrence](#first-last-occurrence)
  - [Python's bisect Module](#bisect-module)
- [6. Binary Search on Answer](#6-search-on-answer)
  - [Visual: Koko Eating Bananas](#visual-koko)
  - [Visual: Decision Tree](#visual-decision-tree)
- [7. When Binary Search Applies](#7-when-applies)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
core binary search mechanics · O(log n) · monotonic property · boundary conditions

**Should Learn** — Important for real projects, comes up regularly:
first/last occurrence · search on answer pattern · search in rotated array

**Good to Know** — Useful in specific situations, not always tested:
search in infinite array · search in 2D matrix

**Reference** — Know it exists, look up syntax when needed:
ternary search · fractional binary search · binary lifting

Iris is a detective. She has a list of 1000 suspects, sorted by height. A witness says: "The culprit is about 175cm tall." Iris does not interview all 1000 people — she opens the list to the middle (suspect 500), checks their height. Too tall? She throws away the top half. Too short? She throws away the bottom half. Each step, she halves the suspects. In 10 steps, she finds her person among 1000. In 20 steps, among a million. That is **binary search** — the art of intelligent elimination.

<a id="1-guessing-game"></a>
# 1. The Guessing Game

Iris plays the classic number game with her partner: "I'm thinking of a number between 1 and 1000. Guess it."

**Bad strategy (Linear Search):** "Is it 1? Is it 2? Is it 3?..." Worst case: 1000 guesses.

**Good strategy (Binary Search):** "Is it 500?" Partner: "Too high." "Is it 250?" Partner: "Too low." "Is it 375?" ...

Every guess cuts the remaining options in half. She finds the answer in at most 10 guesses.

```
1000 numbers → guess 500 → 500 remaining
500  numbers → guess 250 → 250 remaining
250  numbers → guess 125 → 125 remaining
...
2    numbers → guess 1   → 1 remaining
1    number  → found!
```

<a id="visual-hot-cold"></a>
## Visual: The Hot/Cold Game

```
Iris is playing "Hot/Cold":

"Is it 500?" → "Cold! Too high."
"Is it 250?" → "Warmer! Too low."
"Is it 375?" → "Hot! A bit high."
"Is it 312?" → "Very hot! A bit low."
"Is it 343?" → "BURNING! You're there!"

Each time:
  sum/2 → cut problem in half
  "too high" → discard upper half
  "too low"  → discard lower half

10 questions, 1000 possibilities. That's binary search.
```

> [↑ Back to Top](#top)

<a id="2-core-idea"></a>
# 2. Core Idea and Why O(log n)

Iris formalizes her technique. Binary search works when data is sorted OR when she can decide which half to eliminate. The process: find middle, compare with target, eliminate half, repeat.

Binary search works when:
- Data is sorted, OR
- There is a monotonic property (condition flips from False to True at one point)

Process:
1. Find middle
2. Compare with target
3. Eliminate half
4. Repeat

Time: O(log n) — because size becomes n → n/2 → n/4 → n/8 → ... → 1. That takes log₂(n) steps.

**Common mistake — unsorted input:** Binary search on unsorted data produces silently wrong answers with no error. Always confirm ordering before applying it.

<a id="visual-finding-37"></a>
## Visual: Finding 37 Step-by-Step

**Array:** `[1, 5, 12, 18, 23, 37, 44, 57, 62, 89]`. **Target:** `37`

```
Indices:   0   1   2   3   4   5   6   7   8   9
Array:    [1,  5, 12, 18, 23, 37, 44, 57, 62, 89]

lo=0, hi=9
```

**Iteration 1:**

```
lo=0, hi=9, mid = (0+9)//2 = 4

         lo              hi
          ↓               ↓
[1,  5, 12, 18, 23, 37, 44, 57, 62, 89]
                 ↑
               mid=4, value=23

23 < 37 → target in RIGHT half → lo = mid+1 = 5

Search space:
Before: [1, 5, 12, 18, 23, 37, 44, 57, 62, 89]
         ────────────────  eliminated
After:                   [37, 44, 57, 62, 89]
```

**Iteration 2:**

```
lo=5, hi=9, mid = (5+9)//2 = 7

                     lo              hi
                      ↓               ↓
[1,  5, 12, 18, 23, 37, 44, 57, 62, 89]
                             ↑
                           mid=7, value=57

57 > 37 → target in LEFT half → hi = mid-1 = 6

Search space: [37, 44]
```

**Iteration 3:**

```
lo=5, hi=6, mid = (5+6)//2 = 5

                     lo  hi
                      ↓   ↓
[1,  5, 12, 18, 23, 37, 44, 57, 62, 89]
                     ↑
                   mid=5, value=37

37 == 37 → FOUND! Return index 5.
```

```
Shrinking search space:

Step 1:  [─────────────────────────────]  all 10 elements
Step 2:             [───────────────]     5 elements
Step 3:             [────]                2 elements
Step 4:             ●                    1 element (found)
```

<a id="visual-log-n"></a>
## Visual: O(log n) — The Math

How many times can you cut a number in half before reaching 1?

```
n  → n/2  → n/4  → n/8  → ... → 1
That takes log₂(n) steps.
```

**Concrete example:**

```
n = 1,000,000,000 (one billion)

Step 1:  500,000,000
Step 2:  250,000,000
Step 3:  125,000,000
...
Step 10:     976,562
...
Step 20:         953
...
Step 30:           1 → FOUND

1,000,000,000 elements. At most 30 comparisons.
```

Linear search on a billion items? Up to 1,000,000,000 comparisons.
Binary search? 30. That is the power of logarithmic time.

> 📝 **Practice:** [Q1 · classic-binary-search](./practice.md#q1--classic-binary-search--exact-match) · [Q2 · recursive](./practice.md#q2--binary-search--recursive) · [Q3 · search-insert-position](./practice.md#q3--search-insert-position)

> [↑ Back to Top](#top)

<a id="3-three-templates"></a>
# 3. The Three Templates

Iris discovers that binary search comes in three flavors. The difference is subtle but critical — using the wrong template causes infinite loops or missed answers.

Classic iterative version:

```python
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
```

<a id="template-1"></a>
## Template 1: Exact Match

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1

    while lo <= hi:           # note: lo <= hi
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid        # found!
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1                 # not found
```

```
When to use: You need to find an exact value.
Loop exits when: lo > hi (crossed, not found) or when arr[mid]==target.
```

<a id="template-2"></a>
## Template 2: Left Boundary (First True)

```python
def find_left(arr, target):
    lo, hi = 0, len(arr)      # hi = len(arr), not len-1

    while lo < hi:            # note: lo < hi (strict)
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid          # hi = mid, not mid-1

    return lo                 # lo == hi, this is the answer
```

```
When to use: Find the first position where a condition becomes True.
Example: "Find the leftmost index where arr[i] >= target"
Loop exits when lo == hi. That position is the answer.
```

<a id="template-3"></a>
## Template 3: Right Boundary (Last True)

```python
def find_right(arr, target):
    lo, hi = 0, len(arr) - 1

    while lo < hi:
        mid = (lo + hi + 1) // 2   # ceiling division to avoid infinite loop
        if arr[mid] <= target:
            lo = mid               # lo = mid
        else:
            hi = mid - 1

    return lo
```

```
When to use: Find the last position where a condition is True.
Note the +1 in mid calculation — prevents infinite loop when lo+1==hi.
```

<a id="templates-comparison"></a>
## Side-by-Side Comparison

```
Template 1          Template 2          Template 3
─────────────────   ─────────────────   ─────────────────
lo <= hi            lo < hi             lo < hi
mid = (lo+hi)//2    mid = (lo+hi)//2    mid = (lo+hi+1)//2
return mid          hi = mid            lo = mid
hi = mid-1          lo = mid+1          hi = mid-1
                    return lo           return lo
─────────────────   ─────────────────   ─────────────────
"exact match"       "first true"        "last true"
                    "left boundary"     "right boundary"
```

**Common mistake — mid computation overflow:** Use `mid = left + (right - left) // 2` instead of `(left + right) // 2`. Python doesn't overflow, but this signals cross-language awareness in interviews.

**Common mistake — infinite loop with Template 3:** When `lo=4, hi=5`, floor division gives `mid=4`. If `arr[mid]` satisfies and you set `lo = mid = 4`, lo never advances. Fix: use ceiling division `mid = (lo + hi + 1) // 2`.

> 📝 **Practice:** [Q9 · lo≤hi vs lo<hi](./practice.md#q9--off-by-one-lo--hi-vs-lo--hi) · [Q10 · mid+1 vs mid](./practice.md#q10--off-by-one-mid1-vs-mid-mid-1-vs-mid) · [Q11 · three-templates](./practice.md#q11--template-comparison--three-templates)

> [↑ Back to Top](#top)

<a id="4-common-mistakes"></a>
# 4. Common Mistakes and Boundaries

Iris learns that binary search demands precision. Even experienced engineers write bugs — Jon Bentley famously noted that fewer than 10% of professional programmers implement it correctly on the first try.

**Infinite loop from wrong boundary update:**

```python
# WRONG — left = mid never advances when left=0, right=1
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] < target:
            left = mid          # BUG: stays 0 forever
        else:
            right = mid - 1

# CORRECT — left = mid + 1 guarantees progress
        if nums[mid] < target:
            left = mid + 1
```

Test case that exposes the bug: `nums = [1, 3]`, searching for `3` hangs forever.

**Wrong boundary update:**

Use `left = mid + 1` and `right = mid - 1` for standard exact-match search. Use `right = mid` (not `mid - 1`) only when preserving mid as a candidate answer (first occurrence patterns).

**Returning the wrong pointer after the loop:**

When `while left <= right` exits, `left > right`. Returning `mid` from the last iteration is dangerous — mid is stale.

```python
# WRONG — mid is stale after loop exits
def first_occurrence(nums, target):
    ...
    return mid   # BUG

# CORRECT — track result explicitly
def first_occurrence(nums, target):
    left, right = 0, len(nums) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            result = mid
            right = mid - 1
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result
```

**Forgetting to check whether target exists after bisect:**

`bisect_left` returns an insertion point. If target is absent, that position holds a different value. Always check: `if pos < len(nums) and nums[pos] == target`.

**Common mistake — using left = mid instead of left = mid + 1:** When `left=0, right=1`, `mid=0`. Setting `left = mid = 0` makes no progress. The search space never shrinks. Always use `left = mid + 1` to guarantee reduction.

<a id="pre-submission-checklist"></a>
## Pre-Submission Checklist

Before submitting any binary search solution:

- [ ] **1. Is the search space sorted (or monotonic)?**
- [ ] **2. Is mid computed safely?** Use `mid = left + (right - left) // 2`
- [ ] **3. Which loop condition?** `left <= right` for exact-match. `left < right` for boundary-finding.
- [ ] **4. Are boundary updates correct?** `mid+1`/`mid-1` for exact-match. One boundary stays at `mid` for first/last occurrence.
- [ ] **5. What is returned after the loop?** Check the value at `left` before returning as "found."
- [ ] **6. bisect_left or bisect_right?** Left = first `>=`. Right = first `>`. Count = `right - left`.

> 📝 **Practice:** [Q25 · bug-hunt](./practice.md#q25--off-by-one-bug-hunt) · [Q15 · integer-sqrt](./practice.md#q15--square-root-via-binary-search-integer) · [Q16 · float-sqrt](./practice.md#q16--square-root-via-binary-search-float)

> [↑ Back to Top](#top)

<a id="5-variations"></a>
# 5. Binary Search Variations

Iris discovers that binary search is rarely asked as a simple "find this value." Real interview problems use variations — lower bound, upper bound, first/last occurrence. These are the bread and butter of binary search interviews.

<a id="lower-upper-bound"></a>
## Lower Bound and Upper Bound

**Lower Bound:** First element >= target. Used for insertion point and range problems.
**Upper Bound:** First element > target. Important with duplicates.

<a id="first-last-occurrence"></a>
## First and Last Occurrence

Modify the condition to continue searching even after a match.

**Common mistake — wrong condition:** Standard exact-match stops at ANY occurrence. For first occurrence, when `arr[mid] == target`, record and search LEFT. For last occurrence, record and search RIGHT.

```python
def first_occurrence(nums, target):
    left, right = 0, len(nums) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            result = mid        # Record and continue searching LEFT
            right = mid - 1
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result

def last_occurrence(nums, target):
    left, right = 0, len(nums) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            result = mid        # Record and continue searching RIGHT
            left = mid + 1
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result
```

<a id="bisect-module"></a>
## Python's bisect Module

**Array:** `[1, 2, 2, 2, 3]`, searching for `2`

```
Index:  0  1  2  3  4
Array: [1, 2, 2, 2, 3]
              ↑↑↑
         three 2s here
```

**`bisect_left(arr, 2)` = 1:** Insert position from the LEFT (before existing 2s)
**`bisect_right(arr, 2)` = 4:** Insert position from the RIGHT (after existing 2s)

```
Visual comparison:

[1, 2, 2, 2, 3]
    ↑           ↑
bisect_left=1   bisect_right=4

Count of 2s = bisect_right - bisect_left = 4 - 1 = 3
```

**Common mistake — bisect direction:** `bisect_left` gives index of first `>= target`. `bisect_right` gives index of first `> target`. Count = `right - left`, not the reverse.

```python
import bisect

nums = [1, 2, 2, 2, 3]
target = 2

left_boundary = bisect.bisect_left(nums, target)    # 1
right_boundary = bisect.bisect_right(nums, target)  # 4
count = right_boundary - left_boundary              # 3
```

> 📝 **Practice:** [Q6 · first-occurrence](./practice.md#q6--first-occurrence-of-target) · [Q7 · last-occurrence](./practice.md#q7--last-occurrence-of-target) · [Q4 · bisect-left-right](./practice.md#q4--bisect_left-vs-bisect_right) · [Q5 · count-with-bisect](./practice.md#q5--count-occurrences-with-bisect)

> [↑ Back to Top](#top)

<a id="6-search-on-answer"></a>
# 6. Binary Search on Answer

Iris faces her most advanced case: the "culprit" is not in a list — it is a VALUE she must find. She binary searches on the answer space itself. "What is the minimum speed that finishes the job?" The speed forms a monotonic range: all speeds below the answer are too slow, all speeds at/above it work.

**Key insight:** Binary search works on ANY monotonic function, not just sorted arrays.

The template:
```
Step 1: Identify the search space [lo, hi] for the answer
Step 2: Write a feasibility check: can_do(answer) → bool
Step 3: Verify monotonicity: if can_do(x) then can_do(x+1)
Step 4: Binary search for the transition point
```

<a id="visual-koko"></a>
## Visual: Koko Eating Bananas

**Story:** Koko has piles of bananas `[3, 6, 7, 11]` and `h=8` hours. Minimum speed `k`?

```
Speed:     1    2    3    4    5    6    7    8    ...    11
           │    │    │    │    │    │    │    │           │
Too slow?  ✗    ✗    ✗    ✓    ✓    ✓    ✓    ✓    ...   ✓
                         ↑
                    First speed that works = answer
```

```
lo=1, hi=11, mid=6
  Speed 6: ceil(3/6)+ceil(6/6)+ceil(7/6)+ceil(11/6) = 1+1+2+2 = 6 ≤ 8 → YES
  Try lower: hi = mid = 6

lo=1, hi=6, mid=3
  Speed 3: 1+2+3+4 = 10 > 8 → NO, too slow
  lo = mid+1 = 4

lo=4, hi=6, mid=5
  Speed 5: 1+2+2+3 = 8 ≤ 8 → YES
  hi = mid = 5

lo=4, hi=5, mid=4
  Speed 4: 1+2+2+3 = 8 ≤ 8 → YES
  hi = mid = 4

lo == hi == 4. Answer: speed 4.
```

**Common mistake — violating monotonicity:** "Search on answer" only works when the validation function is monotonic. If `can_do(5)=True` but `can_do(6)=False`, binary search converges on the wrong boundary. Always verify: "If X works, does X+1 also work?"

> 📝 **Practice:** [Q17 · koko-bananas](./practice.md#q17--koko-eating-bananas) · [Q18 · ship-packages](./practice.md#q18--capacity-to-ship-packages) · [Q19 · minimize-max](./practice.md#q19--minimize-maximum-split-array-largest-sum) · [Q20 · maximize-min](./practice.md#q20--maximize-minimum-allocate-minimum-pages) · [Q23 · first-bad-version](./practice.md#q23--find-bad-version-first-true-in-answer-space)

> 📝 **Practice:** [Q17 · binary-search-on-answer](../dsa_practice_questions_100.md#q17--thinking--binary-search-on-answer)

<a id="visual-decision-tree"></a>
## Visual: Decision Tree

```
Binary search problem? Ask yourself:

"Is the array sorted (or can I search on a monotonic answer space)?"
           │
           ├─ YES
           │     │
           │     ├─ "Find exact value"
           │     │       → Template 1 (lo <= hi)
           │     │
           │     ├─ "Find first position where condition is True"
           │     │       → Template 2 (lo < hi, hi=mid)
           │     │
           │     ├─ "Find last position where condition is True"
           │     │       → Template 3 (lo < hi, lo=mid, ceil mid)
           │     │
           │     └─ "Find minimum/maximum value that satisfies condition"
           │               → Search on answer, use feasibility check
           │
           └─ NO → Binary search won't work directly
```

> [↑ Back to Top](#top)

<a id="7-when-applies"></a>
# 7. When Binary Search Applies

Iris summarizes her detective rule: binary search works whenever she can look at the middle and confidently say "the answer is NOT in this half." If she cannot make that guarantee, binary search does not apply.

Binary search applies when:
- Data is sorted
- OR there is a **monotonic property** (condition flips from False to True at one point)

Monotonic means: if condition is true at point X, it remains true for all points > X. Examples:
- Speed too slow → fail. Speed fast enough → pass. Faster → still pass.
- Array too small → cannot fit. Large enough → can fit. Larger → still fits.

Binary search thrives on monotonicity.

> 📝 **Practice:** [Q12 · rotated-array](./practice.md#q12--search-in-rotated-sorted-array) · [Q13 · min-rotated](./practice.md#q13--find-minimum-in-rotated-sorted-array) · [Q14 · peak-element](./practice.md#q14--find-peak-element)

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

| Concept | Key Takeaway |
|---------|-------------|
| Binary search | Eliminate half the search space each step → O(log n) |
| Template 1 | `lo <= hi` — exact match, exits when crossed |
| Template 2 | `lo < hi`, `hi = mid` — find first True, converges |
| Template 3 | `lo < hi`, `lo = mid`, ceil mid — find last True |
| Variations | First/last occurrence, lower/upper bound, bisect |
| Search on answer | Binary search on value space, not array index |
| Monotonicity | The property that makes binary search applicable |

**Binary Search vs Linear Search:**

| Feature | Linear | Binary |
|----------|--------|--------|
| Sorted Required | No | Yes |
| Time | O(n) | O(log n) |
| Implementation | Simple | Careful |
| Use case | Small/unsorted | Large sorted data |

**Real-world uses:**
- Database indexes (B-tree lookups)
- Library catalog systems
- Auto-complete suggestions
- Finding roots of equations (bisection method)
- Memory allocation
- Git bisect (finding the commit that introduced a bug)

**Mental model:** Imagine cutting a cake in half every time. Each cut reduces the problem dramatically. If you cannot discard half confidently, binary search cannot be applied.

> Binary search works whenever you can look at the middle of a sorted space and say "the answer is definitely not in this half." Each step, you eliminate half the possibilities. 1 billion elements. 30 steps. That's the magic of O(log n).

> 📝 **Practice:** [Q16 · binary-search-conditions](../dsa_practice_questions_100.md#q16--normal--binary-search-conditions) · [Q94 · debug-binary-search](../dsa_practice_questions_100.md#q94--debug--debug-binary-search)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [12_sliding_window → theory.md](../12_sliding_window/theory.md) |
| ➡ Next Module | [14_trees → theory.md](../14_trees/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[12 Sliding Window →](../12_sliding_window/theory.md) · [14 Trees →](../14_trees/theory.md) · [06 Searching →](../06_searching/theory.md) · [16 Heaps →](../16_heaps/theory.md)

**Jump to specific topics in other files:**
- Binary search basics → [06_searching § Binary Search](../06_searching/theory.md#3-why-binary-search)
- Rotated array search → [06_searching § Rotated Array](../06_searching/theory.md#rotated-array)
- Bisect for sorted operations → [05_sorting § Timsort](../05_sorting/theory.md#11-timsort)
- Heap for priority-based search → [16_heaps § theory.md](../16_heaps/theory.md)

> [↑ Back to Top](#top)
