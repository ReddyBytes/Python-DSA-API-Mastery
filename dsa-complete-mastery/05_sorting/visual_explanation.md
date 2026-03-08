# Sorting — A Visual Story

---

## Chapter 1: Why Sorting Matters

Before we sort anything, let us ask why we even bother.

- Binary search only works on sorted data.
- Finding duplicates is trivial if data is sorted (they are adjacent).
- Many algorithms need sorted input to be efficient.
- Database queries depend on sorted indexes.

Sorting is the foundation that makes everything else fast.
Now, let us meet the algorithms — from the naive to the brilliant.

---

## Chapter 2: Bubble Sort — The Heaviest Bubble Rises

Imagine a tank of water with bubbles of different sizes.
When you shake it, the heaviest bubble slowly works its way to the top.
Each pass, the largest unsorted element "bubbles up" to its final position.

### One Full Pass on [5, 3, 1, 4, 2]

Compare adjacent pairs. If the left is bigger than the right, swap them.

```
Start: [5, 3, 1, 4, 2]

Compare positions 0 and 1: 5 > 3 → SWAP
[3, 5, 1, 4, 2]
    ↑↑
Compare positions 1 and 2: 5 > 1 → SWAP
[3, 1, 5, 4, 2]
       ↑↑
Compare positions 2 and 3: 5 > 4 → SWAP
[3, 1, 4, 5, 2]
          ↑↑
Compare positions 3 and 4: 5 > 2 → SWAP
[3, 1, 4, 2, 5]
             ↑↑
End of pass 1: 5 is now in its correct position!

             [3, 1, 4, 2, | 5]
                           ↑ sorted zone growing from right
```

After each pass, the sorted zone grows by one on the right.
After n-1 passes, the entire array is sorted.

```
Pass 1: [3, 1, 4, 2, | 5]
Pass 2: [1, 3, 2, | 4, 5]
Pass 3: [1, 2, | 3, 4, 5]
Pass 4: [1, | 2, 3, 4, 5]

Done!
```

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:   # optimization: already sorted
            break
```

**Complexity:** O(n²) time, O(1) space.
**When to use:** Never, in production. It is the learning algorithm.
**Interesting:** With the early-exit optimization, it is O(n) on an already-sorted array.

---

## Chapter 3: Selection Sort — Shortest Person in Line

You are organizing a group photo. You want people sorted shortest to tallest.

Your strategy: scan the entire line, find the shortest person, bring them to the front.
Then scan the remaining people, find the shortest of those, bring them to position 2.
And so on.

```
[5, 3, 1, 4, 2]

Round 1: Find minimum in [5,3,1,4,2] → 1 (at index 2)
         Swap index 0 and index 2:
[1, 3, 5, 4, 2]
 ↑ placed

Round 2: Find minimum in [3,5,4,2] → 2 (at index 4)
         Swap index 1 and index 4:
[1, 2, 5, 4, 3]
    ↑ placed

Round 3: Find minimum in [5,4,3] → 3 (at index 4)
         Swap index 2 and index 4:
[1, 2, 3, 4, 5]
       ↑ placed

Round 4: Find minimum in [4,5] → 4 (already at index 3)
         No swap needed.
[1, 2, 3, 4, 5]
          ↑ placed

Done!
```

```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
```

**Complexity:** O(n²) always — it always does the full scan regardless of input.
**Comparison with Bubble Sort:** Selection makes fewer swaps (at most n swaps total).
Bubble sort can make O(n²) swaps. If swapping is expensive, selection sort is better.

---

## Chapter 4: Insertion Sort — The Card Hand

You are playing cards. As each new card is dealt, you pick it up and slot it into
the correct position among the cards already in your hand.

Your hand is always sorted. You just keep inserting one card at a time.

```
Dealt so far (hand = sorted): [  ]
Deal 5: Hand = [5]

Deal 3: 3 < 5 → slide 5 right, insert 3 before it
        Hand = [3, 5]

Deal 1: 1 < 3 → slide 3 and 5 right, insert 1 at start
        Hand = [1, 3, 5]

Deal 4: 4 > 3 but 4 < 5 → slide 5 right, insert 4 before it
        Hand = [1, 3, 4, 5]

Deal 2: 2 > 1 but 2 < 3 → slide 3,4,5 right, insert 2
        Hand = [1, 2, 3, 4, 5]
```

Visualized on the array `[5, 3, 1, 4, 2]`:

```
[5 | 3, 1, 4, 2]  ← sorted part | unsorted part
     ↑ next card to insert

