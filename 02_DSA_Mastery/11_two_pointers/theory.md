<a id="top"></a>
# 📘 11 – Two Pointers in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is Two Pointers?](#1-what-is-two-pointers)
  - [Visual: Brute Force vs Two Pointers](#visual-brute-vs-two)
  - [Visual: Pattern Cheat Sheet](#visual-pattern-sheet)
- [2. When Two Pointers Is Applicable](#2-when-applicable)
- [3. Opposite Direction — Converging Pointers](#3-opposite-direction)
  - [Visual: Converging Inward](#visual-converging)
- [4. Same Direction — Fast and Slow](#4-same-direction)
  - [Visual: Reader/Writer Pattern](#visual-reader-writer)
- [5. Two Sum in Sorted Array](#5-two-sum)
  - [Visual: Two Sum Step-by-Step](#visual-two-sum)
- [6. Removing Duplicates from Sorted Array](#6-remove-duplicates)
  - [Visual: Remove Duplicates Step-by-Step](#visual-remove-dups)
- [7. Palindrome Checking](#7-palindrome)
- [8. Container With Most Water](#8-container-water)
  - [Visual: Container Step-by-Step](#visual-container)
- [9. Partitioning Problems](#9-partitioning)
- [10. Two Pointers in Linked List](#10-linked-list)
  - [Visual: Cycle Detection](#visual-cycle)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
opposite-direction pointers · same-direction pointers · two sum sorted

**Should Learn** — Important for real projects, comes up regularly:
when to use two pointers vs hashmap · removing duplicates · palindrome check

**Good to Know** — Useful in specific situations, not always tested:
container with most water · partition pattern

**Reference** — Know it exists, look up syntax when needed:
two pointers on different arrays · three-pointer variants

Dex is a card dealer at a casino. He uses both hands simultaneously — left hand on one end of the table, right hand on the other. Instead of scanning every card one by one (O(n²) comparisons), he moves both hands intelligently toward each other, eliminating possibilities with every move. That is **two pointers** — a technique that transforms brute-force nested loops into elegant O(n) solutions through controlled, intelligent movement.

<a id="1-what-is-two-pointers"></a>
# 1. What Is Two Pointers?

Dex discovers that two pointers is not a data structure — it is a movement strategy. Instead of scanning everything repeatedly with nested loops, he places two fingers on the data and moves them based on logic.

Two people stand at opposite ends of a long shelf looking for two books whose combined thickness equals exactly 10cm. Instead of one person checking every pair (5,000 comparisons for 100 books), they each check from their end and move inward. At most 100 moves. O(n) instead of O(n²).

<a id="visual-brute-vs-two"></a>
## Visual: Brute Force vs Two Pointers

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

<a id="visual-pattern-sheet"></a>
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

The golden rule: you need to be able to answer "why is it safe to discard this element?" If you can, two pointers will work.

> [↑ Back to Top](#top)

<a id="2-when-applicable"></a>
# 2. When Two Pointers Is Applicable

Dex knows to reach for two pointers when he sees these signals in a problem:

- Sorted arrays
- Pairs or triplets
- Subarray problems
- Reversing problems
- Partitioning problems
- Removing duplicates
- Palindrome checking

If you see "pair", "sum", "opposite ends" — consider two pointers.

**Common mistake — applying to unsorted input:** The converging pattern only works on sorted arrays. `sum < target → move left right` assumes smaller values are on the left. On unsorted arrays, sort first or use a hash map.

> [↑ Back to Top](#top)

<a id="3-opposite-direction"></a>
# 3. Opposite Direction — Converging Pointers

Dex places his left hand at the start and right hand at the end. They walk toward each other, making decisions at every step based on the current state. This is the most common two-pointer pattern.

Used in: Two Sum (sorted), palindrome, container with most water, 3Sum.

<a id="visual-converging"></a>
## Visual: Converging Inward

```
Converging inward on sorted array:

[ 1,  3,  5,  7,  9 ]
  L→               ←R     sum=10, too big → move R left
  L→         ←R           sum=8,  found!

Rules:
sum > target  →  move hi left   (decrease the big number)
sum < target  →  move lo right  (increase the small number)
sum = target  →  found!
lo >= hi      →  no solution
```

> 📝 **Practice:** [Q2 — Two Sum in Sorted Array](./practice.md#q2--two-sum-sorted) · [Q1 — Valid Palindrome](./practice.md#q1--valid-palindrome) · [Q9 — Container With Most Water](./practice.md#q9--container-with-most-water)

> [↑ Back to Top](#top)

<a id="4-same-direction"></a>
# 4. Same Direction — Fast and Slow

Dex uses both hands moving forward but at different speeds. One hand reads (scans every card), the other writes (places kept cards). Think of it as a reader/writer pattern.

Used in: removing duplicates, partitioning, move zeros, sliding window foundation.

<a id="visual-reader-writer"></a>
## Visual: Reader/Writer Pattern

```
Initial:
[ 1,  1,  2,  3,  3,  4 ]
  ↑
  slow=0, fast=0

slow = the write position (where to put the next unique element)
fast = the reader (scanning through every element)
```

> 📝 **Practice:** [Q3 — Remove Duplicates](./practice.md#q3--remove-duplicates) · [Q4 — Move Zeros](./practice.md#q4--move-zeros) · [Q12 — Partition Around Value](./practice.md#q12--partition-around-value)

> [↑ Back to Top](#top)

<a id="5-two-sum"></a>
# 5. Two Sum in Sorted Array

Dex receives a sorted hand of cards and must find two that sum to a target. Left finger on the smallest, right on the largest. Too big? Move right left. Too small? Move left right.

**Input:** `[1, 3, 5, 7, 9]`, target = `8`

<a id="visual-two-sum"></a>
## Visual: Two Sum Step-by-Step

```
Array:  [ 1,  3,  5,  7,  9 ]
Index:    0   1   2   3   4

Step 1:
  lo=0 (1), hi=4 (9)
  sum = 1 + 9 = 10 > 8 → move hi left

Step 2:
  lo=0 (1), hi=3 (7)
  sum = 1 + 7 = 8 == 8 → FOUND! Return [0, 3]
```

Done in 2 steps instead of checking all 10 pairs.

**Why it works:** When sum is too big, moving right left is the only way to decrease. When too small, moving left right is the only way to increase. Sorted order guarantees directional correctness.

**Common mistake — converging on unsorted array:** Silently returns wrong answers. Sort first (losing indices) or use hash map when indices matter.

> 📝 **Practice:** [Q10 — Three Sum](./practice.md#q10--three-sum) · [Q21 — Four Sum](./practice.md#q21--four-sum)

> [↑ Back to Top](#top)

<a id="6-remove-duplicates"></a>
# 6. Removing Duplicates from Sorted Array

Dex has a sorted hand with duplicate cards. He uses two fingers: fast scans every card, slow tracks where the next unique card should be placed.

**Input:** `[1, 1, 2, 3, 3, 4]`

<a id="visual-remove-dups"></a>
## Visual: Remove Duplicates Step-by-Step

```
Step 1: fast=0, slow=0
[ 1,  1,  2,  3,  3,  4 ]
  SF
arr[fast]=1, unique. Write. slow=1, fast=1

Step 2: fast=1
[ 1,  1,  2,  3,  3,  4 ]
      SF
arr[1]=1 == arr[0]=1 → DUPLICATE, skip. fast=2

Step 3: fast=2
[ 1,  1,  2,  3,  3,  4 ]
      ↑   ↑
    slow  fast
arr[2]=2 ≠ arr[1]=1 → NEW! Write 2 at slow.
Array: [ 1,  2,  2,  3,  3,  4 ]  slow=2, fast=3

Step 4: fast=3
arr[3]=3 ≠ arr[2]=2 → NEW! Write 3. slow=3, fast=4

Step 5: fast=4
arr[4]=3 == arr[3]=3 → DUPLICATE. fast=5

Step 6: fast=5
arr[5]=4 ≠ arr[4]=3 → NEW! Write 4. slow=4

Final: [ 1,  2,  3,  4,  _,  _ ]  ← first 4 are unique
```

Time: O(n). Space: O(1). Efficient in-place solution.

> 📝 **Practice:** [Q3 — Remove Duplicates](./practice.md#q3--remove-duplicates) · [Q11 — Remove Element In-Place](./practice.md#q11--remove-element-in-place)

> [↑ Back to Top](#top)

<a id="7-palindrome"></a>
# 7. Palindrome Checking

Dex checks if a word reads the same forwards and backwards. Left finger at the start, right finger at the end. Compare, move inward. If any mismatch — not a palindrome.

```
"racecar"
 L→         ←R
 r == r ✓ → move inward
   a == a ✓
     c == c ✓
       e (middle) → done! Palindrome ✓
```

Time: O(n). Space: O(1). Classic opposite-direction pattern.

**Common mistake — off-by-one in loop condition:** Use `while left < right`, not `while left <= right`. The `<=` version compares the middle character to itself — harmless here but signals a flawed invariant.

> 📝 **Practice:** [Q1 — Valid Palindrome](./practice.md#q1--valid-palindrome) · [Q18 — Valid Palindrome II](./practice.md#q18--valid-palindrome-ii) · [Q20 — Wrong Stop Condition Bug](./practice.md#q20--wrong-stop-condition)

> [↑ Back to Top](#top)

<a id="8-container-water"></a>
# 8. Container With Most Water

Dex faces a row of walls. He places his hands at the far ends and calculates the water they could hold. Then he moves the shorter wall inward — because moving the taller one can never help (the water is limited by the shorter side, and width only decreases).

**Input:** `[1, 8, 6, 2, 5, 4, 8, 3, 7]`

```
water = min(height[lo], height[hi]) × (hi - lo)
         ↑ limited by shorter wall    ↑ width
```

<a id="visual-container"></a>
## Visual: Container Step-by-Step

```
Step 1: lo=0, hi=8
  height[0]=1, height[8]=7
  water = min(1,7) * 8 = 8
  Move shorter (lo) → lo=1

Step 2: lo=1, hi=8
  height[1]=8, height[8]=7
  water = min(8,7) * 7 = 49  ← max!
  Move shorter (hi) → hi=7

Step 3: lo=1, hi=7
  height[1]=8, height[7]=3
  water = min(8,3) * 6 = 18
  Move shorter (hi) → hi=6

...continue until lo >= hi...

Maximum water = 49
```

**Key insight:** Always move the SHORTER wall's pointer. Moving the taller wall inward definitely cannot do better — you lose width AND the limiting factor stays the same.

> 📝 **Practice:** [Q9 — Container With Most Water](./practice.md#q9--container-with-most-water)

> [↑ Back to Top](#top)

<a id="9-partitioning"></a>
# 9. Partitioning Problems

Dex rearranges cards in-place: move all zeros to the end, or sort colors (Dutch National Flag). The pattern: slow pointer tracks the write position, fast pointer scans.

```
Move zeros: slow writes non-zeros, fast scans everything.
Time: O(n), Space: O(1)
```

**Common mistake — Dutch National Flag: advancing mid after swap with hi:** When `nums[mid] == 2`, swap with `hi` but do NOT advance `mid` — the swapped element is unclassified.

```
Invariant:
  nums[0 .. lo-1]   = all 0s
  nums[lo .. mid-1] = all 1s
  nums[mid .. hi]   = UNKNOWN
  nums[hi+1 .. n-1] = all 2s
```

> 📝 **Practice:** [Q4 — Move Zeros](./practice.md#q4--move-zeros) · [Q12 — Partition Around Value](./practice.md#q12--partition-around-value) · [Q13 — Sort Colors (Dutch Flag)](./practice.md#q13--sort-colors-dutch-flag)

> [↑ Back to Top](#top)

<a id="10-linked-list"></a>
# 10. Two Pointers in Linked List

Dex applies the same technique to linked lists — fast and slow pointers. Fast moves 2 steps, slow moves 1. This detects cycles (Floyd's), finds the middle, and removes the nth node from end.

<a id="visual-cycle"></a>
## Visual: Cycle Detection

```
Slow moves 1 step:  A → B → C → D
Fast moves 2 steps: A → C → E → B → D → ...

If there's a cycle, fast laps slow and they meet.
If no cycle, fast reaches null first.
```

**Common mistake — not checking `fast.next`:** Guard must check BOTH `fast` and `fast.next` before accessing `fast.next.next`.

```
while fast and fast.next:   ← check BOTH
    slow = slow.next
    fast = fast.next.next
```

> 📝 **Practice:** [Q6 — Cycle Detection](./practice.md#q6--cycle-detection) · [Q7 — Middle of Linked List](./practice.md#q7--middle-of-linked-list) · [Q17 — Cycle Entry Point](./practice.md#q17--cycle-entry-point) · [Q25 — Nth Node From End](./practice.md#q25--nth-node-from-end)

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

| Concept | Key Takeaway |
|---------|-------------|
| Two pointers | Movement strategy that eliminates nested loops |
| Opposite direction | Sorted array, converging inward — Two Sum, palindrome |
| Same direction | Reader/writer — remove duplicates, partition |
| Fast/slow | Cycle detection, find middle (linked list) |
| Container with water | Always move the shorter wall |
| Why it works | Sorted order lets you prove elimination is safe |

**Two Pointers vs Hashing:**
- Two pointers: requires sorted data, O(1) space, O(n) time
- Hashing: works on unsorted, O(n) space, O(n) time
- Choose based on: is data sorted? Can you afford extra space?

**Common mistakes checklist:**
- Moving wrong pointer (must decrease sum → move right, not left)
- Infinite loops (every iteration must advance at least one pointer)
- Forgetting sorted requirement
- Not handling duplicates (in 3Sum, skip duplicates after finding a match)
- Incorrect boundary (`< right` not `<= right` for palindrome)

**Performance:**
- Without two pointers: O(n²) nested loops
- With two pointers: O(n) single pass
- For n = 10⁵: O(n²) is impossible, O(n) is feasible

Two pointers prepares Dex for sliding window, greedy problems, binary search variations, and advanced optimization patterns.

> 📝 **Practice:** [Q8 — Why O(n) Beats O(n²)](./practice.md#q8--when-two-pointers-beats-brute-force) · [Q16 — Choosing Pointer Direction](./practice.md#q16--choosing-pointer-direction) · [Q19 — Two Pointers vs Hash Map](./practice.md#q19--two-pointers-vs-hashmap)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [10_hashing → theory.md](../10_hashing/theory.md) |
| ➡ Next Module | [12_sliding_window → theory.md](../12_sliding_window/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[10 Hashing →](../10_hashing/theory.md) · [12 Sliding Window →](../12_sliding_window/theory.md) · [06 Searching →](../06_searching/theory.md) · [07 Linked List →](../07_linked_list/theory.md)

**Jump to specific topics in other files:**
- Sliding window (extension of same-direction) → [12_sliding_window § theory.md](../12_sliding_window/theory.md)
- Binary search (another elimination technique) → [06_searching § theory.md](../06_searching/theory.md)
- Floyd's cycle detection → [07_linked_list § Detect Cycle](../07_linked_list/theory.md#detect-cycle)
- Dutch National Flag → [02_arrays § Dutch National Flag](../02_arrays/theory.md#dutch-national-flag)

> [↑ Back to Top](#top)
