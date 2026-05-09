<a id="top"></a>
# Binary Search — The Art of Intelligent Guessing

> Binary Search is not just searching.
>
> It is intelligent elimination.
>
> Instead of checking everything,
> we cut the problem into half every time.

Binary Search is one of the most powerful optimization techniques.

If linear search is walking step-by-step,
binary search is teleporting halfway.

## 📖 Table of Contents

1. [Real Life Story — Guess the Number Game](#1-real-life-story)
2. [Core Idea — Divide the Search Space](#2-core-idea)
3. [Visual Understanding](#3-visual-understanding)
4. [Why It Is So Fast](#4-why-it-is-so-fast)
5. [Binary Search Implementation](#5-binary-search-implementation)
6. [Common Mistakes](#6-common-mistakes)
7. [Binary Search Variations](#7-binary-search-variations)
8. [Binary Search on Answer (Very Important)](#8-binary-search-on-answer)
9. [When Can We Use Binary Search?](#9-when-can-we-use-binary-search)
10. [Real-World Uses](#10-real-world-uses)
11. [Binary Search vs Linear Search](#11-binary-search-vs-linear-search)
12. [Advanced Insight — Why Boundaries Matter](#12-advanced-insight)
13. [Mental Model to Remember](#13-mental-model)
14. [Final Understanding](#14-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
core binary search mechanics · O(log n) · monotonic property · boundary conditions

**Should Learn** — Important for real projects, comes up regularly:
first/last occurrence · search on answer pattern · search in rotated array

**Good to Know** — Useful in specific situations, not always tested:
search in infinite array · search in 2D matrix

**Reference** — Know it exists, look up syntax when needed:
ternary search · fractional binary search · binary lifting

<a id="1-real-life-story"></a>
# 1. Real Life Story — Guess the Number Game

Imagine I tell you:

"I'm thinking of a number between 1 and 100."

You guess randomly:

1?  
2?  
3?  
4?  

You might take 100 tries.

But what if you think smart?

Guess 50.

If I say:
Too high → search between 1 and 49.
Too low → search between 51 and 100.

Each time,
you eliminate half.

That is binary search.

## Visual: The Hot/Cold Game in Action

You are playing a number guessing game with a friend.

"I'm thinking of a number between 1 and 1000. Guess it."

**Bad strategy (Linear Search):** "Is it 1? Is it 2? Is it 3?..."
Worst case: 1000 guesses.

**Good strategy (Binary Search):** "Is it 500?"
Friend: "Cold! Too high."
"Is it 250?"
Friend: "Warmer! Too low."
"Is it 375?"
...

Every guess cuts the remaining options in half. You'll find the answer in at most 10 guesses.

```
1000 numbers → guess 500 → 500 remaining
500  numbers → guess 250 → 250 remaining
250  numbers → guess 125 → 125 remaining
...
2    numbers → guess 1   → 1 remaining
1    number  → found!
```

That is binary search. Every step, half the possibilities are eliminated.

> [↑ Back to Top](#top)

<a id="2-core-idea"></a>
# 2. Core Idea — Divide the Search Space

Binary search works when:

Data is sorted OR  
We can decide which half to eliminate.

Process:

1. Find middle
2. Compare with target
3. Eliminate half
4. Repeat

Time complexity:

O(log n)

Why?

Because size becomes:

n → n/2 → n/4 → n/8 → …

Logarithmic growth.

**Common mistake — unsorted input:** Binary search on unsorted data produces silently wrong answers with no error. Always confirm ordering before applying it. If the array is unsorted, sort first (`O(n log n)`) or use a different algorithm entirely.

📝 **Practice:** [Q1 · classic-binary-search](./practice.md#q1--classic-binary-search--exact-match) · [Q2 · recursive](./practice.md#q2--binary-search--recursive) · [Q3 · search-insert-position](./practice.md#q3--search-insert-position)

> [↑ Back to Top](#top)

<a id="3-visual-understanding"></a>
# 3. Visual Understanding

Example:

```
[1, 3, 5, 7, 9, 11, 13]
```

Find 9.

left = 0  
right = 6  

mid = 3 → value = 7

7 < 9 → discard left half

Now:

left = 4  
right = 6  

mid = 5 → value = 11

11 > 9 → discard right half

Now:

left = 4  
right = 4  

Found 9.

We didn't scan entire array.

## Visual: Step-by-Step — Finding 37

**Array:** `[1, 5, 12, 18, 23, 37, 44, 57, 62, 89]`
**Target:** `37`

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

23 < 37 → target is in the RIGHT half → lo = mid+1 = 5

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

57 > 37 → target is in the LEFT half → hi = mid-1 = 6

Search space:
Before: [37, 44, 57, 62, 89]
                  ────────── eliminated
After:  [37, 44]
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
Number line showing shrinking search space:

Step 1:  [─────────────────────────────]  all 10 elements
Step 2:             [───────────────]     5 elements
Step 3:             [────]                2 elements
Step 4:             ●                    1 element (found)
```

> [↑ Back to Top](#top)

<a id="4-why-it-is-so-fast"></a>
# 4. Why It Is So Fast

Let n = 1,000,000.

Linear search:
Worst case → 1,000,000 comparisons.

Binary search:
log₂(1,000,000) ≈ 20 steps.

Huge difference.

## Visual: O(log n) — The Math That Will Blow Your Mind

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
Step 4:   62,500,000
Step 5:   31,250,000
Step 6:   15,625,000
Step 7:    7,812,500
Step 8:    3,906,250
Step 9:    1,953,125
Step 10:     976,562
Step 11:     488,281
Step 12:     244,140
Step 13:     122,070
Step 14:      61,035
Step 15:      30,517
Step 16:      15,258
Step 17:       7,629
Step 18:       3,814
Step 19:       1,907
Step 20:         953
Step 21:         476
Step 22:         238
Step 23:         119
Step 24:          59
Step 25:          29
Step 26:          14
Step 27:           7
Step 28:           3
Step 29:           1
Step 30:       FOUND

1,000,000,000 elements. At most 30 comparisons.
```

Linear search on a billion items? Up to 1,000,000,000 comparisons.
Binary search? 30.

That's the power of logarithmic time.

> [↑ Back to Top](#top)

<a id="5-binary-search-implementation"></a>
# 5. Binary Search Implementation

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

Important:
Loop condition must be correct.

## Visual: The Three Templates — Which One to Use?

Binary search comes in three flavors. The difference is subtle but critical.

### Template 1: Find Exact Match

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

### Template 2: Find Left Boundary (First True)

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

### Template 3: Find Right Boundary (Last True)

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

**Side-by-side comparison:**

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

**Common mistake — mid computation overflow:** Computing `mid = (left + right) // 2` overflows in C++/Java with large values. Use `mid = left + (right - left) // 2` instead. Python doesn't overflow, but writing it the safe way in interviews signals cross-language awareness — an important signal for senior roles.

**Common mistake — infinite loop with Template 3:** When `lo=4, hi=5`, floor division gives `mid=4`. If `arr[mid]` satisfies the condition and you set `lo = mid = 4`, lo never advances. Fix: use ceiling division `mid = (lo + hi + 1) // 2`.

📝 **Practice:** [Q9 · lo≤hi vs lo<hi](./practice.md#q9--off-by-one-lo--hi-vs-lo--hi) · [Q10 · mid+1 vs mid](./practice.md#q10--off-by-one-mid1-vs-mid-mid-1-vs-mid) · [Q11 · three-templates](./practice.md#q11--template-comparison--three-templates)

> [↑ Back to Top](#top)

<a id="6-common-mistakes"></a>
# 6. Common Mistakes

Binary search demands precision. These are the patterns that trip up even experienced engineers.

**Infinite loop from wrong loop condition:**

```python
# WRONG — left = mid never advances when left=0, right=1
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid          # BUG: stays 0 forever
        else:
            right = mid - 1

# CORRECT — left = mid + 1 guarantees progress
    elif nums[mid] < target:
        left = mid + 1
```

Test case that exposes the bug: `nums = [1, 3]`, searching for `3` hangs forever with the wrong version.

**Wrong boundary update:**

Use `left = mid + 1` and `right = mid - 1` for standard exact-match search.
Use `right = mid` (not `mid - 1`) only when preserving mid as a candidate answer (first occurrence patterns).

**Returning the wrong pointer after the loop:**

When `while left <= right` exits, `left > right` and `left` is one past the last searched position. Returning `mid` from the last iteration is especially dangerous — mid is stale and may be nowhere near the answer.

```python
# WRONG — mid is stale after the loop exits
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

**Forgetting to check whether the target exists after bisect:**

`bisect_left` returns an insertion point. If target is not present, that position holds a different (larger) value. Always check: `if pos < len(nums) and nums[pos] == target`.

Summary of conditions that must hold:

- Infinite loop (wrong boundary update)
- Using `while left < right` incorrectly
- Not handling duplicates properly
- Integer overflow in some languages
- Forgetting sorted requirement

> [↑ Back to Top](#top)

<a id="7-binary-search-variations"></a>
# 7. Binary Search Variations

Binary search is not just exact match.

It has many forms.

## Lower Bound

Find first element ≥ target.

Used in:

- Insert position
- Range problems

## Upper Bound

Find first element > target.

Important in duplicates.

## First Occurrence / Last Occurrence

Modify condition to continue searching even after match.

Used when duplicates exist.

**Common mistake — wrong condition for first vs last occurrence:** Using a standard exact-match template stops at any occurrence, not the first or last. For first occurrence, when `arr[mid] == target` set `result = mid` and continue searching left (`right = mid - 1`). For last occurrence, set `result = mid` and continue searching right (`left = mid + 1`).

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

## Python's bisect Module

Python has a built-in module for sorted arrays.

**Array:** `[1, 2, 2, 2, 3]`, searching for `2`

```
Index:  0  1  2  3  4
Array: [1, 2, 2, 2, 3]
              ↑↑↑
         three 2s here
```

**`bisect_left(arr, 2)`:** Where would 2 be inserted to stay sorted, from the LEFT side?

```
[1, 2, 2, 2, 3]
    ↑
    index 1 ← insert here, before the existing 2s

bisect_left returns 1
```

**`bisect_right(arr, 2)`:** Where would 2 be inserted to stay sorted, from the RIGHT side?

```
[1, 2, 2, 2, 3]
                ↑
             index 4 ← insert here, after the existing 2s

bisect_right returns 4
```

```
Visual comparison:

[1, 2, 2, 2, 3]
    ↑           ↑
bisect_left=1   bisect_right=4

The 2s occupy indices 1, 2, 3.
Left boundary: bisect_left → 1
Right boundary (exclusive): bisect_right → 4

Count of 2s = bisect_right - bisect_left = 4 - 1 = 3
```

**Common mistake — bisect_left vs bisect_right direction:** The count formula is `bisect_right - bisect_left`, not the reverse. `bisect_left` gives the index of the first element `>= target`. `bisect_right` gives the index of the first element `> target` (one past the last occurrence). Subtracting them in the wrong order gives a negative count.

```python
import bisect

nums = [1, 2, 2, 2, 3]
target = 2

right_boundary = bisect.bisect_right(nums, target)   # 4
left_boundary  = bisect.bisect_left(nums, target)    # 1
count = right_boundary - left_boundary               # 3 — correct
```

📝 **Practice:** [Q6 · first-occurrence](./practice.md#q6--first-occurrence-of-target) · [Q7 · last-occurrence](./practice.md#q7--last-occurrence-of-target) · [Q4 · bisect-left-right](./practice.md#q4--bisect_left-vs-bisect_right) · [Q5 · count-with-bisect](./practice.md#q5--count-occurrences-with-bisect)

> [↑ Back to Top](#top)

<a id="8-binary-search-on-answer"></a>
# 8. Binary Search on Answer (Very Important)

Sometimes array is not directly searchable.

But answer lies in a range.

Example:

Find minimum speed to complete work in time.

Speed range:
1 to max_possible.

Instead of checking every speed:

Binary search on speed.

If speed works:
Try smaller.
If not:
Try larger.

Binary search can search over solution space.

This is advanced pattern.

## Visual: The Koko Eating Bananas Problem

**Story:** Koko has `n` piles of bananas. She has `h` hours before the guard returns. She can eat at speed `k` bananas per hour. What's the minimum speed `k` that lets her finish all piles in time?

**Input:** piles = `[3, 6, 7, 11]`, h = `8`

**Key insight:** This is a monotonic function.

```
If speed k=5 works (she finishes in 8 hours),
then speed k=6 also works (she finishes faster).

"If S works, S+1 works too."
That's monotonic. That means binary search applies.
```

Visualize the answer space as a number line:

```
Speed:     1    2    3    4    5    6    7    8    ...    11
           │    │    │    │    │    │    │    │           │
Too slow?  ✗    ✗    ✗    ✗    ✓    ✓    ✓    ✓    ...   ✓
                              ↑
                         First speed that works = answer
```

The transition from ✗ to ✓ happens at exactly one point. Binary search finds that transition.

```
lo = 1          (minimum possible speed)
hi = max(piles) (no need to eat faster than the biggest pile)
```

**Walking through it:**

```
piles = [3, 6, 7, 11], h = 8

lo=1, hi=11, mid=6
  Can Koko eat all piles at speed 6?
  pile 3:  ceil(3/6)=1 hour
  pile 6:  ceil(6/6)=1 hour
  pile 7:  ceil(7/6)=2 hours
  pile 11: ceil(11/6)=2 hours
  Total: 1+1+2+2 = 6 hours ≤ 8 → YES, speed 6 works
  But maybe we can go slower. Try lower: hi = mid = 6

lo=1, hi=6, mid=3
  Can Koko eat at speed 3?
  pile 3:  ceil(3/3)=1
  pile 6:  ceil(6/3)=2
  pile 7:  ceil(7/3)=3
  pile 11: ceil(11/3)=4
  Total: 1+2+3+4 = 10 hours > 8 → NO, too slow
  Must go faster: lo = mid+1 = 4

lo=4, hi=6, mid=5
  Can Koko eat at speed 5?
  pile 3:  ceil(3/5)=1
  pile 6:  ceil(6/5)=2
  pile 7:  ceil(7/5)=2
  pile 11: ceil(11/5)=3
  Total: 1+2+2+3 = 8 ≤ 8 → YES, speed 5 works
  Try lower: hi = mid = 5

lo=4, hi=5, mid=4
  Can Koko eat at speed 4?
  Total: 1+2+2+3 = 8 ≤ 8 → YES, speed 4 works
  Try lower: hi = mid = 4

lo=4, hi=4 → lo == hi → STOP

Answer: 4
```

**The template for "search on answer" problems:**

```
Step 1: Identify the search space (minimum and maximum possible answer).
Step 2: Write a "feasibility check" function: can_do(answer) → bool.
Step 3: Verify monotonicity: if can_do(x) then can_do(x+1).
Step 4: Binary search for the transition point.
```

**Common mistake — violating the monotonicity assumption:** "Binary search on the answer" works only when the validation function is monotonic: all values below the answer are invalid and all values at/above it are valid (or vice versa). If `can_do(days=5)` is True but `can_do(days=6)` is False and `can_do(days=7)` is True, binary search will converge on the wrong boundary. Always verify: "Is it true that if X works, X+1 also works?" before applying this pattern.

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

📝 **Practice:** [Q17 · koko-bananas](./practice.md#q17--koko-eating-bananas) · [Q18 · ship-packages](./practice.md#q18--capacity-to-ship-packages) · [Q19 · minimize-max](./practice.md#q19--minimize-maximum-split-array-largest-sum) · [Q20 · maximize-min](./practice.md#q20--maximize-minimum-allocate-minimum-pages) · [Q23 · first-bad-version](./practice.md#q23--find-bad-version-first-true-in-answer-space)

📝 **Practice:** [Q17 · binary-search-on-answer](../dsa_practice_questions_100.md#q17--thinking--binary-search-on-answer)

> [↑ Back to Top](#top)

<a id="9-when-can-we-use-binary-search"></a>
# 9. When Can We Use Binary Search?

Binary search works when:

- Data is sorted
OR
- There is monotonic behavior

Monotonic means:

If condition true at some point,
it remains true afterward.

Example:

Speed too slow → fail  
Speed fast enough → pass  
Faster speed → still pass

This is monotonic property.

Binary search thrives on monotonicity.

📝 **Practice:** [Q12 · rotated-array](./practice.md#q12--search-in-rotated-sorted-array) · [Q13 · min-rotated](./practice.md#q13--find-minimum-in-rotated-sorted-array) · [Q14 · peak-element](./practice.md#q14--find-peak-element)

> [↑ Back to Top](#top)

<a id="10-real-world-uses"></a>
# 10. Real-World Uses

- Searching in database indexes
- Library catalog systems
- Auto-complete suggestions
- Finding root of equation
- Memory allocation
- Competitive programming optimization

Binary search is widely used.

> [↑ Back to Top](#top)

<a id="11-binary-search-vs-linear-search"></a>
# 11. Binary Search vs Linear Search

| Feature | Linear | Binary |
|----------|--------|--------|
| Sorted Required | No | Yes |
| Time | O(n) | O(log n) |
| Implementation | Simple | Careful |
| Use case | Small data | Large sorted data |

> [↑ Back to Top](#top)

<a id="12-advanced-insight"></a>
# 12. Advanced Insight — Why Boundaries Matter

If you update incorrectly:

```
left = mid
```

Instead of:

```
left = mid + 1
```

You may cause infinite loop.

Binary search must reduce search space every iteration.

That's mandatory.

**Common mistake — using left = mid instead of left = mid + 1:** When `left=0, right=1`, `mid=0`. If the target is greater and you set `left = mid = 0`, no progress is made. The search space never shrinks. Always use `left = mid + 1` to guarantee the search space reduces by at least one element per iteration.

## Pre-Submission Checklist

Before submitting any binary search solution, answer these 6 questions:

- [ ] **1. Is the search space sorted (or monotonic)?**
  Binary search on unsorted data gives silent wrong answers. Confirm ordering before applying it.

- [ ] **2. Is mid computed safely?**
  Use `mid = left + (right - left) // 2`. Safe in all languages, not just Python.

- [ ] **3. Which loop condition — `left <= right` or `left < right`?**
  Use `left <= right` for exact-match search. Use `left < right` for boundary-finding patterns where you preserve mid as a candidate.

- [ ] **4. Are boundary updates `mid+1`/`mid-1` or `mid`?**
  In exact-match search, always `left = mid + 1` and `right = mid - 1`.
  In first/last occurrence, one boundary stays at `mid` (to preserve the candidate).

- [ ] **5. What is returned after the loop?**
  `left`, `right`, and `mid` have different meanings post-loop. State which you return and why. Check the value at `left` before returning it as "found."

- [ ] **6. Is `bisect_left` or `bisect_right` the right tool?**
  `bisect_left` gives the index of the first element `>= target`.
  `bisect_right` gives the index of the first element `> target` (one past the last occurrence).
  The count of a target is always `bisect_right - bisect_left`.

📝 **Practice:** [Q25 · bug-hunt](./practice.md#q25--off-by-one-bug-hunt) · [Q15 · integer-sqrt](./practice.md#q15--square-root-via-binary-search-integer) · [Q16 · float-sqrt](./practice.md#q16--square-root-via-binary-search-float)

> [↑ Back to Top](#top)

<a id="13-mental-model"></a>
# 13. Mental Model to Remember

Imagine cutting a cake into halves every time.

Each cut reduces problem dramatically.

Binary search is repeated halving.

If you cannot discard half confidently,
binary search cannot be applied.

> Binary search works whenever you can look at the middle of a sorted space and say
> "the answer is definitely not in this half." Each step, you eliminate half the possibilities.
> 1 billion elements. 30 steps. That's the magic of O(log n).

> [↑ Back to Top](#top)

<a id="14-final-understanding"></a>
# 14. Final Understanding

Binary Search is:

- Fast
- Elegant
- Precise
- Logarithmic
- Based on elimination
- Requires sorted/monotonic property

It is one of the most powerful optimization tools.

If you master binary search,
you unlock many hard interview problems.

📝 **Practice:** [Q16 · binary-search-conditions](../dsa_practice_questions_100.md#q16--normal--binary-search-conditions) · [Q94 · debug-binary-search](../dsa_practice_questions_100.md#q94--debug--debug-binary-search)

> [↑ Back to Top](#top)

**[🏠 Back to README](../README.md)**

**Prev:** [← Sliding Window — Interview Q&A](../12_sliding_window/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