Take 3. Compare with 5: 3 < 5, shift 5 right.
[_, 5 | 1, 4, 2]  → insert 3
[3, 5 | 1, 4, 2]

Take 1. Compare with 5: shift. Compare with 3: shift.
[_, _, 3, 5 | 4, 2] → insert 1
[1, 3, 5 | 4, 2]    Oops, let me re-draw:
[1, 3, 5 | 4, 2]

Take 4. Compare with 5: 4 < 5, shift. Compare with 3: 4 > 3, stop.
[1, 3, _, 5 | 2] → insert 4
[1, 3, 4, 5 | 2]

Take 2. Shift 5, 4, 3 right. 2 > 1, stop.
[1, _, 3, 4, 5] → insert 2
[1, 2, 3, 4, 5]
```

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]   # shift right
            j -= 1
        arr[j + 1] = key          # insert
```

**Complexity:** O(n²) worst case, O(n) best case (already sorted — no shifts needed).
**Superpower:** Extremely fast on nearly-sorted or small arrays. This is why TimSort uses it.
**Online algorithm:** Can sort data as it arrives, without seeing the full list first.

---

## Chapter 5: Merge Sort — Two Sorted Piles of Cards

You work at a casino. You have a shuffled deck of cards.
You split the deck in half, give each half to a dealer.
Each dealer splits their half again, and again, until each person holds just one card.

Then everyone starts merging: take two sorted piles, merge them into one sorted pile.
Repeat until you have one big sorted deck.

### The Split

```
[5, 3, 1, 4, 2]

          [5, 3, 1, 4, 2]
          /              \
      [5, 3, 1]        [4, 2]
      /       \         /   \
   [5, 3]    [1]      [4]   [2]
   /    \
 [5]   [3]
```

### The Merge — Going Back Up

```
[5] and [3] → merge into [3, 5]

   [5]  [3]
    ↓    ↓
Compare: 3 < 5 → take 3
         [3, _]
         5 remains → take 5
         [3, 5] ✓

[3, 5] and [1] → merge into [1, 3, 5]

   [3, 5]  [1]
Compare: 1 < 3 → take 1
         [1, _]
         [3, 5] remaining → take them all
         [1, 3, 5] ✓

[4] and [2] → merge into [2, 4]

   [4]  [2]
Compare: 2 < 4 → take 2
         [2, _]
         4 remains → take 4
         [2, 4] ✓

[1, 3, 5] and [2, 4] → merge into [1, 2, 3, 4, 5]

   [1, 3, 5]   [2, 4]
Compare 1 vs 2: take 1   → [1]
Compare 3 vs 2: take 2   → [1, 2]
Compare 3 vs 4: take 3   → [1, 2, 3]
Compare 5 vs 4: take 4   → [1, 2, 3, 4]
[5] remains:    take 5   → [1, 2, 3, 4, 5] ✓
```

### ASCII Tree — Complete View

```
                [5, 3, 1, 4, 2]
               /               \
          [5, 3, 1]           [4, 2]
          /       \           /    \
       [5, 3]    [1]        [4]   [2]
       /    \
     [5]   [3]

─── Merging back up ───

     [5]   [3]
       \  /
      [3, 5]
         |    + [1]
       [1, 3, 5]
                  [4]  [2]
                    \ /
                  [2, 4]

       [1, 3, 5]      [2, 4]
             \         /
           [1, 2, 3, 4, 5]
```

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

**Complexity:** O(n log n) always — guaranteed.
**Space:** O(n) — needs temporary arrays during merge.
**Stable:** Yes — equal elements maintain their original order.

---

## Chapter 6: Quick Sort — The Pivot Party

You are organizing a party seating chart.
You pick one person as the "pivot" (say, the host).
Everyone shorter than the host sits to the left.
Everyone taller sits to the right.

Now the host is in the right seat. Recursively do the same for the left and right groups.

### Partition [5, 3, 1, 4, 2] with pivot = 4

```
Initial: [5, 3, 1, 4, 2],  pivot = arr[3] = 4

We want: [everything < 4] [4] [everything > 4]

Lomuto partition scheme:
  i = -1 (last index of "small" zone)
  pivot = 4

  j=0: arr[0]=5 > 4 → skip
  j=1: arr[1]=3 < 4 → i++, swap(arr[0], arr[1])
       i=0
       [3, 5, 1, 4, 2]  ← 3 is now in "small" zone

  j=2: arr[2]=1 < 4 → i++, swap(arr[1], arr[2])
       i=1
       [3, 1, 5, 4, 2]  ← 1 is now in "small" zone

  j=3: arr[3]=4 = pivot → skip
  j=4: arr[4]=2 < 4 → i++, swap(arr[2], arr[4])
       i=2
       [3, 1, 2, 4, 5]  ← 2 is now in "small" zone

  End: swap pivot (index 3) with arr[i+1] = arr[3]
       Pivot is already at index 3, no swap needed.
       [3, 1, 2, | 4 | 5]
                   ↑
                 4 is in its final sorted position!
```

