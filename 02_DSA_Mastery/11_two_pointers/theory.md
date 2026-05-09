<a id="top"></a>
# Two Pointers — Thinking With Two Moving Hands

> Two pointers is not a data structure.
> It is a technique.
>
> It transforms brute-force O(n²) solutions
> into efficient O(n) or O(n log n).

Two pointers is about controlled movement.

Instead of scanning everything repeatedly,
you move intelligently.

## 📖 Table of Contents

1. [Real-Life Analogy — Finding a Book Between Two People](#1-real-life-analogy)
2. [The Core Idea](#2-the-core-idea)
3. [When Two Pointers Is Applicable](#3-when-two-pointers-is-applicable)
4. [Two Main Types of Two Pointer Techniques](#4-two-main-types)
5. [Example — Two Sum in Sorted Array](#5-two-sum-in-sorted-array)
6. [Why It Works](#6-why-it-works)
7. [Removing Duplicates from Sorted Array](#7-removing-duplicates)
8. [Palindrome Checking](#8-palindrome-checking)
9. [Container With Most Water](#9-container-with-most-water)
10. [Partitioning Problems](#10-partitioning-problems)
11. [Two Pointers vs Hashing](#11-two-pointers-vs-hashing)
12. [Two Pointers in Linked List](#12-two-pointers-in-linked-list)
13. [Common Mistakes](#13-common-mistakes)
14. [Performance Advantage](#14-performance-advantage)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
opposite-direction pointers · same-direction pointers · two sum sorted

**Should Learn** — Important for real projects, comes up regularly:
when to use two pointers vs hashmap · removing duplicates · palindrome check

**Good to Know** — Useful in specific situations, not always tested:
container with most water · partition pattern

**Reference** — Know it exists, look up syntax when needed:
two pointers on different arrays · three-pointer variants

<a id="1-real-life-analogy"></a>
# 1. Real-Life Analogy — Finding a Book Between Two People

Imagine two people standing at opposite ends of a long shelf.

One starts from left.
One starts from right.

They move toward each other,
checking books until they meet.

Instead of one person checking entire shelf,
two people divide work efficiently.

That is two pointers.

## Visual: Brute Force vs Two Pointers

You're at a bookshelf looking for two books whose combined thickness equals exactly 10cm.

**Approach 1 (Brute Force):** Pick up book 1, measure it against every other book. Then book 2 against every other. Then book 3...

If there are 100 books, you make roughly 5,000 comparisons. That is O(n²).

**Approach 2 (Two Pointers):** Sort the books by thickness. Put your left finger at the thinnest book, right finger at the thickest. Check the pair. Too thick? Move the right finger left. Too thin? Move the left finger right.

You'll find the answer in at most 100 moves. That is O(n).

```
Brute Force:    every pair
                (0,1)(0,2)(0,3)...(0,99)
                (1,2)(1,3)...(1,99)
                ...
                = n*(n-1)/2 pairs

Two Pointers:   start outside, move inward
                L→→→→  ←←←←R
                = at most n moves
```

Same problem. Two fingers. 50x fewer comparisons.

> [↑ Back to Top](#top)

<a id="2-the-core-idea"></a>
# 2. The Core Idea

Instead of using nested loops:

```
for i in range(n):
    for j in range(n):
```

We use:

```
left = 0
right = n - 1
```

And move them based on condition.

Two pointers reduces redundant work.

## Visual: Pattern Cheat Sheet

```
┌─────────────────────────────────────────────────────────────┐
│                   TWO POINTER PATTERNS                       │
├──────────────────┬──────────────────────────────────────────┤
│ Opposite ends    │ Array is sorted, looking for pair/combo   │
│  L ────→ ←──── R│ Two Sum, Container with Water, 3Sum       │
├──────────────────┼──────────────────────────────────────────┤
│ Same direction   │ One pointer reads, one writes             │
│  S──→            │ Remove duplicates, partition, filter      │
│  F──────→        │                                           │
├──────────────────┼──────────────────────────────────────────┤
│ Fast/Slow        │ Detecting cycles, finding middle          │
│  S─→             │ Linked list cycle, Floyd's algorithm       │
│  F──→            │                                           │
└──────────────────┴──────────────────────────────────────────┘
```

**The golden rule:** You need to be able to answer "why is it safe to discard this element?" If you can answer that, two pointers will work.

> The one-liner mental model: Two pointers work because at each step, you can logically eliminate part of the search space. You are not guessing — you are using the sorted order (or structure) to prove certain options cannot be the answer.

> [↑ Back to Top](#top)

<a id="3-when-two-pointers-is-applicable"></a>
# 3. When Two Pointers Is Applicable

Look for:

- Sorted arrays
- Pairs or triplets
- Subarray problems
- Reversing problems
- Partitioning problems
- Removing duplicates
- Palindrome checking

If you see "pair", "sum", "opposite ends",
consider two pointers.

**Common mistake — applying to unsorted input:** The converging two-pointer pattern only works on sorted arrays. The logic `sum < target → move left right` assumes smaller values are on the left. On an unsorted array that assumption is false, so the search terminates in the wrong direction. Sort first, or use a hash map for unsorted input.

> [↑ Back to Top](#top)

<a id="4-two-main-types"></a>
# 4. Two Main Types of Two Pointer Techniques

## 🔹 Opposite Direction

One pointer at start,
one at end.

Move inward.

Used in:

- Two Sum (sorted)
- Palindrome
- Container with most water

> 📝 **Practice:** [Q2 — Two Sum in Sorted Array](./practice.md#q2--two-sum-sorted) · [Q1 — Valid Palindrome](./practice.md#q1--valid-palindrome) · [Q9 — Container With Most Water](./practice.md#q9--container-with-most-water)

## Visual: Converging Inward

This works on **sorted** arrays. One pointer starts at the left, one at the right. They walk toward each other.

```
Converging inward:

[ 1,  3,  5,  7,  9 ]
  L→               ←R     sum=10, too big
  L→         ←R           sum=8,  found!

If not found, pointers would cross and we'd exit.
```

```
sum > target  →  move hi left   (decrease the big number)
sum < target  →  move lo right  (increase the small number)
sum = target  →  found!
lo >= hi      →  no solution
```

## 🔹 Same Direction

Both pointers move forward.

Used in:

- Removing duplicates
- Partitioning
- Slow-fast pointer problems
- Sliding window foundation

> 📝 **Practice:** [Q3 — Remove Duplicates](./practice.md#q3--remove-duplicates) · [Q4 — Move Zeros](./practice.md#q4--move-zeros) · [Q12 — Partition Around Value](./practice.md#q12--partition-around-value)

## Visual: Same Direction — Fast and Slow

Both pointers start at the left but move at different speeds or for different purposes.
Think of it as: one pointer **reads**, one pointer **writes**.

```
Initial:
[ 1,  1,  2,  3,  3,  4 ]
  ↑
  slow=0, fast=0

slow = the write position (where to put the next unique element)
fast = the reader (scanning through every element)
```

> [↑ Back to Top](#top)

<a id="5-two-sum-in-sorted-array"></a>
# 5. Example — Two Sum in Sorted Array

Given sorted array:

```
[1, 2, 4, 6, 10]
```

Target = 8

Initialize:

left = 0 (1)
right = 4 (10)

Check:
1 + 10 = 11 → too big → move right left

Now:
1 + 6 = 7 → too small → move left right

Now:
2 + 6 = 8 → found

Time:
O(n)

Instead of O(n²).

## Visual: Two Sum Step-by-Step

**Input:** `[1, 3, 5, 7, 9]`, target = `8`

```
Array:  [ 1,  3,  5,  7,  9 ]
Index:    0   1   2   3   4

lo = 0 (pointing at 1)
hi = 4 (pointing at 9)
```

**Step 1:**

```
[ 1,  3,  5,  7,  9 ]
  ↑               ↑
  lo              hi

sum = 1 + 9 = 10
10 > 8 (too big)
Must decrease sum → move hi LEFT
```

**Step 2:**

```
[ 1,  3,  5,  7,  9 ]
  ↑           ↑
  lo          hi

sum = 1 + 7 = 8
8 == 8 → FOUND! Return [lo, hi] = [0, 3]
```

Done in 2 steps instead of checking all 10 pairs.

**Why does this work? The math:**

When sum is too big, we need a smaller value. The only way to get smaller is to move the right pointer left (decrease the larger number). We cannot move left pointer right — that would make things even bigger.

When sum is too small, we need a bigger value. Move the left pointer right.

**Common mistake — converging pointers on unsorted array:** Running this pattern directly on an unsorted array silently returns wrong answers or misses valid pairs. Always sort first (losing original indices), or use a hash map when original indices must be preserved.

> 📝 **Practice:** [Q10 — Three Sum](./practice.md#q10--three-sum) · [Q21 — Four Sum](./practice.md#q21--four-sum)

> [↑ Back to Top](#top)

<a id="6-why-it-works"></a>
# 6. Why It Works

Because array is sorted.

If sum too large:
Moving right pointer left reduces sum.

If sum too small:
Moving left pointer right increases sum.

Sorted order enables directional movement.

> 📝 **Practice:** [Q8 — Why O(n) Beats O(n²)](./practice.md#q8--when-two-pointers-beats-brute-force) · [Q16 — Choosing Pointer Direction](./practice.md#q16--choosing-pointer-direction)

> [↑ Back to Top](#top)

<a id="7-removing-duplicates"></a>
# 7. Removing Duplicates from Sorted Array

Given:

```
[1, 1, 2, 2, 3]
```

Use:

- slow pointer
- fast pointer

Fast scans.
Slow updates unique elements.

Result:
[1, 2, 3]

Time:
O(n)
Space:
O(1)

Efficient in-place solution.

## Visual: Remove Duplicates Step-by-Step

**Input:** `[1, 1, 2, 3, 3, 4]`
**Goal:** Remove duplicates in-place, return the count of unique elements.

**Step 1:** fast=0, slow=0

```
[ 1,  1,  2,  3,  3,  4 ]
  SF                        (both pointing at 1)

arr[fast]=1 is unique (nothing before it).
Write it. slow moves forward.

slow=1, fast=1
```

**Step 2:** fast=1

```
[ 1,  1,  2,  3,  3,  4 ]
  ^   SF
  ↑
  already written

arr[fast]=1 == arr[fast-1]=1 → DUPLICATE, skip it.
Only fast moves forward.

slow=1, fast=2
```

**Step 3:** fast=2

```
[ 1,  1,  2,  3,  3,  4 ]
      ↑   ↑
    slow  fast

arr[fast]=2 ≠ arr[fast-1]=1 → NEW element!
Write 2 at slow position.

Array becomes:
[ 1,  2,  2,  3,  3,  4 ]
          ↑
      slow=2, fast=3
```

**Step 4:** fast=3

```
[ 1,  2,  2,  3,  3,  4 ]
          ↑   ↑
        slow  fast

arr[fast]=3 ≠ arr[fast-1]=2 → NEW element!
Write 3 at slow=2.

Array becomes:
[ 1,  2,  3,  3,  3,  4 ]
              ↑
          slow=3, fast=4
```

**Step 5:** fast=4

```
arr[fast]=3 == arr[fast-1]=3 → DUPLICATE, skip.
slow=3, fast=5
```

**Step 6:** fast=5

```
[ 1,  2,  3,  3,  3,  4 ]
              ↑       ↑
            slow      fast

arr[fast]=4 ≠ arr[fast-1]=3 → NEW element!
Write 4 at slow=3.

Final: [ 1,  2,  3,  4,  _,  _ ]  ← first 4 elements are unique
```

The first 4 elements `[1, 2, 3, 4]` are the answer. The remainder after slow does not matter.

> 📝 **Practice:** [Q3 — Remove Duplicates](./practice.md#q3--remove-duplicates) · [Q11 — Remove Element In-Place](./practice.md#q11--remove-element-in-place)

> [↑ Back to Top](#top)

<a id="8-palindrome-checking"></a>
# 8. Palindrome Checking

Given string:

```
"racecar"
```

left = 0
right = len(s) - 1

Compare s[left] and s[right].

If equal → move inward.

If mismatch → not palindrome.

Time:
O(n)

This is classic opposite-direction two pointers.

**Common mistake — off-by-one in loop condition:** Using `while left <= right` instead of `while left < right` causes a redundant comparison when pointers meet at the middle character (compares character to itself). This is harmless for a simple palindrome check but signals a flawed invariant and causes real bugs in related variations like palindromic substring counting. Use `while left < right` for palindrome checks; use expand-around-center for counting palindromic substrings.

> 📝 **Practice:** [Q1 — Valid Palindrome](./practice.md#q1--valid-palindrome) · [Q18 — Valid Palindrome II](./practice.md#q18--valid-palindrome-ii) · [Q20 — Wrong Stop Condition Bug](./practice.md#q20--wrong-stop-condition)

> [↑ Back to Top](#top)

<a id="9-container-with-most-water"></a>
# 9. Container With Most Water

Given heights array.

Use two pointers at ends.

Area determined by:

min(height[left], height[right]) × width

Move pointer pointing to smaller height.

Why?

Because area limited by smaller height.

Moving taller one won't increase area.

This is logic-based movement.

## Visual: Container With Most Water Step-by-Step

**Input:** `[1, 8, 6, 2, 5, 4, 8, 3, 7]`
Each number represents a wall height. Find two walls that hold the most water.

```
Walls visualized:

    8           8
    █       █   █
    █   █   █   █   7
    █   █ █ █   █   █
    █   █ █ █   █   █
1   █   █ █ █   █ █ █
─────────────────────
0   1   2 3 4   5 6 7 8   ← index

Heights: [1, 8, 6, 2, 5, 4, 8, 3, 7]
```

Water between walls at index `lo` and `hi`:

```
water = min(height[lo], height[hi]) * (hi - lo)
         ↑ limited by shorter wall    ↑ width
```

**Strategy:** Start with max width (lo=0, hi=8). Move pointers inward.

**Key insight:** Always move the SHORTER wall's pointer. The water is limited by the shorter wall. Moving the taller wall inward definitely cannot do better (we lose width AND the limiting factor does not change). Moving the shorter wall is our only chance to find a taller partner.

```
Step 1: lo=0, hi=8
  height[0]=1, height[8]=7
  water = min(1,7) * (8-0) = 1 * 8 = 8
  Move shorter (lo) → lo=1

Step 2: lo=1, hi=8
  height[1]=8, height[8]=7
  water = min(8,7) * (8-1) = 7 * 7 = 49  ← new max!
  Move shorter (hi) → hi=7

Step 3: lo=1, hi=7
  height[1]=8, height[7]=3
  water = min(8,3) * (7-1) = 3 * 6 = 18
  Move shorter (hi) → hi=6

Step 4: lo=1, hi=6
  height[1]=8, height[6]=8
  water = min(8,8) * (6-1) = 8 * 5 = 40
  Tie: move either → hi=5

Step 5: lo=1, hi=5
  height[1]=8, height[5]=4
  water = min(8,4) * (5-1) = 4 * 4 = 16
  Move shorter (hi) → hi=4

Step 6: lo=1, hi=4
  height[1]=8, height[4]=5
  water = min(8,5) * (4-1) = 5 * 3 = 15
  Move shorter (hi) → hi=3

Step 7: lo=1, hi=3
  height[1]=8, height[3]=2
  water = min(8,2) * (3-1) = 2 * 2 = 4
  Move shorter (hi) → hi=2

Step 8: lo=1, hi=2
  height[1]=8, height[2]=6
  water = min(8,6) * (2-1) = 6 * 1 = 6
  Move shorter (hi) → hi=1

lo >= hi → STOP

Maximum water found = 49 (at lo=1, hi=8)
```

> 📝 **Practice:** [Q9 — Container With Most Water](./practice.md#q9--container-with-most-water)

> [↑ Back to Top](#top)

<a id="10-partitioning-problems"></a>
# 10. Partitioning Problems

Example:
Move all zeros to end.

Use:

- slow pointer for placement
- fast pointer for scanning

When non-zero found:
Swap with slow pointer.

Time:
O(n)

Two pointers helps rearrange in-place.

**Common mistake — Dutch National Flag: advancing mid after swap with hi:** In the three-pointer Dutch National Flag algorithm (sort 0s, 1s, 2s in-place), when `nums[mid] == 2` you swap `mid` with `hi` and must NOT advance `mid`. The element swapped in from `hi` is unclassified. Only advance `mid` when it sees a 0 or 1.

```
Invariant at all times:
  nums[0 .. lo-1]   = all 0s
  nums[lo .. mid-1] = all 1s
  nums[mid .. hi]   = UNKNOWN (to be processed)
  nums[hi+1 .. n-1] = all 2s
```

> 📝 **Practice:** [Q4 — Move Zeros](./practice.md#q4--move-zeros) · [Q12 — Partition Around Value](./practice.md#q12--partition-around-value) · [Q13 — Sort Colors (Dutch Flag)](./practice.md#q13--sort-colors-dutch-flag)

> [↑ Back to Top](#top)

<a id="11-two-pointers-vs-hashing"></a>
# 11. Two Pointers vs Hashing

Two pointers requires sorted data.

Hashing works on unsorted data.

Example:

Two Sum:

Sorted:
Use two pointers → O(n)

Unsorted:
Use hashmap → O(n)

Choose technique based on input condition.

> 📝 **Practice:** [Q19 — Two Pointers vs Hash Map Decision](./practice.md#q19--two-pointers-vs-hashmap)

> [↑ Back to Top](#top)

<a id="12-two-pointers-in-linked-list"></a>
# 12. Two Pointers in Linked List

Fast and slow pointer pattern:

- Detect cycle
- Find middle
- Remove nth node

Two pointers applies beyond arrays.

## Visual: Cycle Detection

Fast and slow pointers work for linked list cycles.

```
Slow moves 1 step:  A → B → C → D
Fast moves 2 steps: A → C → E → B → D → ...

If there's a cycle, fast laps slow and they meet.
If no cycle, fast reaches null first.
```

That is Floyd's algorithm.

**Common mistake — not checking `fast.next` before `fast.next.next`:** The fast/slow pattern advances `fast` two steps per iteration. To do that safely, both `fast` and `fast.next` must be non-None. Checking only `fast.next.next` raises `AttributeError` when `fast.next` is `None` — you are calling `.next` on None. Always guard with `while fast and fast.next`.

```
Correct guard:
  while fast and fast.next:   ← check BOTH
      slow = slow.next
      fast = fast.next.next
```

> 📝 **Practice:** [Q6 — Cycle Detection](./practice.md#q6--cycle-detection) · [Q7 — Middle of Linked List](./practice.md#q7--middle-of-linked-list) · [Q17 — Cycle Entry Point](./practice.md#q17--cycle-entry-point) · [Q25 — Nth Node From End](./practice.md#q25--nth-node-from-end)

> [↑ Back to Top](#top)

<a id="13-common-mistakes"></a>
# 13. Common Mistakes

- Moving wrong pointer
- Infinite loops
- Forgetting sorted requirement
- Not handling duplicates properly
- Incorrect boundary conditions

Two pointer logic must be precise.

**Common mistake — infinite loop (pointer not advancing):** Every iteration of a two-pointer loop must move at least one pointer. The most common form is handling the equal case without advancing either pointer. After finding a match in 3Sum, you must advance both `left += 1` and `right -= 1` before skipping duplicates. Use this checklist after writing any two-pointer loop:

```
After every iteration, ask:
  [ ] Did I advance left OR right?
  [ ] Is there any code path where neither pointer moves?
  [ ] After handling duplicates, did I also advance past the current element?
```

> 📝 **Practice:** [Q20 — Wrong Stop Condition Bug](./practice.md#q20--wrong-stop-condition) · [Q24 — Not Moving Both Pointers Bug](./practice.md#q24--not-moving-both-pointers-bug)

> [↑ Back to Top](#top)

<a id="14-performance-advantage"></a>
# 14. Performance Advantage

Without two pointers:
O(n²)

With two pointers:
O(n)

Massive improvement for large inputs.

Example:
n = 10⁵

O(n²) → impossible
O(n) → feasible

Two pointers is optimization mindset.

> 📝 **Practice:** [Q8 — Why O(n) Beats O(n²)](./practice.md#q8--when-two-pointers-beats-brute-force)

> [↑ Back to Top](#top)

# Final Understanding

Two pointers is:

- A movement strategy
- A pattern recognition skill
- Based on direction control
- Often requires sorted data
- Reduces nested loops

It prepares you for:

- Sliding window
- Greedy problems
- Binary search variations
- Advanced optimization patterns

Two pointers is where problem-solving becomes elegant.

# Navigation

Previous:
[10_hashing/theory.md](/02_DSA_Mastery/10_hashing/theory.md)

Next:
[11_two_pointers/interview.md](/02_DSA_Mastery/11_two_pointers/interview.md)
[12_sliding_window/theory.md](/02_DSA_Mastery/12_sliding_window/theory.md)

**[🏠 Back to README](../README.md)**

**Prev:** [← Hashing — Interview Q&A](../10_hashing/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
