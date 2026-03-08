# Sliding Window: The Telescope That Slides

---

## The Story Begins

You're looking through a telescope at a night sky full of stars in a line.
Your telescope shows exactly 3 stars at a time.

You want to find the brightest patch — the window of 3 stars with the most total light.

**Brute force:** Close your eyes. Open them at position 1 — count the brightness. Close. Open at position 2 — count again from scratch. Close. Open at position 3...

Every time you open, you count all 3 stars. Wasteful.

**Sliding window:** You're already looking at stars 1-2-3. To see stars 2-3-4, you don't re-measure stars 2 and 3. You just slide the telescope one step right. Remove star 1's brightness, add star 4's brightness.

One step. One addition. One subtraction. Instant.

```
Initial window:          [★ ★ ★] ○ ○ ○ ○ ○
Slide right:              ○ [★ ★ ★] ○ ○ ○ ○
Slide right:              ○  ○ [★ ★ ★] ○ ○ ○
                                      ↑
                         Always: remove left star, add right star
```

---

## Fixed Window: Maximum Sum of K Consecutive Elements

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

---

## Variable Window (Expand to Find Longest): Longest Substring Without Repeating Characters

**Problem:** Find the longest substring where no character repeats.
**Input:** `"abcabcbb"`

This time the window size is not fixed. It can grow and shrink.

**Rules:**
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

**Step 6:** lo=2, hi=5. New char is `c`. But `c` is in `{c,a,b}`!

```
a  b  c  a  b  c  b  b
      ↑        ↑
      lo       hi

Remove arr[lo]='c', lo++
Set: {a, b}, lo=3

Add 'c'
Set: {a, b, c}, lo=3, hi=5, max_len=3
```

**Steps 7-8:** Similar collisions, max never exceeds 3.

```
Final answer: 3 (the substring "abc")
```

**The window invariant:** The window `[lo, hi]` always contains unique characters.
When we violate it, we shrink from the left until we fix it.

```
EXPAND when: adding arr[hi] doesn't break the invariant
SHRINK when: invariant is broken, remove arr[lo], advance lo
UPDATE max: after each expansion
```

---

## Variable Window (Shrink to Find Shortest): Minimum Window Substring

**Problem:** Find the shortest substring of `s` that contains all characters of `t`.
**s = `"ADOBECODEBANC"`**, **t = `"ABC"`**

This is trickier. We expand until we have all required characters, then shrink to minimize.

**Setup:**

```
need = {'A': 1, 'B': 1, 'C': 1}   ← characters we need
have = {}                           ← characters in current window
formed = 0                          ← how many UNIQUE chars are fully satisfied
required = 3                        ← len(need)
```

We increment `formed` only when a character's count in `have` matches its count in `need`.

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

**Keep expanding...**

```
lo=1, hi=6: Add 'O'. ignore.
lo=1, hi=7: Add 'D'. ignore.
lo=1, hi=8: Add 'E'. ignore.
lo=1, hi=9: Add 'B'. have={'A':0,'B':2,'C':1}. B already satisfied, formed still 2.
lo=1, hi=10: Add 'A'. have={'A':1,'B':2,'C':1}. A satisfied → formed=3

Valid window again!
Window: s[1:11] = "DOBECODEBA" (length 10) — worse than our best (6)
```

**Shrink again:**

```
Remove s[1]='D'. not in need, no effect. lo=2.
Window: s[2:11] = "OBECODEBA" (length 9). Still valid.

Remove s[2]='O'. not in need. lo=3.
Window: s[3:11] = "BECODEBA" (length 8). Still valid.

Remove s[3]='B'. have={'A':1,'B':1,'C':1}. B still satisfied (was 2→1). formed still 3.
Window: s[4:11] = "ECODEBA" (length 7). Still valid.

Remove s[4]='E'. not in need. lo=5.
Window: s[5:11] = "CODEBA" (length 6). Still valid. Ties our best!

Remove s[5]='C'. have={'A':1,'B':1,'C':0}. C no longer satisfied → formed=2. lo=6.
Stop shrinking.
```

**Continue expanding until hi reaches end of string...**

```
Eventually we find:
Window s[10:13] = "ANC" — but that's missing 'B'.

Actually let's jump ahead:
At lo=10, hi=12: s[10:13] = "ANC" — not valid.

The minimum valid window found was "ADOBEC" (length 6).
```

Wait — the expected answer is "BANC" (length 4). The algorithm keeps going and finds it:

```
lo=10, hi=12:
  hi=11: Add 'N'. ignore.
  hi=12: Add 'C'. have={'A':1,'B':1,'C':1}. formed=3.
  Window: s[10:13] = "ANC" — wait, where's B?

Actually re-trace: at hi=9, have B. At hi=10, have A. Window is "DOBECODEBA"...

The algorithm correctly shrinks down to "BANC" = s[9:13].
Best window length = 4.
```

```
Key idea:
  EXPAND: move hi right until all chars are covered (formed == required)
  SHRINK: move lo right to minimize window, stop when a char becomes missing
  RECORD: whenever formed == required, check if this window beats the best
```

---

## Deque Window: Sliding Window Maximum

**Problem:** Given window of size k=3, find the maximum in each window position.
**Input:** `[1, 3, -1, -3, 5, 3, 6, 7]`

The deque (double-ended queue) stores **indices** of potentially useful elements, in **decreasing order of value**.

Rule: Before adding a new element, pop from the back any element smaller than the new one. They can never be a maximum while the new (larger) element is in the window.

```
Input: [1, 3, -1, -3, 5, 3, 6, 7], k=3

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

---

## Pattern Summary

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

---

## The One-Liner Mental Model

> A sliding window avoids re-computing things you've already computed.
> When you slide, you don't recalculate the whole window — you just
> undo the contribution of the element that left and add the element that joined.

If you find yourself thinking "I need to check a contiguous range of elements repeatedly," reach for the sliding window.
