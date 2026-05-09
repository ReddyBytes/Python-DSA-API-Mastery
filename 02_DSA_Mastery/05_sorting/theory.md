<a id="top"></a>
# 📘 05 – Sorting in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Problem Does Sorting Solve?](#1-what-problem-does-sorting-solve)
- [2. Two Core Ways Sorting Algorithms Work](#2-two-core-ways)
  - [Strategy A — Repeated Comparison and Swap](#strategy-a)
  - [Strategy B — Divide, Reorganize, Rebuild](#strategy-b)
- [3. Bubble Sort — Adjacent Correction](#3-bubble-sort)
  - [Visual: One Full Pass](#visual-bubble-pass)
- [4. Selection Sort — Minimum Placement](#4-selection-sort)
  - [Visual: Selection Rounds](#visual-selection)
- [5. Insertion Sort — Build Sorted Portion](#5-insertion-sort)
  - [Visual: The Card Hand](#visual-insertion)
- [6. Merge Sort — Divide and Conquer](#6-merge-sort)
  - [Visual: The Split](#visual-merge-split)
  - [Visual: The Merge](#visual-merge-up)
  - [Visual: ASCII Tree — Complete View](#visual-merge-tree)
- [7. Quick Sort — Partition Strategy](#7-quick-sort)
  - [Visual: Partition](#visual-partition)
- [8. Heap Sort — Structure-Based Sorting](#8-heap-sort)
- [9. Why O(n log n) Is the Speed Limit](#9-speed-limit)
  - [The Information Theory Argument](#info-theory)
- [10. Stability Explained Clearly](#10-stability)
  - [Visual: The Playing Card Story](#visual-stability)
  - [Stability Summary Table](#stability-table)
- [11. Python's Built-in Sort — Timsort](#11-timsort)
  - [How Timsort Works](#how-timsort-works)
  - [Galloping Mode](#galloping-mode)
- [12. Comparison vs Non-Comparison Sorting](#12-non-comparison)
  - [Counting Sort](#counting-sort)
  - [Radix Sort](#radix-sort)
- [13. Choosing the Right Algorithm](#13-choosing)
  - [Decision Table](#decision-table)
  - [Complete Complexity Reference](#complexity-reference)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
merge sort · quick sort · heap sort · stability definition · O(n log n) lower bound

**Should Learn** — Important for real projects, comes up regularly:
Timsort (Python default) · counting sort · radix sort · when to use which

**Good to Know** — Useful in specific situations, not always tested:
insertion sort for nearly-sorted data · sorting stability trade-offs

**Reference** — Know it exists, look up syntax when needed:
shell sort · introsort · bucket sort

Leo is an apprentice at a sorting factory. His job: take a mess of items and arrange them in order. But the factory has many stations — each teaching a different strategy. Some stations are slow but simple. Others are fast but tricky. Today Leo will visit every station, learn how each one works, and understand when to use which. By the end, he will know that sorting is not about rearranging numbers — it is about controlling order to unlock efficiency.

<a id="1-what-problem-does-sorting-solve"></a>
# 1. What Problem Does Sorting Solve?

Leo's first lesson at the factory: "Why do we even bother sorting?" His mentor shows him two shelves. On the unsorted shelf, finding a specific item requires checking every single one. On the sorted shelf, Leo can jump straight to the right area — like opening a dictionary to the right letter.

Unsorted data forces you to scan everything. Sorted data allows:

- Binary search → O(log n)
- Two pointers → O(n)
- Easy duplicate detection (duplicates are adjacent)
- Range queries
- Efficient merging
- Database queries depend on sorted indexes

Sorting is often a transformation step — it reshapes the problem space. Sorting is the foundation that makes everything else fast.

> [↑ Back to Top](#top)

<a id="2-two-core-ways"></a>
# 2. Two Core Ways Sorting Algorithms Work

Leo learns that every sorting station in the factory follows one of two fundamental strategies — like two schools of martial arts. One relies on brute patience. The other relies on clever division.

<a id="strategy-a"></a>
## Strategy A — Repeated Comparison and Swap

Gradually push elements to correct positions. Simple, intuitive, but slow for large inputs.

Examples: Bubble, Selection, Insertion

<a id="strategy-b"></a>
## Strategy B — Divide, Reorganize, Rebuild

Break the problem into smaller parts, solve each, then combine. Faster, but more complex.

Examples: Merge sort, Quick sort, Heap sort

Understanding the strategy helps remember behavior.

> [↑ Back to Top](#top)

<a id="3-bubble-sort"></a>
# 3. Bubble Sort — Adjacent Correction

Leo arrives at the first station. Imagine a tank of water with bubbles of different sizes. When you shake it, the heaviest bubble slowly works its way to the top. Each pass, the largest unsorted element "bubbles up" to its final position.

## Core Idea

Compare neighboring elements. Swap if they are in wrong order. Repeat until no swaps needed.

<a id="visual-bubble-pass"></a>
## Visual: One Full Pass on [5, 3, 1, 4, 2]

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

After each pass, the sorted zone grows by one on the right. After n-1 passes, the entire array is sorted.

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

## Complexity

Worst Case: O(n²). Best Case (already sorted with optimization): O(n).

## When Useful?

- Very small arrays
- Educational understanding

Rarely used in real systems.

**Common mistake — using bubble sort in production:** It is the learning algorithm. In production, always use Python's built-in `sorted()` or `.sort()` which runs Timsort at O(n log n).

> [↑ Back to Top](#top)

<a id="4-selection-sort"></a>
# 4. Selection Sort — Minimum Placement

Leo moves to the next station. You are organizing a group photo. You want people sorted shortest to tallest. Your strategy: scan the entire line, find the shortest person, bring them to the front. Then scan the remaining people, find the shortest of those, bring them to position 2. And so on.

## Core Idea

1. Find smallest element.
2. Swap it to front.
3. Repeat for remaining array.

<a id="visual-selection"></a>
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

Number of swaps = n (at most). Time complexity: O(n²) always — it always does the full scan regardless of input.

Comparison with bubble sort: Selection makes fewer swaps (at most n swaps total). Bubble sort can make O(n²) swaps. If swapping is expensive, selection sort is better.

> [↑ Back to Top](#top)

<a id="5-insertion-sort"></a>
# 5. Insertion Sort — Build Sorted Portion

Leo picks up a deck of cards. As each new card is dealt, he picks it up and slots it into the correct position among the cards already in his hand. His hand is always sorted. He just keeps inserting one card at a time.

## Core Idea

Divide array into sorted left portion and unsorted right portion. Insert each element from right into correct position in left.

<a id="visual-insertion"></a>
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

If array is nearly sorted: few shifts required. Best Case: O(n). Worst Case: O(n²).

**Online algorithm:** Can sort data as it arrives, without seeing the full list first. Used in hybrid algorithms like Timsort.

> [↑ Back to Top](#top)

<a id="6-merge-sort"></a>
# 6. Merge Sort — Divide and Conquer

Leo enters the casino station. He has a shuffled deck of cards. He splits the deck in half, gives each half to a dealer. Each dealer splits their half again, and again, until each person holds just one card. Then everyone starts merging: take two sorted piles, merge them into one sorted pile. Repeat until you have one big sorted deck.

## Core Idea

1. Divide array into halves.
2. Recursively sort halves.
3. Merge sorted halves.

<a id="visual-merge-split"></a>
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

<a id="visual-merge-up"></a>
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

<a id="visual-merge-tree"></a>
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

At each level: you process all n elements once. Number of levels: log n. Total: O(n log n) always — guaranteed.

## Trade-Off

Space: O(n) extra memory. Stable: Yes — equal elements maintain their original order. Excellent for large datasets where stability matters.

> [↑ Back to Top](#top)

<a id="7-quick-sort"></a>
# 7. Quick Sort — Partition Strategy

Leo arrives at the party station. He is organizing a seating chart. He picks one person as the "pivot" (say, the host). Everyone shorter than the host sits to the left. Everyone taller sits to the right. Now the host is in the right seat. Recursively do the same for the left and right groups.

## Core Idea

1. Choose pivot.
2. Rearrange so smaller elements go left, larger go right.
3. Recursively sort partitions.

<a id="visual-partition"></a>
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
    pivot = arr[high]
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

Best/Average: O(n log n). Worst: O(n²) — when pivot is always smallest or largest.
Space: O(log n) average (recursive call stack depth).

## Important Detail

Pivot selection matters:
- First element (bad for sorted arrays)
- Random pivot (better)
- Median-of-three (more stable)

**Common mistake — bad pivot choice on sorted input:** Using the first or last element as pivot on an already-sorted array degrades quicksort to O(n²). Always use a random pivot or median-of-three in production.

> [↑ Back to Top](#top)

<a id="8-heap-sort"></a>
# 8. Heap Sort — Structure-Based Sorting

Leo reaches the structure station. Imagine a company hierarchy where the CEO (maximum value) is always at the top. To sort, Leo repeatedly removes the CEO, places them at the end of the sorted section, and promotes the next in line. That hierarchy is a **heap**.

## Core Idea

Use a max heap:
1. Build heap from array — O(n)
2. Extract max repeatedly — O(log n) each
3. Place at end

Heap property: Parent ≥ children.

## Complexity

Build heap: O(n). Extraction: n times × O(log n) each. Total: O(n log n).

## Strength

- In-place (no extra memory)
- No worst-case degradation like quicksort
- Guaranteed O(n log n) always

Weakness: Not stable.

> [↑ Back to Top](#top)

<a id="9-speed-limit"></a>
# 9. Why O(n log n) Is the Speed Limit

Leo asks his mentor: "Can any sorting algorithm be faster than O(n log n)?" The mentor smiles and explains using information theory — a beautiful proof that no comparison-based sort can ever beat this bound.

<a id="info-theory"></a>
## The Information Theory Argument

Imagine your sorting algorithm is having a conversation with the array. It can only ask one type of question: "Is element A greater than element B?" Each comparison gives you 1 bit of information: yes or no. After k comparisons, you know at most 2^k different things.

There are n! possible orderings of n elements. To uniquely identify which one you started with, you need:

```
2^k ≥ n!
k ≥ log₂(n!)
```

By Stirling's approximation:
```
log₂(n!) ≈ n log₂(n)
```

So any comparison-based sorting algorithm must make at least **Ω(n log n) comparisons**. No matter how clever you are, you cannot do better using only comparisons.

```
For n = 1000:
  n! ≈ 4 × 10^2567  (an astronomically large number of possible orderings)
  log₂(n!) ≈ 8,530 comparisons minimum

  Merge sort on 1000 elements: ~10,000 comparisons
  Very close to the theoretical minimum!
```

The algorithms that break O(n log n) — counting sort, radix sort, bucket sort — do so by using **more than just comparisons**. They exploit the actual values of elements.

> [↑ Back to Top](#top)

<a id="10-stability"></a>
# 10. Stability Explained Clearly

Leo encounters a subtle but critical concept. Two items can have the same "sort key" but be different items — like two 7s in a deck of cards. A **stable** sort preserves the original order of equal elements. An unstable sort may rearrange them unpredictably.

<a id="visual-stability"></a>
## Visual: The Playing Card Story

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

**Scenario:** Sorting employees first by name, then by department.

```
After sort by name:
Alice - Engineering
Bob   - Marketing
Carol - Engineering
Dave  - Marketing

After STABLE sort by department:
Alice - Engineering   ← original alpha order preserved
Carol - Engineering
Bob   - Marketing
Dave  - Marketing

After UNSTABLE sort by department:
Carol - Engineering   ← order within department: anyone's guess
Alice - Engineering
Dave  - Marketing
Bob   - Marketing
```

<a id="stability-table"></a>
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

**Common mistake — assuming stability without checking:** Java's `Arrays.sort` for primitive types uses dual-pivot quicksort which is NOT stable. Python's sort is always stable.

> [↑ Back to Top](#top)

<a id="11-timsort"></a>
# 11. Python's Built-in Sort — Timsort

Leo discovers that Python does not use any single algorithm he learned — it uses a hybrid called **Timsort**, invented by Tim Peters in 2002. Timsort watched real-world data for patterns and realized something profound: real data is almost never fully random.

Python's `sorted()` and `list.sort()` use Timsort — a hybrid of **merge sort and insertion sort**, engineered for real-world data.

## The Key Insight: Real Data Is Not Random

A list of timestamps, a list of names, a log file — these all have large stretches that are already sorted. Random data is rare. Nearly-sorted data is common.

<a id="how-timsort-works"></a>
## How Timsort Works

**Step 1: Find or create "runs"**

Scan the array for naturally sorted (or reverse-sorted) sequences.

```
[1, 3, 5, 2, 4, 7, 8, 6]

Run 1: [1, 3, 5]          ← already ascending
Run 2: [2, 4, 7, 8]       ← already ascending
Run 3: [6]                ← singleton
```

Reverse-sorted runs are reversed in-place (free O(n) win). If a run is shorter than `minrun` (typically 32-64 elements), it is extended using insertion sort.

**Step 2: Merge runs using merge sort strategy**

```
Merge [1, 3, 5] + [2, 4, 7, 8] → [1, 2, 3, 4, 5, 7, 8]
Merge [1,2,3,4,5,7,8] + [6]    → [1, 2, 3, 4, 5, 6, 7, 8]
```

## Why Timsort Is Fast on Nearly-Sorted Data

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

<a id="galloping-mode"></a>
## Galloping Mode — The Speed Boost

When merging two runs and one side is "winning" many consecutive comparisons, Timsort switches to **binary search jumps** (galloping) to skip ahead faster.

If you are merging `[1,2,3,4,5,...]` and `[100,200,300,...]`, instead of comparing 1 vs 100, 2 vs 100, 3 vs 100, ... Timsort jumps: "is 1,2,4,8,16,32... of left still less than 100?" Then binary searches for the exact crossover point.

## Timsort: Key Facts

Time: O(n log n) worst case, O(n) best case. Stable: Yes. Always prefer built-in sort in production.

**Common mistake — `sorted()` vs `.sort()` confusion:** `sorted()` returns a **new list** and leaves the original unchanged. `.sort()` modifies the list **in-place** and returns `None`.

```python
# WRONG: rebinds local name only — caller's list unchanged
def sort_in_place_wrong(nums):
    nums = sorted(nums)

# CORRECT
def sort_in_place_correct(nums):
    nums.sort()

def get_sorted_correct(nums):
    return sorted(nums)   # original untouched
```

| Function | Modifies original | Returns |
|---|---|---|
| `list.sort()` | YES | `None` |
| `sorted()` | NO | new sorted list |

> [↑ Back to Top](#top)

<a id="12-non-comparison"></a>
# 12. Comparison vs Non-Comparison Sorting

Leo learns that the O(n log n) speed limit only applies to sorts that compare elements. Some clever algorithms bypass comparisons entirely by exploiting the actual values — counting them or processing them digit by digit.

<a id="counting-sort"></a>
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

**Time:** O(n + k). **Space:** O(k). **Limit:** Only works for non-negative integers. Impractical if k >> n.

<a id="radix-sort"></a>
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

**Common mistake — sorting numeric strings lexicographically:**

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

<a id="13-choosing"></a>
# 13. Choosing the Right Algorithm

Leo's final lesson: there is no single best algorithm. Each has its domain. His mentor teaches him to ask five questions before choosing: Data size? Memory budget? Stability needed? Nearly sorted? Worst-case guarantees required?

<a id="decision-table"></a>
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

Merge sort is the **safe, reliable** choice — guaranteed O(n log n) always, but uses O(n) extra memory.

Quick sort is the **fast but risky** choice — blazing fast in practice, minimal memory, but catastrophic on bad pivots.

Timsort is the **wise, pragmatic** choice — it has seen the real world and knows that data is usually partially sorted.

<a id="complexity-reference"></a>
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

**Common mistake — custom comparator returning True/False:** Python 3's `cmp_to_key` must return negative/0/positive, not True/False.

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

**Common mistake — Largest Number problem:** For LeetCode 179, naive descending sort fails for `[3, 30]`. The fix is a custom comparator on string concatenation:

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

**Common mistake — modifying a list while iterating:**

```python
# WRONG: index shifts corrupt traversal
def remove_duplicates_wrong(nums):
    nums.sort()
    for i in range(len(nums) - 1):
        if nums[i] == nums[i + 1]:
            nums.pop(i)

# CORRECT: build new list
def remove_duplicates_correct(nums):
    nums.sort()
    result = []
    for num in nums:
        if not result or result[-1] != num:
            result.append(num)
    return result
```

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

Sorting is foundational to searching, optimization patterns, and system-level operations. It is not one-size-fits-all. Understanding internal strategy is more important than memorizing the complexity table.

| Concept | Key Takeaway |
|---------|-------------|
| Why sort? | Unlocks binary search, two pointers, duplicate detection |
| O(n²) sorts | Simple but slow — bubble, selection, insertion |
| Merge sort | Guaranteed O(n log n), stable, O(n) extra space |
| Quick sort | Fast in practice, O(n²) worst case, use random pivot |
| Heap sort | Guaranteed O(n log n), in-place, not stable |
| O(n log n) limit | Proven by information theory for comparison sorts |
| Non-comparison | Counting sort O(n+k), radix sort O(d×n) — bypass the limit |
| Stability | Preserves order of equal elements — matters for multi-key sorts |
| Timsort | Python's default — hybrid merge+insertion, O(n) on nearly-sorted |
| Production rule | Always use `sorted()` / `.sort()` unless you have a specific reason not to |

Mastering sorting prepares Leo for binary search, two pointers, heaps, greedy algorithms, and graph algorithms. Sorting is a gateway topic in DSA.

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [04_recursion → theory.md](../04_recursion/theory.md) |
| ➡ Next Module | [06_searching → theory.md](../06_searching/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[04 Recursion →](../04_recursion/theory.md) · [06 Searching →](../06_searching/theory.md) · [16 Heaps →](../16_heaps/theory.md) · [01 Complexity Analysis →](../01_complexity_analysis/theory.md)

**Jump to specific topics in other files:**
- Binary search (requires sorted input) → [06_searching § theory.md](../06_searching/theory.md)
- Heap data structure → [16_heaps § theory.md](../16_heaps/theory.md)
- Two pointers on sorted arrays → [11_two_pointers § theory.md](../11_two_pointers/theory.md)
- Quick sort partition = Dutch National Flag → [02_arrays § Dutch National Flag](../02_arrays/theory.md#dutch-national-flag)

> [↑ Back to Top](#top)
