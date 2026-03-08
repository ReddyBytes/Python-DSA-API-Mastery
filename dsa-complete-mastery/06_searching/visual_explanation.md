# Searching Algorithms — Visual Explanation

---

## Chapter 1: The Lost Keys Problem (Linear Search)

Picture this. You come home, reach into your pocket — no keys. You start checking every
drawer in the house, one by one. Kitchen drawer... nope. Junk drawer... nope. Bedside
table drawer... THERE they are.

That is linear search. You check every single item until you find what you want (or run
out of places to look).

```
Array: [14, 3, 27, 9, 51, 6, 33]
Target: 33

Step 1: Check index 0 → 14 ≠ 33
Step 2: Check index 1 →  3 ≠ 33
Step 3: Check index 2 → 27 ≠ 33
Step 4: Check index 3 →  9 ≠ 33
Step 5: Check index 4 → 51 ≠ 33
Step 6: Check index 5 →  6 ≠ 33
Step 7: Check index 6 → 33 = 33  ✓ FOUND at index 6
```

**The harsh truth:** Whether you find your keys on step 1 or step 7, the worst case is
always going through everything. That is O(n).

Best case? O(1) — the first drawer you check. Lucky you.
Average case? O(n/2) — which we still just call O(n).

Linear search does not care whether the data is sorted or random. It just walks forward
until it finds the item or falls off the end.

```python
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
```

When should you use it? When the array is small, unsorted, or you only search once.
When should you NOT use it? When the array is large and sorted. That is where binary
search comes in.

---

## Chapter 2: The Phone Book Moment (Why Binary Search Needs Sorted Data)

You are looking up "Williams" in a phone book (yes, a physical phone book).

Do you start at page 1 and read every name? Of course not. You flip to the middle —
let's say you land on "Morrison." You know Williams comes after Morrison alphabetically,
so you throw away the entire first half of the book. You are now searching half the
remaining pages.

**That is binary search.** But here is the critical insight:

> Binary search only works because the phone book is SORTED.

If every phone book entry were in random order, opening to the middle tells you nothing.
"Morrison" could have been placed anywhere. You cannot throw away half the book because
the second half might contain entries starting with A through L.

```
SORTED book — middle gives useful information:
[A...] [B...] [C...] [MIDDLE → M] [...S] [...T] [...W] [...Z]
                           ↑
                    "Williams > M, so discard left half"

RANDOM book — middle tells you nothing:
[X...] [B...] [Z...] [MIDDLE → M] [...A] [...T] [...W] [...D]
                           ↑
                    "Williams > M, but Williams could be ANYWHERE"
```

This is the key mental model: **binary search is elimination.** Every comparison lets
you confidently throw away half the remaining candidates. Unsorted data never lets you
do that.

---

## Chapter 3: Binary Search Step by Step

Let's search for **37** in this sorted array:

```
Index: [0]  [1]  [2]  [3]  [4]  [5]  [6]  [7]  [8]  [9]
Value:   1    5   12   18   23   37   44   57   62   89
```

We start with `lo = 0`, `hi = 9`.

---

**Round 1:**

```
lo=0                          hi=9
 ↓                              ↓
  1    5   12   18   23   37   44   57   62   89
                    ↑
               mid = (0+9)//2 = 4
               arr[4] = 23

23 < 37, so target is in the RIGHT half.
Move lo = mid + 1 = 5
```

---

**Round 2:**

```
                         lo=5       hi=9
                          ↓          ↓
  1    5   12   18   23   37   44   57   62   89
                               ↑
                          mid = (5+9)//2 = 7
                          arr[7] = 57

57 > 37, so target is in the LEFT half.
Move hi = mid - 1 = 6
```

---

**Round 3:**

```
                         lo=5  hi=6
                          ↓     ↓
  1    5   12   18   23   37   44   57   62   89
                          ↑
                     mid = (5+6)//2 = 5
                     arr[5] = 37

37 == 37  ✓ FOUND at index 5
```

Three comparisons to search 10 elements. Linear search would have needed 6.
For an array of 1 billion elements, binary search needs at most 30 comparisons.

**Why do we check mid BEFORE moving?**

We check `arr[mid] == target` first so we do not miss it. If we moved pointers first,
we might skip right over the answer.

**What happens if lo > hi?**

The window has collapsed — we have exhausted all candidates without finding the target.
Return -1.

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

---

## Chapter 4: The Three Templates — Which One Do You Use?

Binary search has one of the most confusing sets of variations in all of DSA. People
argue about `<=` vs `<`, `mid+1` vs `mid`, `mid-1` vs `mid`. Let's demystify this.

### Template 1: `lo <= hi` — Exact Match Search

Use this when you want to find a specific value and return its index.

```
Invariant: target (if it exists) is in the range [lo, hi]

Loop exits when:  lo > hi  (window is empty — not found)
                  OR we return early when arr[mid] == target

 lo=0                    hi=9
  ├────────────────────────┤
  │ search space           │
  └────────────────────────┘

Each step either:
  - Returns the found index
  - Shrinks the window by setting lo = mid+1 or hi = mid-1
```

The `lo <= hi` condition means we still check when the window is a single element
(lo == hi). This is correct for exact match — that single element might be our answer.

---

### Template 2: `lo < hi` — Boundary Finding

Use this when you want to find the LEFTMOST or RIGHTMOST position (first occurrence,
insertion point, etc.).

```
Invariant: the answer is always inside [lo, hi]

Loop exits when:  lo == hi  (they converge ON the answer)

 lo=0                    hi=9
  ├────────────────────────┤
  At convergence: lo == hi == answer position
```