Now recursively sort `[3, 1, 2]` and `[5]`:

```
Sort [3, 1, 2], pivot = 2:
  [1 | 2 | 3]

Sort [5]: already sorted.

Final: [1, 2, 3, 4, 5] ✓
```

```python
def quick_sort(arr, low, high):
    if low < high:
        pivot_idx = partition(arr, low, high)
        quick_sort(arr, low, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, high)

def partition(arr, low, high):
    pivot = arr[high]   # choose last element as pivot
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
```

**Best/Average Complexity:** O(n log n) — pivot splits array roughly in half each time.
**Worst Case:** O(n²) — when pivot is always the smallest or largest element.
This happens on already-sorted arrays with a bad pivot choice.
Fix: use random pivot or median-of-three.

**Space:** O(log n) average (recursive call stack depth).
**In-place:** Yes — no extra array needed (unlike merge sort).

---

## Chapter 7: Why O(n log n) is the Speed Limit

This is a beautiful insight. Forget code for a moment.

### The Information Theory Argument

Imagine your sorting algorithm is having a conversation with the array.
It can only ask one type of question: "Is element A greater than element B?"

Each comparison gives you 1 bit of information: yes or no.
After k comparisons, you know at most 2^k different things.

There are n! possible orderings of n elements.
To uniquely identify which one you started with, you need:

```
2^k ≥ n!
k ≥ log₂(n!)
```

By Stirling's approximation:
```
log₂(n!) ≈ n log₂(n)
```

So any comparison-based sorting algorithm must make at least **Ω(n log n) comparisons**.
No matter how clever you are, you cannot do better using only comparisons.

```
For n = 1000:
  n! ≈ 4 × 10^2567  (an astronomically large number of possible orderings)
  log₂(n!) ≈ 8,530 comparisons minimum

  Merge sort on 1000 elements: ~10,000 comparisons
  Very close to the theoretical minimum!
```

The algorithms that break O(n log n) — counting sort, radix sort, bucket sort —
do so by using **more than just comparisons**. They exploit the actual values of elements.

---

## Chapter 8: Stability — The Playing Card Story

Suppose you have a hand of playing cards, some with the same number but different suits:

```
Original order: [7♥, 3♦, 7♠, 5♣, 3♥]
                  0   1   2   3   4
```

You sort by number only. What happens to the two 7s and the two 3s?

**Stable sort:** Equal elements preserve their original relative order.

```
Stable result:   [3♦, 3♥, 5♣, 7♥, 7♠]
                   ↑   ↑        ↑   ↑
                3♦ came before 3♥ originally → preserved
                7♥ came before 7♠ originally → preserved
```

**Unstable sort:** Equal elements may be reordered.

```
Unstable result: [3♥, 3♦, 5♣, 7♠, 7♥]  ← order of equals flipped
```

### Why Stability Matters

**Scenario:** You are sorting a list of employees first by department, then by name.

Step 1: Sort by name (alphabetical).
Step 2: Sort by department.

If Step 2 is stable, employees within the same department remain alphabetically ordered.
If Step 2 is unstable, the alphabetical ordering from Step 1 is destroyed.

```
After step 1 (sort by name):
Alice - Engineering
Bob   - Marketing
Carol - Engineering
Dave  - Marketing

After step 2 with STABLE sort (sort by department):
Alice - Engineering   ← Alice before Carol (original alpha order preserved)
Carol - Engineering
Bob   - Marketing     ← Bob before Dave (original alpha order preserved)
Dave  - Marketing

After step 2 with UNSTABLE sort (sort by department):
Carol - Engineering   ← order within department: anyone's guess
Alice - Engineering
Dave  - Marketing
Bob   - Marketing
```

**Stability Summary:**

```
Algorithm        Stable?
────────────────────────
Bubble Sort      Yes     ← never swaps equal elements
Insertion Sort   Yes     ← only shifts, never swaps past equals
Merge Sort       Yes     ← takes left side first on ties
Quick Sort       No      ← pivot swaps can reorder equals
Selection Sort   No      ← swaps can pull elements across equals
Heap Sort        No      ← heap operations ignore order of equals
TimSort          Yes     ← designed to be stable
```

