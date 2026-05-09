<a id="top"></a>

# 📘 Sorting in Python — Deep Conceptual Theory

> Sorting is not about rearranging numbers.
> It is about controlling order to unlock efficiency.
> Many powerful algorithms assume sorted input.
> Understanding sorting deeply improves your optimization skills.

## 📖 Table of Contents

1. [What Problem Does Sorting Actually Solve?](#what-problem-does-sorting-actually-solve)
2. [Two Core Ways Sorting Algorithms Work](#two-core-ways-sorting-algorithms-work)
3. [Bubble Sort — Adjacent Correction Strategy](#bubble-sort--adjacent-correction-strategy)
4. [Selection Sort — Minimum Placement Strategy](#selection-sort--minimum-placement-strategy)
5. [Insertion Sort — Build Sorted Portion](#insertion-sort--build-sorted-portion)
6. [Merge Sort — Divide and Conquer Strategy](#merge-sort--divide-and-conquer-strategy)
7. [Quick Sort — Partition Strategy](#quick-sort--partition-strategy)
8. [Heap Sort — Structure-Based Sorting](#heap-sort--structure-based-sorting)
9. [Why O(n log n) Is the Speed Limit](#why-on-log-n-is-the-speed-limit)
10. [Stability Explained Clearly](#stability-explained-clearly)
11. [Python's Built-in Sort — Timsort](#pythons-built-in-sort--timsort)
12. [Comparison vs Non-Comparison Sorting](#comparison-vs-non-comparison-sorting)
13. [Choosing Sorting Algorithm — Practical Thinking](#choosing-sorting-algorithm--practical-thinking)
14. [Final Perspective](#final-perspective)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
merge sort · quick sort · heap sort · stability definition · O(n log n) lower bound

**Should Learn** — Important for real projects, comes up regularly:
Timsort (Python default) · counting sort · radix sort · when to use which

**Good to Know** — Useful in specific situations, not always tested:
insertion sort for nearly-sorted data · sorting stability trade-offs

**Reference** — Know it exists, look up syntax when needed:
shell sort · introsort · bucket sort

<a id="what-problem-does-sorting-actually-solve"></a>

# 1. What Problem Does Sorting Actually Solve?

Before we sort anything, let us ask why we even bother.

Unsorted data forces you to scan everything.

Sorted data allows:

- Binary search → O(log n)
- Two pointers → O(n)
- Easy duplicate detection (duplicates are adjacent)
- Range queries
- Efficient merging
- Database queries depend on sorted indexes

Sorting is often a transformation step — it reshapes the problem space.
Sorting is the foundation that makes everything else fast.

> [↑ Back to Top](#top)

<a id="two-core-ways-sorting-algorithms-work"></a>

# 2. Two Core Ways Sorting Algorithms Work

Every sorting algorithm follows one of these strategies:

## Strategy A — Repeated Comparison & Swap

Gradually push elements to correct positions.

Examples:
- Bubble
- Selection
- Insertion

## Strategy B — Divide, Reorganize, Rebuild

Break problem into smaller parts, then combine.

Examples:
- Merge sort
- Quick sort
- Heap sort

Understanding the strategy helps remember behavior.

> [↑ Back to Top](#top)

<a id="bubble-sort--adjacent-correction-strategy"></a>

# 3. Bubble Sort — Adjacent Correction Strategy

Imagine a tank of water with bubbles of different sizes.
When you shake it, the heaviest bubble slowly works its way to the top.
Each pass, the largest unsorted element "bubbles up" to its final position.

## Core Idea

Compare neighboring elements.
Swap if they are in wrong order.
Repeat until no swaps needed.

## Visual: One Full Pass on [5, 3, 1, 4, 2]

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

Each pass pushes one maximum to its correct position.

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

## Complexity

Worst Case: O(n²)

Best Case (already sorted with optimization): O(n)

With the early-exit optimization, it is O(n) on an already-sorted array.

## When Useful?

- Very small arrays
- Educational understanding

Rarely used in real systems.

**Common mistake — using bubble sort in production:** It is the learning algorithm. In production, always use Python's built-in `sorted()` or `.sort()` which runs Timsort at O(n log n).

> [↑ Back to Top](#top)

<a id="selection-sort--minimum-placement-strategy"></a>

# 4. Selection Sort — Minimum Placement Strategy

You are organizing a group photo. You want people sorted shortest to tallest.
Your strategy: scan the entire line, find the shortest person, bring them to the front.
Then scan the remaining people, find the shortest of those, bring them to position 2.
And so on.

## Core Idea

1. Find smallest element.
2. Swap it to front.
3. Repeat for remaining array.

## Visual: [5, 3, 1, 4, 2]

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

## Important Observation

Number of swaps = n (at most)

Time complexity: O(n²) always — it always does the full scan regardless of input.

Comparison with bubble sort: Selection makes fewer swaps (at most n swaps total). Bubble sort can make O(n²) swaps. If swapping is expensive, selection sort is better.

> [↑ Back to Top](#top)

<a id="insertion-sort--build-sorted-portion"></a>

# 5. Insertion Sort — Build Sorted Portion

You are playing cards. As each new card is dealt, you pick it up and slot it into
the correct position among the cards already in your hand.
Your hand is always sorted. You just keep inserting one card at a time.

## Core Idea

Divide array into:

- Sorted left portion
- Unsorted right portion

Insert each element from right into correct position in left.

## Visual: [5, 3, 1, 4, 2]

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
[3, 5 | 1, 4, 2]

Take 1. Compare with 5: shift. Compare with 3: shift.
[1, 3, 5 | 4, 2]

Take 4. Compare with 5: 4 < 5, shift. Compare with 3: 4 > 3, stop.
[1, 3, 4, 5 | 2]

Take 2. Shift 5, 4, 3 right. 2 > 1, stop.
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

## Why It Is Powerful

If array is nearly sorted: few shifts required.

Best Case: O(n)

Worst Case: O(n²)

**Online algorithm:** Can sort data as it arrives, without seeing the full list first.

Used in hybrid algorithms like Timsort.

> [↑ Back to Top](#top)

<a id="merge-sort--divide-and-conquer-strategy"></a>

# 6. Merge Sort — Divide and Conquer Strategy

You work at a casino. You have a shuffled deck of cards.
You split the deck in half, give each half to a dealer.
Each dealer splits their half again, and again, until each person holds just one card.
Then everyone starts merging: take two sorted piles, merge them into one sorted pile.
Repeat until you have one big sorted deck.

## Core Idea

1. Divide array into halves.
2. Recursively sort halves.
3. Merge sorted halves.

## Visual: The Split

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

## Visual: The Merge — Going Back Up

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

## Visual: ASCII Tree — Complete View

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

## Why It Is Efficient

At each level: you process all n elements once.

Number of levels: log n

Total: O(n log n) always — guaranteed.

## Trade-Off

Space: O(n) extra memory

Stable: Yes — equal elements maintain their original order.

Excellent for large datasets where stability matters.

> [↑ Back to Top](#top)

<a id="quick-sort--partition-strategy"></a>

# 7. Quick Sort — Partition Strategy

You are organizing a party seating chart.
You pick one person as the "pivot" (say, the host).
Everyone shorter than the host sits to the left.
Everyone taller sits to the right.
Now the host is in the right seat. Recursively do the same for the left and right groups.

## Core Idea

1. Choose pivot.
2. Rearrange so:
   - Smaller elements left
   - Larger elements right
3. Recursively sort partitions.

## Visual: Partition [5, 3, 1, 4, 2] with pivot = 4

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

## Why It Is Fast in Practice

- In-place
- Cache friendly
- Low constant factors

Best/Average: O(n log n) — pivot splits array roughly in half each time.

Worst: O(n²) — when pivot is always the smallest or largest element. This happens on already-sorted arrays with a bad pivot choice.

Space: O(log n) average (recursive call stack depth).

## Important Detail

Pivot selection matters:
- First element (bad for sorted arrays)
- Random pivot (better)
- Median-of-three (more stable)

Fix worst case: use random pivot or median-of-three.

**Common mistake — bad pivot choice on sorted input:** Using the first or last element as pivot on an already-sorted array degrades quicksort to O(n²). Always use a random pivot or median-of-three in production.

> [↑ Back to Top](#top)

<a id="heap-sort--structure-based-sorting"></a>

# 8. Heap Sort — Structure-Based Sorting

## Core Idea

Use heap (max heap):

1. Build heap from array.
2. Extract max repeatedly.
3. Place at end.

Heap property: Parent ≥ children.

## Complexity

Build heap: O(n)

Extraction: n times → O(log n) each

Total: O(n log n)

## Strength

- In-place
- No worst-case degradation like quicksort
- Guaranteed O(n log n) always

Weakness: Not stable.

> [↑ Back to Top](#top)

<a id="why-on-log-n-is-the-speed-limit"></a>

# 9. Why O(n log n) Is the Speed Limit

This is a beautiful insight. Forget code for a moment.

## The Information Theory Argument

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

> [↑ Back to Top](#top)

<a id="stability-explained-clearly"></a>

# 10. Stability Explained Clearly

Stable sort preserves order of equal elements.

## Visual: The Playing Card Story

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

## Why Stability Matters

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

Stability matters in multi-level sorting.

## Stability Summary

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

**Common mistake — assuming stability without checking:** Java's `Arrays.sort` for primitive types uses dual-pivot quicksort which is NOT stable. Python's sort is always stable. When porting Java sorting logic to Python, do not add unnecessary compound keys to simulate stability — Python's stability makes extra compound keys potentially change the intended order.

> [↑ Back to Top](#top)

<a id="pythons-built-in-sort--timsort"></a>

# 11. Python's Built-in Sort — Timsort

Python's built-in `sorted()` and `list.sort()` use **Timsort**, invented by Tim Peters in 2002.

Timsort is a hybrid of **merge sort and insertion sort**, engineered for real-world data.

## The Key Insight: Real Data Is Not Random

In the real world, data comes in partially sorted "runs."
A list of timestamps, a list of names that was recently modified,
a log file — these all have large stretches that are already sorted.

Random data is rare. Nearly-sorted data is common.

## How Timsort Works

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
it is extended using insertion sort — which is superfast on small arrays.

**Step 2: Merge runs using merge sort strategy**

```
Merge [1, 3, 5] + [2, 4, 7, 8] → [1, 2, 3, 4, 5, 7, 8]
Merge [1,2,3,4,5,7,8] + [6]    → [1, 2, 3, 4, 5, 6, 7, 8]
```

## Why Timsort Is Fast on Nearly-Sorted Data

If the array is already sorted, there is one run of length n.
No merging needed. Timsort detects this and runs in O(n) — just checking, no work.

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

## Galloping Mode — The Speed Boost

When merging two runs and one side is "winning" many consecutive comparisons,
Timsort switches to **binary search jumps** (galloping) to skip ahead faster.

If you are merging `[1,2,3,4,5,...]` and `[100,200,300,...]`,
instead of comparing 1 vs 100, 2 vs 100, 3 vs 100, ...
Timsort jumps: "is 1,2,4,8,16,32... of left still less than 100?"
Then binary searches for the exact crossover point.

This makes Timsort exceptional for lists that have "blocks" of already-ordered elements.

## Timsort: Key Facts

Time: O(n log n) worst case, O(n) best case (already sorted)

Stable: Yes

Always prefer built-in sort in production.

**Common mistake — `sorted()` vs `.sort()` confusion:** `sorted()` returns a **new list** and leaves the original unchanged. `.sort()` modifies the list **in-place** and returns `None`. Mixing these up produces subtle bugs:

```python
# WRONG: rebinds local name only — caller's list is unchanged
def sort_in_place_wrong(nums):
    nums = sorted(nums)

# CORRECT
def sort_in_place_correct(nums):
    nums.sort()

def get_sorted_correct(nums):
    return sorted(nums)   # original untouched; new sorted list returned
```

| Function      | Modifies original | Returns         |
|---------------|-------------------|-----------------|
| `list.sort()` | YES               | `None`          |
| `sorted()`    | NO                | new sorted list |

> [↑ Back to Top](#top)

<a id="comparison-vs-non-comparison-sorting"></a>

# 12. Comparison vs Non-Comparison Sorting

Comparison-based sorts have a proven lower bound of O(n log n). Non-comparison sorts can beat this bound by exploiting element values directly.

## Counting Sort — O(n + k)

**When to use:** Elements are integers in a known, small range [0, k].

```
Input:  [4, 2, 2, 8, 3, 3, 1]   range: 0-8 (k=8)

Count:  [0, 1, 2, 2, 1, 0, 0, 0, 1]
         0  1  2  3  4  5  6  7  8

Output: [1, 2, 2, 3, 3, 4, 8]
```

```python
def counting_sort(arr, max_val):
    count = [0] * (max_val + 1)
    for num in arr:
        count[num] += 1
    result = []
    for num, freq in enumerate(count):
        result.extend([num] * freq)
    return result
```

**Time:** O(n + k). **Space:** O(k).
**Limit:** Only works for non-negative integers. Impractical if k >> n.

## Radix Sort — O(d × n)

**When to use:** Integers with d digits (or strings of length d). Sorts digit by digit.

```
Input:  [329, 457, 657, 839, 436, 720, 355]

Pass 1 (ones digit):
  720, 355, 436, 457, 657, 329, 839

Pass 2 (tens digit):
  720, 329, 436, 839, 355, 457, 657

Pass 3 (hundreds digit):
  329, 355, 436, 457, 657, 720, 839  ← sorted!
```

**Key:** Each pass uses a stable sort (like counting sort).
**Time:** O(d × n). For 32-bit ints, d=10 → effectively O(n).

**Common mistake — sorting numeric strings lexicographically:** String comparison is character-by-character. `"10" < "2"` because `"1" < "2"`. When data is numeric strings, use `key=int` for correct ordering:

```python
# WRONG: lexicographic order
numbers = ["10", "1", "2", "20", "3"]
wrong = sorted(numbers)
print(wrong)   # ['1', '10', '2', '20', '3']  ← BUG

# CORRECT: numeric order
correct = sorted(numbers, key=int)
print(correct)  # ['1', '2', '3', '10', '20']
```

> [↑ Back to Top](#top)

<a id="choosing-sorting-algorithm--practical-thinking"></a>

# 13. Choosing Sorting Algorithm — Practical Thinking

Ask:

- Data size?
- Memory allowed?
- Stability needed?
- Nearly sorted?
- Worst-case guarantees required?

Engineering decision is contextual.

## Decision Table

```
┌───────────────────────────────────────────────────────────────────────────┐
│  Scenario                          │  Algorithm         │  Why             │
├────────────────────────────────────┼────────────────────┼──────────────────┤
│  General purpose                   │  Python sorted()   │  Timsort, stable │
│  Nearly sorted data                │  Insertion/Timsort │  O(n) best case  │
│  Integer keys, small range         │  Counting sort     │  O(n+k)          │
│  Fixed-length integers/strings     │  Radix sort        │  O(d×n)          │
│  Memory limited, in-place needed   │  Heap sort         │  O(1) extra space│
│  Average case matters most         │  Quick sort        │  Best cache perf │
│  Worst case must be O(n log n)     │  Merge/Heap sort   │  Guaranteed      │
│  Must preserve equal-element order │  Merge/Timsort     │  Stable          │
└───────────────────────────────────────────────────────────────────────────┘
```

## The Mental Model

Merge sort is the **safe, reliable** choice — guaranteed O(n log n) always,
but uses O(n) extra memory and has overhead from copying.

Quick sort is the **fast but risky** choice — blazing fast in practice,
minimal memory, but catastrophic on bad pivots. Always randomize the pivot.

Timsort is the **wise, pragmatic** choice — it has seen the real world and
knows that data is usually partially sorted. It adapts accordingly.

## Complete Complexity Reference

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

**Common mistake — custom comparator returning True/False:** Python 3 removed the `cmp=` argument. A comparator passed to `cmp_to_key` must return negative/0/positive, not True/False. `True == 1` means "a comes after b" and `False == 0` means "equal" — "before" is never signalled:

```python
from functools import cmp_to_key

# WRONG: returns True/False (1/0) — "before" never returned
def bad_comparator(a, b):
    return a > b

# CORRECT: returns -1/0/1
def good_comparator_desc(a, b):
    if a > b:   return -1
    elif a < b: return 1
    else:       return 0

# Simpler alternative when possible
result = sorted(nums, key=lambda x: -x)
```

**Common mistake — Largest Number: sorting integers directly:** For LeetCode 179, naive descending sort by value fails for `[3, 30]` — `[30, 3]` gives `"303"` but `"330"` is correct. The fix is a custom comparator on string concatenation:

```python
from functools import cmp_to_key

def largest_number(nums):
    def comparator(a, b):
        if str(a) + str(b) > str(b) + str(a): return -1
        elif str(a) + str(b) < str(b) + str(a): return 1
        else: return 0
    nums.sort(key=cmp_to_key(comparator))
    result = "".join(map(str, nums))
    return "0" if result[0] == "0" else result
```

**Common mistake — modifying a list while iterating over it:** Removing elements during index-based iteration shifts everything left, causing elements to be skipped or raising IndexError. Always collect results into a new list:

```python
# WRONG: index shifts corrupt traversal
def remove_duplicates_wrong(nums):
    nums.sort()
    for i in range(len(nums) - 1):
        if nums[i] == nums[i + 1]:
            nums.pop(i)   # shifts everything — skips elements

# CORRECT: build new list
def remove_duplicates_correct(nums):
    nums.sort()
    result = []
    for num in nums:
        if not result or result[-1] != num:
            result.append(num)
    return result

# CORRECT: use set
def remove_duplicates_set(nums):
    return sorted(set(nums))
```

> [↑ Back to Top](#top)

<a id="final-perspective"></a>

# 14. Final Perspective

Sorting is:

- Foundational to searching
- Required for optimization patterns
- Core to many system-level operations
- Not one-size-fits-all

Understanding internal strategy
is more important than memorizing complexity table.

Mastering sorting prepares you for:
- Binary search
- Two pointers
- Heaps
- Greedy algorithms
- Graph algorithms

Sorting is a gateway topic in DSA.

> [↑ Back to Top](#top)

**[🏠 Back to README](../README.md)**

**Prev:** [← Recursion — Interview Q&A](../04_recursion/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
