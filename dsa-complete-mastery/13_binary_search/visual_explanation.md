# Binary Search: The Hot/Cold Game

---

## The Story Begins

You're playing a number guessing game with a friend.

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

That's **binary search**. Every step, half the possibilities are eliminated.

---

## Why O(log n): The Math That Will Blow Your Mind

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

---

## Step-by-Step: Finding 37

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

---

## The Three Templates: Which One to Use?

Binary search comes in three flavors. The difference is subtle but critical.

### Template 1: Find Exact Match

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1

    while lo <= hi:           # ← note: lo <= hi
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
    lo, hi = 0, len(arr)      # ← hi = len(arr), not len-1

    while lo < hi:            # ← note: lo < hi (strict)
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid          # ← hi = mid, not mid-1

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
        mid = (lo + hi + 1) // 2   # ← ceiling division to avoid infinite loop
        if arr[mid] <= target:
            lo = mid               # ← lo = mid
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

---

## Binary Search on the Answer (The Clever One)

This is where binary search goes from "find a value in an array" to "find a value that satisfies a condition."

### The Koko Eating Bananas Problem

**Story:** Koko has `n` piles of bananas. She has `h` hours before the guard returns. She can eat at speed `k` bananas per hour (finishing a pile in one hour if she eats the whole pile). What's the minimum speed `k` that lets her finish all piles in time?

**Input:** piles = `[3, 6, 7, 11]`, h = `8`
**Output:** minimum speed k

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

Binary search for the transition point:
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
  pile 3:  ceil(3/4)=1
  pile 6:  ceil(6/4)=2
  pile 7:  ceil(7/4)=2
  pile 11: ceil(11/4)=3
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

---

## Python's bisect Module: Binary Search Built In

Python has a built-in module for sorted arrays. Let's see how it works.

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

Count of 2s = bisect_right - bisect_left = 4 - 1 = 3 ✓
```

**Finding if a value exists:**

```python
import bisect

def exists(arr, target):
    i = bisect_left(arr, target)
    return i < len(arr) and arr[i] == target
```

**Finding the range of a value:**

```python
left  = bisect_left(arr, target)   # first occurrence
right = bisect_right(arr, target)  # one past last occurrence
count = right - left               # number of occurrences
```

---

## Common Pitfalls

**1. Infinite loop with Template 3:**

```
lo=4, hi=5, mid=(4+5)//2=4

if arr[mid] satisfies condition: lo = mid = 4
→ lo stays at 4 forever!

Fix: mid = (lo + hi + 1) // 2   ← ceiling, not floor
```

**2. Integer overflow (C++/Java, not Python):**

```
lo = 1,000,000,000
hi = 2,000,000,000
mid = (lo + hi) / 2  ← overflow in languages with fixed int size!

Fix: mid = lo + (hi - lo) / 2
Python doesn't have this problem (arbitrary precision ints).
```

**3. Off-by-one errors:**

```
Template 1: hi starts at len(arr)-1, loop is lo <= hi
Template 2: hi starts at len(arr),   loop is lo < hi

Mixing these up causes either missing the last element
or going out of bounds.
```

---

## Summary: The Decision Tree

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

---

## The One-Liner Mental Model

> Binary search works whenever you can look at the middle of a sorted space and say
> "the answer is definitely not in this half." Each step, you eliminate half the possibilities.
> 1 billion elements. 30 steps. That's the magic of O(log n).