---

## Chapter 9: Python's TimSort — The Hybrid Champion

Python's built-in `sorted()` and `list.sort()` use **TimSort**, invented by Tim Peters in 2002.

TimSort is a hybrid of **merge sort and insertion sort**, engineered for real-world data.

### The Key Insight: Real Data is Not Random

In the real world, data comes in partially sorted "runs."
A list of timestamps, a list of names that was recently modified,
a log file — these all have large stretches that are already sorted.

Random data is rare. Nearly-sorted data is common.

### How TimSort Works

**Step 1: Find or create "runs"**

Scan the array for naturally sorted (or reverse-sorted) sequences.

```
[1, 3, 5, 2, 4, 7, 8, 6]

Run 1: [1, 3, 5]          ← already ascending
Run 2: [2, 4, 7, 8]       ← already ascending
Run 3: [6]                ← singleton
```

Reverse-sorted runs are reversed in-place (free O(n) win).

If a run is shorter than `minrun` (typically 32-64 elements),
it is extended using **insertion sort** — which is superfast on small arrays.

**Step 2: Merge runs using merge sort strategy**

```
Merge [1, 3, 5] + [2, 4, 7, 8] → [1, 2, 3, 4, 5, 7, 8]
Merge [1,2,3,4,5,7,8] + [6]    → [1, 2, 3, 4, 5, 6, 7, 8]
```

### Why TimSort is Fast on Nearly-Sorted Data

If the array is already sorted, there is one run of length n.
No merging needed. TimSort detects this and runs in O(n) — just checking, no work.

Insertion sort is extremely cache-friendly and fast on small inputs.
The merge step is only called when runs need to be combined.

```
Data shape               TimSort behavior
──────────────────────────────────────────────────────
Already sorted           O(n)   — detects one run
Reverse sorted           O(n)   — reverses in O(n), one merge
Random                   O(n log n) — full merge sort
Lots of equal elements   O(n)   — duplicate-detection optimizations
Real-world (mixed)       O(n log n) but with very small constants
──────────────────────────────────────────────────────
```

### Galloping Mode — The Speed Boost

When merging two runs and one side is "winning" many consecutive comparisons,
TimSort switches to **binary search jumps** (galloping) to skip ahead faster.

If you are merging `[1,2,3,4,5,...]` and `[100,200,300,...]`,
instead of comparing 1 vs 100, 2 vs 100, 3 vs 100, ...
TimSort jumps: "is 1,2,4,8,16,32... of left still less than 100?"
Then binary searches for the exact crossover point.

This makes TimSort exceptional for lists that have "blocks" of already-ordered elements.

---

## Chapter 10: The Big Sorting Picture

```
Algorithm       Best      Average    Worst     Space   Stable
──────────────────────────────────────────────────────────────────
Bubble Sort     O(n)      O(n²)      O(n²)     O(1)    Yes
Selection Sort  O(n²)     O(n²)      O(n²)     O(1)    No
Insertion Sort  O(n)      O(n²)      O(n²)     O(1)    Yes
Merge Sort      O(n logn) O(n logn)  O(n logn) O(n)    Yes
Quick Sort      O(n logn) O(n logn)  O(n²)     O(logn) No
Heap Sort       O(n logn) O(n logn)  O(n logn) O(1)    No
TimSort         O(n)      O(n logn)  O(n logn) O(n)    Yes
──────────────────────────────────────────────────────────────────
```

### When to Use What

```
Use case                                    Algorithm
────────────────────────────────────────────────────────────────
General purpose in Python                   TimSort (sorted/list.sort)
Need guaranteed O(n log n), stable          Merge Sort
Need in-place, average O(n log n)           Quick Sort (random pivot)
Nearly sorted data                          Insertion Sort / TimSort
Small arrays (n < 20)                       Insertion Sort
Need stable, space is fine                  Merge Sort
Integer values in known range               Counting Sort → O(n+k)
Large integers or strings                   Radix Sort → O(nk)
────────────────────────────────────────────────────────────────
```

### The Mental Model

Merge sort is the **safe, reliable** choice — guaranteed O(n log n) always,
but uses O(n) extra memory and has overhead from copying.

Quick sort is the **fast but risky** choice — blazing fast in practice,
minimal memory, but catastrophic on bad pivots. Always randomize the pivot.

TimSort is the **wise, pragmatic** choice — it has seen the real world and
knows that data is usually partially sorted. It adapts accordingly.

---

*Next up: Searching — binary search, depth-first, breadth-first, and the art of not looking where you don't need to.*