Key difference: when `arr[mid]` could be the answer, we set `hi = mid` (not `mid-1`)
because we don't want to exclude mid from consideration.

```python
# Find leftmost position where arr[i] >= target
def lower_bound(arr, target):
    lo, hi = 0, len(arr)           # hi = len(arr) — one past the end!
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid               # mid might be the answer, keep it
    return lo                      # lo == hi at this point
```

---

### Template 3: `lo < hi - 1` — Avoids Infinite Loop Trap

Use this when `mid` is assigned to `lo` (not `mid+1`). Without the `lo < hi - 1`
guard, you get an infinite loop.

```
The danger:
  lo=5, hi=6
  mid = (5+6)//2 = 5
  If we set lo = mid = 5... lo never advances!
  We are stuck forever.

The fix:
  Loop condition: lo < hi - 1
  This ensures at least 2 elements remain, so mid is always BETWEEN lo and hi.

 lo   mid   hi
  ├────┼─────┤
  This gap guarantees mid != lo when using integer division
```

When the loop exits with `lo < hi - 1` as the condition, you have `hi = lo + 1`. You
then manually check both `arr[lo]` and `arr[hi]` after the loop.

---

## Chapter 5: The Off-by-One Errors, Visualized

This trips up nearly everyone. Here is the rule in plain English:

### When to use `lo = mid + 1`

When you are CERTAIN the answer is NOT at mid (you have already checked it and it is
too small).

```
arr[mid] < target:
  mid is definitely not the answer
  Everything ≤ mid is too small
  Safe to move lo PAST mid

  ... [mid] [mid+1] ...
         ✗    ← lo starts here
```

### When to use `lo = mid`

When mid COULD be the answer. You do not want to skip it.

```
arr[mid] could still satisfy the condition:
  Do NOT discard mid
  Move lo TO mid (but only safe if loop is lo < hi - 1)

  ... [mid] [mid+1] ...
       ↑
    lo stays here
```

### When to use `hi = mid - 1`

When arr[mid] is too large AND you are doing exact match search.

```
arr[mid] > target:
  mid is definitely not the answer
  Everything ≥ mid is too large

  ... [mid-1] [mid] ...
          ↑     ✗
       hi goes here
```

### When to use `hi = mid`

When doing boundary finding and mid might be the answer.

```
arr[mid] >= target:
  mid satisfies the condition but there might be an earlier one
  Keep mid in the search space

  ... [mid-1] [mid] ...
               ↑
            hi stays here
```

---

## Chapter 6: Search on Answer — The Guessing Game

Here is where binary search becomes a superpower. Most people learn it for finding
positions in arrays. But the real magic is searching for the ANSWER ITSELF.

### The Koko Eating Bananas Problem

Koko has piles of bananas: `[3, 6, 7, 11]`. She has 8 hours to eat them all. What is
the minimum speed (bananas/hour) she can eat at and still finish in time?

At speed `k`, pile of size `p` takes `ceil(p/k)` hours.

**The naive approach:** Try every possible speed from 1 upward. O(max_pile * n).

**The smart approach:** The answer (speed) has a range. Minimum possible: 1. Maximum
possible: max(piles) = 11. And here is the key insight:

> If speed k works, then speed k+1 also works. The "works" condition is monotone.

```
Speed:   1    2    3    4    5    6    7    8    9   10   11
Works?:  ✗    ✗    ✗    ✗    ✗    ✗    ✗    ✓    ✓    ✓    ✓
                                             ↑
                                      first valid speed
```

This is a sorted yes/no array! We can binary search for the FIRST "yes."

```
lo=1, hi=11

Round 1: mid=6
  Speed 6: [3,6,7,11] → ceil(3/6)+ceil(6/6)+ceil(7/6)+ceil(11/6) = 1+1+2+2 = 6 hours ≤ 8 ✓
  Works! But maybe a slower speed also works. hi = mid = 6

Round 2: lo=1, hi=6, mid=3
  Speed 3: 1+2+3+4 = 10 hours > 8 ✗
  Too slow. lo = mid + 1 = 4

Round 3: lo=4, hi=6, mid=5
  Speed 5: 1+2+2+3 = 8 hours ≤ 8 ✓
  Works! hi = mid = 5

Round 4: lo=4, hi=5, mid=4
  Speed 4: 1+2+2+3 = 8 hours ≤ 8 ✓
  Works! hi = mid = 4

lo == hi == 4. Answer: speed 4.
```

We searched on the SPEED, not on a position in the array. This is the "search on
answer" pattern.

**The template for "search on answer":**

```
1. Identify the range [lo, hi] for the answer
2. Write a function: can_solve(k) → True/False
3. Make sure the True/False values are monotone (all False then all True, or vice versa)
4. Binary search for the boundary
```

---

## Quick Reference

```
+------------------+------------------+------------------+
| Template         | Condition        | Loop exits when  |
+------------------+------------------+------------------+
| Exact match      | lo <= hi         | lo > hi or found |
| Leftmost bound   | lo < hi          | lo == hi         |
| Avoid inf loop   | lo < hi - 1      | hi == lo + 1     |
+------------------+------------------+------------------+

+------------------+------------------+
| Situation        | Pointer move     |
+------------------+------------------+
| arr[mid] < tgt   | lo = mid + 1     |
| arr[mid] > tgt   | hi = mid - 1     |
| mid might be ans | hi = mid         |
| mid can't be ans | lo = mid + 1     |
+------------------+------------------+

Time:  O(log n)
Space: O(1)
```

---

*Next up: Linked Lists — where nodes play a treasure hunt.*
