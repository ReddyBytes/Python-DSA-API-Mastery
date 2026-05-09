<a id="top"></a>
# 📘 Sliding Window — The Magic Moving Frame

> Imagine you are looking at the world through a small window.
> You can move the window.
> You can expand it.
> You can shrink it.
>
> But you never rebuild the entire world again.
>
> That is Sliding Window.

Sliding Window is not a data structure.
It is a way of thinking.

It transforms slow O(n²) substring and subarray problems
into fast O(n) solutions.

## 📖 Table of Contents

1. [Real Life Story — Watching Through a Window](#1-real-life-story)
2. [Chocolate Bar Story — Maximum Sweetness](#2-chocolate-bar-story)
3. [Core Idea of Sliding Window](#3-core-idea)
4. [Two Types of Sliding Window](#4-two-types)
5. [Fixed Window — Step by Step](#5-fixed-window-step-by-step)
6. [Variable Window — Growing and Shrinking](#6-variable-window)
7. [Why Sliding Window Is So Powerful](#7-why-powerful)
8. [Sliding Window in Strings](#8-sliding-window-in-strings)
9. [Common Sliding Window Problems](#9-common-problems)
10. [Sliding Window Maximum — Deque](#10-sliding-window-maximum)
11. [Sliding Window vs Two Pointers](#11-vs-two-pointers)
12. [Maintaining Window State](#12-maintaining-window-state)
13. [Real Life Applications](#13-real-life-applications)
14. [Mental Model to Remember](#14-mental-model)
15. [Final Understanding](#15-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
fixed-size window · variable-size window · window expansion and contraction

**Should Learn** — Important for real projects, comes up regularly:
state maintenance in window · longest substring without repeating chars · minimum window substring

**Good to Know** — Useful in specific situations, not always tested:
sliding window maximum (deque optimization) · window vs two pointers distinction

**Reference** — Know it exists, look up syntax when needed:
categorical sliding window · multi-pointer variants

<a id="1-real-life-story"></a>
# 1. Real Life Story — Watching Through a Window

Imagine you are inside a train.

You look outside through your window.

The window shows only part of the scenery.

As train moves:

- The window moves forward.
- Old scenery disappears.
- New scenery appears.

You don't restart looking from beginning.
You just slide forward.

That is sliding window.

You're looking through a telescope at a night sky full of stars in a line.
Your telescope shows exactly 3 stars at a time.

You want to find the brightest patch — the window of 3 stars with the most total light.

Brute force: Close your eyes. Open them at position 1 — count the brightness. Close. Open at position 2 — count again from scratch.

Every time you open, you count all 3 stars. Wasteful.

Sliding window: You're already looking at stars 1-2-3. To see stars 2-3-4, you don't re-measure stars 2 and 3. You just slide the telescope one step right. Remove star 1's brightness, add star 4's brightness.

One step. One addition. One subtraction. Instant.

```
Initial window:          [★ ★ ★] ○ ○ ○ ○ ○
Slide right:              ○ [★ ★ ★] ○ ○ ○ ○
Slide right:              ○  ○ [★ ★ ★] ○ ○ ○
                                      ↑
                         Always: remove left star, add right star
```

> [↑ Back to Top](#top)

<a id="2-chocolate-bar-story"></a>
# 2. Chocolate Bar Story — Maximum Sweetness

Imagine you have chocolates:

```
[2, 1, 5, 1, 3, 2]
```

You want to find:

Maximum sum of 3 consecutive chocolates.

Brute force way:

Check every group of 3.

That means:

(2,1,5)
(1,5,1)
(5,1,3)
(1,3,2)

This is O(nk).

But sliding window says:

Don't recompute from scratch.

Step 1:
Take first 3 → sum = 8

Step 2:
Remove 2
Add next element (1)

New sum = 8 - 2 + 1 = 7

You reuse previous work.

You slide forward.

That reduces complexity to O(n).

## Visual: Fixed Window Maximum Sum

**Problem:** Find the max sum of any 3 consecutive elements.
**Input:** `[2, 1, 5, 1, 3, 2]`, k = 3

**Brute force (O(n*k)):**

```
Window [2,1,5]   → sum = 8
Window [1,5,1]   → sum = 7
Window [5,1,3]   → sum = 9  ← max
Window [1,3,2]   → sum = 6

For each window, sum all k elements. Expensive if k is large.
```

**Sliding window (O(n)):**

```
Step 1: Build the first window.
  Sum the first k=3 elements: 2+1+5 = 8

  [ 2,  1,  5,  1,  3,  2 ]
    ├────────┤
    window = [2,1,5], sum = 8, max_sum = 8

Step 2: Slide right.
  - Remove the leftmost element (2)
  - Add the new rightmost element (1)
  - New sum = 8 - 2 + 1 = 7

  [ 2,  1,  5,  1,  3,  2 ]
         ├────────┤
         window = [1,5,1], sum = 7, max_sum = 8

Step 3: Slide right.
  - Remove 1, add 3
  - New sum = 7 - 1 + 3 = 9

  [ 2,  1,  5,  1,  3,  2 ]
              ├────────┤
              window = [5,1,3], sum = 9, max_sum = 9

Step 4: Slide right.
  - Remove 5, add 2
  - New sum = 9 - 5 + 2 = 6

  [ 2,  1,  5,  1,  3,  2 ]
                   ├────────┤
                   window = [1,3,2], sum = 6, max_sum = 9

No more slides. Answer: 9
```

The key: we never re-sum the whole window. Each slide is just one subtraction and one addition.

```
Formula:
  new_sum = old_sum - arr[left] + arr[right]
                      ↑ leaving    ↑ entering
```

> [↑ Back to Top](#top)

<a id="3-core-idea"></a>
# 3. Core Idea of Sliding Window

Instead of:

Rebuilding subarray every time,

You:

1. Maintain a window
2. Expand right boundary
3. Shrink left boundary when needed
4. Maintain some property (sum, count, max, etc.)

Window has two pointers:

```
left → start
right → end
```

Window moves intelligently.

> [↑ Back to Top](#top)

<a id="4-two-types"></a>
# 4. Two Types of Sliding Window

## 🔹 Fixed Size Window

Window size is constant.

Example:
Find max sum of k elements.

Window size always k.

Only slides forward.

> 📝 **Practice:** [Q24 · sliding-window-fixed](../dsa_practice_questions_100.md#q24--code--sliding-window-fixed)
> 📝 **Practice:** [Q1 — Max Sum Subarray of Size K](./practice.md#q1--max-sum-subarray-of-size-k) · [Q2 — Average of All Subarrays](./practice.md#q2--average-of-all-subarrays-of-size-k) · [Q6 — First Negative in Window](./practice.md#q6--first-negative-in-each-window-of-size-k)

## 🔹 Variable Size Window

Window grows and shrinks dynamically.

Example:
Smallest subarray with sum ≥ target.

Window expands until condition satisfied,
then shrinks to optimize.

This is more powerful.

> 📝 **Practice:** [Q25 · sliding-window-variable](../dsa_practice_questions_100.md#q25--thinking--sliding-window-variable)
> 📝 **Practice:** [Q9 — Longest Substring No Repeat](./practice.md#q9--longest-substring-without-repeating-characters) · [Q11 — Longest Subarray Sum ≤ K](./practice.md#q11--longest-subarray-with-sum--k) · [Q15 — Min Size Subarray Sum](./practice.md#q15--minimum-size-subarray-sum)

> [↑ Back to Top](#top)

<a id="5-fixed-window-step-by-step"></a>
# 5. Fixed Window — Step by Step

Example:

```
arr = [4, 2, 1, 7, 8, 1, 2, 8]
k = 3
```

Step 1:
Compute first 3 → 4+2+1 = 7

Step 2:
Slide:
Remove 4
Add 7
New sum = 7 - 4 + 7 = 10

Step 3:
Slide:
Remove 2
Add 8
New sum = 10 - 2 + 8 = 16

You never recompute full sum again.

Time:
O(n)

Space:
O(1)

**Common mistake — fixed-window off-by-one:** For a fixed window of size `k`, the correct slide condition is `right - left + 1 > k`, not `right - left > k`. The missing `+1` means your window has `k+1` elements before it shrinks — always check `right - left + 1 > k` to slide.

> [↑ Back to Top](#top)

<a id="6-variable-window"></a>
# 6. Variable Window — Growing and Shrinking

Imagine you are collecting water.

You keep adding water (expand right).

When bucket overflows (condition satisfied),
you start removing water from left.

Example:

Smallest subarray with sum ≥ 7

```
[2, 3, 1, 2, 4, 3]
```

Process:

Add 2 → sum=2  
Add 3 → sum=5  
Add 1 → sum=6  
Add 2 → sum=8 (≥7)

Now shrink:

Remove 2 → sum=6 (stop shrinking)

Continue expanding.

This grow-shrink behavior is sliding window magic.

## Visual: Longest Substring Without Repeating Characters

**Problem:** Find the longest substring where no character repeats.
**Input:** `"abcabcbb"`

The window size is not fixed. It can grow and shrink.

Rules:
- Expand (move right pointer) when the window is valid (no repeats)
- Shrink (move left pointer) when we have a repeat

```
String: a  b  c  a  b  c  b  b
Index:  0  1  2  3  4  5  6  7
```

**Step 1:** lo=0, hi=0, window=`{a}`, max_len=1

```
a  b  c  a  b  c  b  b
↑
lo/hi

Set: {a}
No repeat → expand
```

**Step 2:** lo=0, hi=1, window=`{a,b}`, max_len=2

```
a  b  c  a  b  c  b  b
↑  ↑
lo hi

Set: {a, b}
No repeat → expand
```

**Step 3:** lo=0, hi=2, window=`{a,b,c}`, max_len=3

```
a  b  c  a  b  c  b  b
↑     ↑
lo    hi

Set: {a, b, c}
No repeat → expand
```

**Step 4:** lo=0, hi=3. New char is `a`. But `a` is already in set!

```
a  b  c  a  b  c  b  b
↑        ↑
lo       hi

New char 'a' is in set {a,b,c} → COLLISION!
Must shrink from the left until 'a' is gone.

Remove arr[lo]='a' from set, lo++
Set: {b, c}, lo=1

Now 'a' is gone → add new 'a'
Set: {b, c, a}, lo=1, hi=3, max_len=3
```

**Step 5:** lo=1, hi=4. New char is `b`. But `b` is in `{b,c,a}`!

```
a  b  c  a  b  c  b  b
   ↑        ↑
   lo       hi

New char 'b' in {b,c,a} → COLLISION!
Remove arr[lo]='b', lo++
Set: {c, a}, lo=2

Now 'b' is gone → add new 'b'
Set: {c, a, b}, lo=2, hi=4, max_len=3
```

**Steps 6-8:** Similar collisions, max never exceeds 3.

```
Final answer: 3 (the substring "abc")
```

The window invariant: The window `[lo, hi]` always contains unique characters.
When we violate it, we shrink from the left until we fix it.

```
EXPAND when: adding arr[hi] doesn't break the invariant
SHRINK when: invariant is broken, remove arr[lo], advance lo
UPDATE max: after each expansion
```

**Common mistake — resetting `left` to 0:** When a collision occurs, the correct fix is to advance `left` one step at a time (`while violated: remove arr[left]; left += 1`) until the window is valid. Resetting `left = 0` throws away all progress, produces O(n²) behavior, and overcounts window length because `right - left + 1` no longer reflects the actual valid window.

> [↑ Back to Top](#top)

<a id="7-why-powerful"></a>
# 7. Why Sliding Window Is So Powerful

Without sliding window:

Nested loops:
O(n²)

With sliding window:

Each element:
- Enters window once
- Leaves window once

Total operations:
≤ 2n

Time:
O(n)

That's massive improvement.

> [↑ Back to Top](#top)

<a id="8-sliding-window-in-strings"></a>
# 8. Sliding Window in Strings

Example:

Longest substring without repeating characters.

You maintain:

- Set of characters inside window
- Expand right pointer
- If duplicate appears:
  shrink left until duplicate removed

Window always contains unique characters.

This is variable window.

> [↑ Back to Top](#top)

<a id="9-common-problems"></a>
# 9. Common Sliding Window Problems

> 📝 **Practice:** [Q1 — Max Sum K](./practice.md#q1--max-sum-subarray-of-size-k) · [Q9 — Longest No Repeat](./practice.md#q9--longest-substring-without-repeating-characters) · [Q10 — Min Window](./practice.md#q10--minimum-window-substring) · [Q12 — All Anagrams](./practice.md#q12--find-all-anagrams-in-a-string) · [Q13 — Permutation in String](./practice.md#q13--permutation-in-string) · [Q21 — SW Maximum](./practice.md#q21--sliding-window-maximum-deque)

- Maximum sum subarray of size k
- Longest substring without repeating characters
- Minimum window substring
- Smallest subarray with given sum
- Permutation in string
- Sliding window maximum (deque based)
- Count occurrences of anagram

Most substring problems use sliding window.

## Visual: Minimum Window Substring

**Problem:** Find the shortest substring of `s` that contains all characters of `t`.
**s = `"ADOBECODEBANC"`**, **t = `"ABC"`**

Expand until we have all required characters, then shrink to minimize.

**Setup:**

```
need = {'A': 1, 'B': 1, 'C': 1}   ← characters we need
have = {}                           ← characters in current window
formed = 0                          ← how many UNIQUE chars are fully satisfied
required = 3                        ← len(need)
```

We increment `formed` only when a character's count in `have` exactly matches its count in `need`.

**Expand until formed == required:**

```
s: A  D  O  B  E  C  O  D  E  B  A  N  C
   0  1  2  3  4  5  6  7  8  9  10 11 12

lo=0, hi=0: Add 'A'. have={'A':1}. A satisfied → formed=1
lo=0, hi=1: Add 'D'. not in need, ignore.
lo=0, hi=2: Add 'O'. not in need, ignore.
lo=0, hi=3: Add 'B'. have={'A':1,'B':1}. B satisfied → formed=2
lo=0, hi=4: Add 'E'. not in need, ignore.
lo=0, hi=5: Add 'C'. have={'A':1,'B':1,'C':1}. C satisfied → formed=3

formed == required → we have a valid window!
Window: s[0:6] = "ADOBEC" (length 6)
```

**Shrink to minimize:**

```
Window: "ADOBEC", lo=0, hi=5

Shrink from left:
  Remove 'A'. have={'A':0,'B':1,'C':1}. A no longer satisfied → formed=2
  lo=1

formed < required → stop shrinking, start expanding again.
```

**Key idea:**

```
EXPAND: move hi right until all chars are covered (formed == required)
SHRINK: move lo right to minimize window, stop when a char becomes missing
RECORD: whenever formed == required, check if this window beats the best
```

**Common mistake — `formed` counter increments too many times:** When tracking whether a character's required count is met, use `have[ch] == need[ch]` (not `>=`). Using `>=` causes `formed` to increment each time the count overshoots, permanently inflating it. The fix: increment `formed` only at the exact moment of satisfaction (`==`), and decrement only when count falls below the requirement.

**Common mistake — using `set(t)` instead of `Counter(t)`:** A set treats `"aa"` identically to `"a"` — it tracks presence, not quantity. Any window with one `'a'` will satisfy a requirement of two `'a'`s. Always use `Counter(t)` when the problem involves required character frequencies.

> [↑ Back to Top](#top)

<a id="10-sliding-window-maximum"></a>
# 10. Sliding Window Maximum — Deque

> 📝 **Practice:** [Q4 — Fixed Window Off-by-One](./practice.md#q4--fixed-window-off-by-one) · [Q17 — Shrink vs Expand](./practice.md#q17--shrink-vs-expand--which-loop) · [Q22 — Duplicates in T](./practice.md#q22--minimum-window-substring-with-duplicates-in-t) · [Q8 — When SW Fails](./practice.md#q8--when-sliding-window-fails)

For each window position, find the maximum element.
Naively this is O(nk). A monotonic deque brings it to O(n).

The deque stores **indices** of potentially useful elements in **decreasing order of value**.
Before adding a new element, pop from the back any element smaller than the new one — they can never be a maximum while the new (larger) element is in the window.

## Visual: Deque Window Step by Step

**Input:** `[1, 3, -1, -3, 5, 3, 6, 7]`, k=3

```
Step 1: i=0, val=1
  Deque (indices): [0]   ← values: [1]
  Window not full yet.

Step 2: i=1, val=3
  3 > arr[deque.back()]=1 → pop 0 from back
  Deque (indices): [1]   ← values: [3]
  Window not full yet.

Step 3: i=2, val=-1
  -1 < arr[deque.back()]=3 → keep 1
  Add 2 to back.
  Deque (indices): [1, 2]   ← values: [3, -1]
  Window [1,3,-1] is full. Max = arr[deque.front()] = arr[1] = 3
  Output: [3]

Step 4: i=3, val=-3
  -3 < arr[deque.back()]=-1 → keep 2
  Add 3 to back.
  Deque (indices): [1, 2, 3]   ← values: [3, -1, -3]
  Is front (index 1) still in window [1,2,3]? Yes. Max = arr[1] = 3.
  Output: [3, 3]

Step 5: i=4, val=5
  5 > arr[3]=-3 → pop 3
  5 > arr[2]=-1 → pop 2
  5 > arr[1]=3  → pop 1
  Deque empty. Add 4.
  Deque (indices): [4]   ← values: [5]
  Is front (index 4) in window [2,3,4]? Yes. Max = arr[4] = 5.
  Output: [3, 3, 5]

Step 6: i=5, val=3
  3 < arr[4]=5 → keep 4
  Add 5.
  Deque (indices): [4, 5]   ← values: [5, 3]
  Is front (index 4) in window [3,4,5]? Yes. Max = 5.
  Output: [3, 3, 5, 5]

Step 7: i=6, val=6
  6 > arr[5]=3 → pop 5
  6 > arr[4]=5 → pop 4
  Add 6.
  Deque (indices): [6]   ← values: [6]
  Is front (index 6) in window [4,5,6]? Yes. Max = 6.
  Output: [3, 3, 5, 5, 6]

Step 8: i=7, val=7
  7 > arr[6]=6 → pop 6
  Add 7.
  Deque (indices): [7]   ← values: [7]
  Is front (index 7) in window [5,6,7]? Yes. Max = 7.
  Output: [3, 3, 5, 5, 6, 7]
```

The deque always stores candidates for the maximum. Its front is always the current maximum.

**Common mistake — wrong deque pop direction:** Use `nums[back] < nums[i]` (strictly less) to pop from the back. Using `nums[back] >= nums[i]` reverses the logic — you end up with a monotonic increasing deque, which produces the window minimum, not the maximum. Also avoid `<=` when duplicate maxima matter, as it discards the earlier index of a tied value.

```
Deque pop condition reference:
  Decreasing deque (for max):  pop back when nums[back] < nums[i]
  Increasing deque (for min):  pop back when nums[back] > nums[i]
  Wrong direction (gives min): pop back when nums[back] >= nums[i]
```

## Visual: Pattern Summary

```
┌─────────────────────┬──────────────────────────────────────────┐
│ Pattern             │ Use When                                  │
├─────────────────────┼──────────────────────────────────────────┤
│ Fixed Window        │ "max/min/sum of k consecutive elements"   │
│ (window size = k)   │ Slide: remove left, add right             │
├─────────────────────┼──────────────────────────────────────────┤
│ Variable Window     │ "longest substring with property X"       │
│ (expand & find max) │ Expand until invalid, shrink until valid  │
├─────────────────────┼──────────────────────────────────────────┤
│ Variable Window     │ "smallest window containing X"            │
│ (shrink & find min) │ Expand until all satisfied, then shrink   │
├─────────────────────┼──────────────────────────────────────────┤
│ Deque Window        │ "max/min of each window position"         │
│ (monotonic deque)   │ Pop smaller elements, front is always max │
└─────────────────────┴──────────────────────────────────────────┘
```

> [↑ Back to Top](#top)

<a id="11-vs-two-pointers"></a>
# 11. Sliding Window vs Two Pointers

> 📝 **Practice:** [Q7 — Sliding Window vs Two Pointers](./practice.md#q7--sliding-window-vs-two-pointers)

Two pointers:
Movement without maintaining internal state.

Sliding window:
Two pointers + maintained property (sum, set, map, etc.)

Sliding window is enhanced two-pointer technique.

> [↑ Back to Top](#top)

<a id="12-maintaining-window-state"></a>
# 12. Maintaining Window State

Window often maintains:

- Current sum
- Character frequency
- Count of distinct elements
- Maximum value
- Minimum value

Instead of recalculating,
you update incrementally.

That is optimization.

> [↑ Back to Top](#top)

<a id="13-real-life-applications"></a>
# 13. Real Life Applications

- Network packet buffering
- Rate limiting systems
- Data stream processing
- Real-time analytics
- Moving averages in finance
- Monitoring CPU usage over time

Sliding window models real-time systems.

> [↑ Back to Top](#top)

<a id="14-mental-model"></a>
# 14. Mental Model to Remember

Imagine a rubber band.

It stretches (expand).
It contracts (shrink).

But it always stays connected.

You never rebuild entire array.
You just adjust boundaries.

That is sliding window thinking.

> A sliding window avoids re-computing things you've already computed.
> When you slide, you don't recalculate the whole window — you just
> undo the contribution of the element that left and add the element that joined.

If you find yourself thinking "I need to check a contiguous range of elements repeatedly," reach for the sliding window.

> [↑ Back to Top](#top)

<a id="15-final-understanding"></a>
# 15. Final Understanding

Sliding window is:

- A dynamic boundary technique
- Built on two pointers
- Used for substring/subarray problems
- Reduces O(n²) to O(n)
- Requires maintaining window property
- Extremely common in interviews

If you master sliding window,
medium-level string problems become easy.

It is one of the most powerful patterns in DSA.

> [↑ Back to Top](#top)

# 🔁 Navigation

Previous:  
[11_two_pointers/theory.md](/02_DSA_Mastery/11_two_pointers/theory.md)

Next:  
[12_sliding_window/interview.md](/02_DSA_Mastery/12_sliding_window/interview.md)  
[13_binary_search/theory.md](/02_DSA_Mastery/13_binary_search/theory.md)

**[🏠 Back to README](../README.md)**

**Prev:** [← Two Pointers — Interview Q&A](../11_two_pointers/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
