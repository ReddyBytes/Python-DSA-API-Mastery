# Two Pointers: Two Fingers, One Brain

---

## The Story Begins

You're at a bookshelf looking for two books whose combined thickness equals exactly 10cm.

**Approach 1 (Brute Force):** Pick up book 1, measure it against every other book. Then book 2 against every other. Then book 3...

If there are 100 books, you make roughly 5,000 comparisons. That's O(n²).

**Approach 2 (Two Pointers):** Sort the books by thickness. Put your left finger at the thinnest book, right finger at the thickest. Check the pair. Too thick? Move the right finger left. Too thin? Move the left finger right.

You'll find the answer in at most 100 moves. That's O(n).

Same problem. Two fingers. 50x fewer comparisons.

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

---

## Pattern 1: Opposite Ends — Converging Inward

This works on **sorted** arrays. One pointer starts at the left, one at the right. They walk toward each other.

### Two Sum (Sorted Array Version)

**Input:** `[1, 3, 5, 7, 9]`, target = `8`
**Find:** two indices whose values sum to 8.

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

When sum is too big, we need a smaller value. The only way to get smaller is to move the right pointer left (decrease the larger number). We can't move left pointer right — that would make things even bigger.

When sum is too small, we need a bigger value. Move the left pointer right.

```
sum > target  →  move hi left   (decrease the big number)
sum < target  →  move lo right  (increase the small number)
sum = target  →  found!
lo >= hi      →  no solution
```

```
Converging inward:

[ 1,  3,  5,  7,  9 ]
  L→               ←R     sum=10, too big
  L→         ←R           sum=8,  found!

If not found, pointers would cross and we'd exit.
```

---

## Pattern 2: Same Direction — Fast and Slow

Both pointers start at the left but move at different speeds or for different purposes.
Think of it as: one pointer **reads**, one pointer **writes**.

### Remove Duplicates from Sorted Array (In-Place)

**Input:** `[1, 1, 2, 3, 3, 4]`
**Goal:** Remove duplicates in-place, return the count of unique elements.

We can't create a new array. We overwrite the input.

Two pointers:
- `slow` = the write position (where to put the next unique element)
- `fast` = the reader (scanning through every element)

```
Initial:
[ 1,  1,  2,  3,  3,  4 ]
  ↑
  slow=0, fast=0
```

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
[ 1,  2,  3,  3,  3,  4 ]
              SF         (both near the 3s)

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

Final array: [ 1,  2,  3,  4,  3,  4 ]
                               ↑
                         slow=4 (return this as count)
```

The first 4 elements `[1, 2, 3, 4]` are the answer. The stuff after slow doesn't matter.

```
Before: [ 1,  1,  2,  3,  3,  4 ]
After:  [ 1,  2,  3,  4,  _,  _ ]  ← first 4 elements are unique
                          ^ slow
```

---

## Pattern 3: Cycle Detection (A Quick Mention)

Fast and slow pointers work brilliantly for linked list cycles too.

```
Slow moves 1 step:  A → B → C → D
Fast moves 2 steps: A → C → E → B → D → ...

If there's a cycle, fast laps slow and they meet.
If no cycle, fast reaches null first.
```

That's the Floyd's algorithm. We cover it in depth in the linked list section.

---

## 3Sum: Two Pointers + An Outer Loop

**Input:** `[-4, -1, -1, 0, 1, 2]`, find all triplets that sum to 0.

**Strategy:** Sort the array. For each element, use two pointers on the rest.

```
Sorted: [ -4, -1, -1,  0,  1,  2 ]
           i
           │
           Fix this, then two-pointer on the rest:
           [ -1, -1,  0,  1,  2 ]
              lo              hi
```

**Outer iteration i=0 (fixing -4):**

```
[ -4, -1, -1,  0,  1,  2 ]
   i   lo                hi

Need: lo + hi = -(-4) = 4
-1 + 2 = 1 ≠ 4, too small → move lo right

[ -4, -1, -1,  0,  1,  2 ]
   i       lo          hi

-1 + 2 = 1 ≠ 4, still too small → move lo right

[ -4, -1, -1,  0,  1,  2 ]
   i            lo      hi

0 + 2 = 2 ≠ 4, still too small → move lo right

[ -4, -1, -1,  0,  1,  2 ]
   i                lo  hi

1 + 2 = 3 ≠ 4, lo and hi adjacent → no triplet with -4
```

**Outer iteration i=1 (fixing -1):**

```
[ -4, -1, -1,  0,  1,  2 ]
        i   lo          hi

Need: lo + hi = -(-1) = 1
-1 + 2 = 1 ✓ → Found triplet! [-1, -1, 2]

Move both: lo right, hi left.

[ -4, -1, -1,  0,  1,  2 ]
        i       lo      hi

Wait: lo ≥ hi? No. Continue.
0 + 1 = 1 ✓ → Found triplet! [-1, 0, 1]

Move both again: lo right, hi left.
lo=4, hi=4: lo ≥ hi → stop.
```

**Duplicate skipping:** If you see the same value as previous, skip to avoid duplicate triplets.

```
i=1 and i=2 both have value -1.
After processing i=1, skip i=2.

if i > 0 and nums[i] == nums[i-1]:
    continue
```

---

## Container With Most Water

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

**Key insight:** Always move the SHORTER wall's pointer.
Why? The water is limited by the shorter wall. If we move the taller wall inward, we definitely can't do better (we lose width AND the limiting factor doesn't change). Moving the shorter wall is our only chance to find a taller partner.

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

---

## Cheat Sheet: Which Pattern?

```
┌─────────────────────────────────────────────────────────────┐
│                   TWO POINTER PATTERNS                       │
├──────────────────┬──────────────────────────────────────────┤
│ Opposite ends    │ Array is sorted, looking for pair/combo   │
│  L ────→ ←──── R│ Two Sum, Container with Water, 3Sum       │
├──────────────────┼──────────────────────────────────────────┤
│ Same direction   │ One pointer reads, one writes             │
│  S──→              │ Remove duplicates, partition, filter     │
│  F──────→        │                                           │
├──────────────────┼──────────────────────────────────────────┤
│ Fast/Slow        │ Detecting cycles, finding middle          │
│  S─→             │ Linked list cycle, Floyd's algorithm       │
│  F──→            │                                           │
└──────────────────┴──────────────────────────────────────────┘
```

**The golden rule:** You need to be able to answer "why is it safe to discard this element?" If you can answer that, two pointers will work.

---

## The One-Liner Mental Model

> Two pointers work because at each step, you can logically eliminate part of the search space.
> You're not guessing — you're using the sorted order (or structure) to prove certain options
> can't be the answer.
