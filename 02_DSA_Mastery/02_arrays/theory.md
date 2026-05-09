<a id="top"></a>
# 📘 02 – Arrays in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is an Array?](#1-what-is-an-array)
  - [How Python Represents Arrays](#how-python-represents-arrays)
- [2. Memory Model — Why Arrays Are Fast](#2-memory-model)
  - [Why Indexing Is O(1)](#why-indexing-is-o1)
  - [Visual: Memory Layout](#visual-memory-layout)
- [3. Core Operations and Their Complexity](#3-core-operations)
- [4. Insert, Delete, and the Shifting Cost](#4-insert-delete)
  - [Visual: Middle Insert](#visual-middle-insert)
  - [Visual: Deletion](#visual-deletion)
  - [Modifying While Iterating](#modifying-while-iterating)
- [5. Dynamic Resizing](#5-dynamic-resizing)
  - [Static vs Dynamic Arrays](#static-vs-dynamic)
- [6. Multi-Dimensional Arrays](#6-multi-dimensional-arrays)
  - [Visual: 2D to 1D Memory](#visual-2d-to-1d)
  - [List Multiplication Trap](#list-multiplication-trap)
- [7. In-Place vs Out-of-Place](#7-in-place-vs-out-of-place)
  - [Shallow vs Deep Copy Trap](#shallow-vs-deep-copy)
- [8. Array Thinking Patterns](#8-array-thinking-patterns)
  - [Prefix Sum Arrays](#prefix-sum-arrays)
  - [Visual: Prefix Sum — The Scoreboard](#visual-prefix-sum)
  - [Kadane's Algorithm — Maximum Subarray](#kadanes-algorithm)
  - [Dutch National Flag — Three-Way Partition](#dutch-national-flag)
- [9. Real-World Impact](#9-real-world-impact)
  - [Cache Friendliness](#cache-friendliness)
  - [NumPy and Contiguous Memory](#numpy-contiguous-memory)
  - [Circular Buffers](#circular-buffers)
  - [Prefix Sum in Analytics](#prefix-sum-analytics)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
indexing and slicing · insertion and deletion complexity · dynamic array resizing

**Should Learn** — Important for real projects, comes up regularly:
prefix sum arrays · multi-dimensional arrays · in-place vs out-of-place

**Good to Know** — Useful in specific situations, not always tested:
cache locality and SIMD · circular arrays

**Reference** — Know it exists, look up syntax when needed:
difference arrays · array compression techniques

Anya just got her first job — organizing a warehouse. The warehouse has a long row of numbered shelves, each holding exactly one box. Shelf 0, shelf 1, shelf 2, all the way down the aisle. Her boss tells her: "If someone asks for item on shelf 47, you do not walk shelf by shelf. You just go straight to shelf 47. That is the power of knowing the address." That is exactly how arrays work — and today, Anya is going to learn why this simple structure is the foundation of every algorithm she will ever write.

<a id="1-what-is-an-array"></a>
# 1. What Is an Array?

Anya's warehouse has 10 shelves placed side by side in a straight line. Each shelf has a number painted on it (the index) and a place to store one box (the value). That straight-line arrangement — numbered, ordered, one next to another — is exactly what an array is.

An **array** is a collection of elements stored in order, one next to another, in memory.

Order matters. Position matters. Index matters.

That position-based access is what makes arrays powerful.

<a id="how-python-represents-arrays"></a>
## How Python Represents Arrays

In Python, Anya writes:

```python
arr = [10, 20, 30, 40]
```

Technically, this is a **list**, but conceptually it behaves like a dynamic array. Think of it as Anya's warehouse that can magically grow — when she runs out of shelves, the warehouse builds more.

Python list is:
- A dynamic array (grows automatically)
- Resizable (allocates extra memory for growth)
- Stores references to objects (each shelf holds an arrow pointing to the actual box)

It is not just a container — it is an intelligent resizing structure.

> 📝 **Practice:** [Q2 — Dynamic Array Resizing](./practice.md#q2--dynamic-resize--dynamic-array-resizing)

> [↑ Back to Top](#top)

<a id="2-memory-model"></a>
# 2. Memory Model — Why Arrays Are Fast

Anya learns that her warehouse shelves are not scattered randomly across the building. They are placed in a perfect line — shelf 0 at address 1000, shelf 1 at address 1004, shelf 2 at address 1008. Because every shelf is the same size and placed consecutively, she can calculate any shelf's location with one formula: `address = base + (index × size)`. No walking. No searching. Just math.

If you know:
- Starting address
- Index number

You can directly calculate the exact location.

```python
arr[2]   # O(1) — direct address jump, no searching
```

<a id="visual-memory-layout"></a>
## Visual: Memory Layout

Picture a parking lot designed by a very organized engineer. Every space is exactly the same size. Every space has a number painted on the ground: 0, 1, 2, 3 ... The spaces are in a straight row, no gaps.

```
Parking Lot Analogy — Fixed-size, numbered spaces in a row:

  Space:   [0]    [1]    [2]    [3]    [4]    [5]
        ┌──────┬──────┬──────┬──────┬──────┬──────┐
Value:  │  42  │  17  │  99  │   5  │  88  │  23  │
        └──────┴──────┴──────┴──────┴──────┴──────┘
           ↑
       base address

Address formula:  address(arr[i]) = base + i × element_size

Example — arr starts at address 1000, each int = 4 bytes:

  Index │ Address │ Value
  ──────┼─────────┼──────
  arr[0]│  1000   │  42
  arr[1]│  1004   │  17
  arr[2]│  1008   │  99
  arr[3]│  1012   │   5   ← arr[3] = 1000 + (3 × 4) = 1012
  arr[4]│  1016   │  88
  arr[5]│  1020   │  23

Finding arr[3]:

  ┌──────────────────────────────────────────┐
  │  base(1000) + index(3) × size(4) = 1012  │
  └──────────────────────────────────────────┘
         │
         ▼
  ┌──────┬──────┬──────┬──────┬──────┬──────┐
  │  42  │  17  │  99  │  5   │  88  │  23  │
  └──────┴──────┴──────┴──────┴──────┴──────┘
  1000   1004   1008   1012   1016   1020
                         ↑
                    go here → value = 5   ✓

No looping. No searching. One arithmetic op, one memory read.
Same speed whether array has 10 or 10,000,000 elements → O(1).
```

<a id="why-indexing-is-o1"></a>
## Why Indexing Is O(1)

Behind the scenes, every access is just:

```
address = base + (index × size)
```

This formula gives instant access. It does not matter if the array has 10 elements or 10 million. Access time remains constant. This is why arrays are heavily used in high-performance systems.

**Common mistake — off-by-one in slicing:**

Python's slice `arr[start:end]` is **exclusive** at `end` — the slicer stops just before it.

```python
arr = [10, 20, 30, 40, 50, 60, 70]

# WRONG — trying to get indices 1 through 4 inclusive
middle = arr[1:4]    # [20, 30, 40] — index 4 (value 50) NOT included!

# RIGHT — use j+1 as the end to include index j
middle = arr[1:5]    # [20, 30, 40, 50] — correct, indices 1,2,3,4
```

The golden rule:
```
arr[i : j+1]    → indices i through j inclusive
arr[i : i+k]    → exactly k elements starting at i
arr[-n:]         → last n elements (cleanest form)
```

> 📝 **Practice:** [Q3 — Insert vs Delete Complexity](./practice.md#q3--insert-delete-complexity--insert-vs-delete-complexity)

> [↑ Back to Top](#top)

<a id="3-core-operations"></a>
# 3. Core Operations and Their Complexity

Anya's boss gives her a chart of everything she can do with the warehouse shelves — and how long each task takes. Some operations are instant (grab a box from a known shelf). Others require moving every box in the warehouse (insert a new shelf in the middle).

| Operation | Complexity | What Actually Happens |
|------------|------------|------------------------|
| Access | O(1) | Direct address jump |
| Update | O(1) | Overwrite memory |
| Append | O(1) amortized | Usually place at end |
| Insert (middle) | O(n) | Shift elements right |
| Delete (middle) | O(n) | Shift elements left |
| Search | O(n) | Scan sequentially |

Understanding the "why" behind these is more important than memorizing the table.

**Common mistake — pop(0) is O(n), not O(1):**

Imagine a queue of 1000 people. The counter calls the person at the front. After they leave, ALL 999 remaining people must physically take one step forward. If you serve 1000 people that way, total work is 1000 + 999 + ... + 1 ≈ 500,000 moves. That is O(n²).

`list.pop(0)` does exactly this. Lists are backed by a contiguous array. Removing the first element requires shifting every other element one position left.

```python
# WRONG — O(n) each time, total O(n²)
queue = list(range(100_000))
while queue:
    queue.pop(0)

# RIGHT — use collections.deque, O(1) popleft
from collections import deque
queue = deque(range(100_000))
while queue:
    queue.popleft()
```

`deque` uses a doubly-linked list of fixed-size blocks. Removing from the left just advances the front pointer — no elements shift.

```python
# Stack pattern (right end only): use list
stack = []
stack.append(10)    # O(1)
stack.pop()         # O(1)

# Queue pattern (both ends): use deque
from collections import deque
q = deque()
q.append(10)        # O(1) — add to right
q.popleft()         # O(1) — remove from left

# deque with maxlen — useful for sliding window
recent = deque(maxlen=3)
for i in range(10):
    recent.append(i)
print(recent)  # deque([7, 8, 9], maxlen=3)
```

Real-world benchmark: draining 100,000 items with `list.pop(0)` takes ~2.5 seconds. With `deque.popleft()` it takes ~0.01 seconds — roughly 200x faster.

> [↑ Back to Top](#top)

<a id="4-insert-delete"></a>
# 4. Insert, Delete, and the Shifting Cost

Anya's warehouse has boxes in strict order: sofa, table, chair, lamp, bookshelf. Her boss says: "Put a new plant stand between the chair and the lamp." Now Anya has to shove everything after the chair one position to the right to make room. The more boxes after the insertion point, the longer it takes.

<a id="visual-middle-insert"></a>
## Visual: Middle Insert

```
Insert "plant" at index 3 — must shift everything right first:

BEFORE:
  idx:   [0]     [1]     [2]     [3]     [4]     [5]
       ┌──────┬──────┬──────┬──────┬──────┬──────┐
       │ sofa │table │chair │ lamp │shelf │      │
       └──────┴──────┴──────┴──────┴──────┴──────┘
                                    ↑ insert here

SHIFT (right to left, 3 moves):
  Step 1: shelf  → [5]
  Step 2: lamp   → [4]
  Step 3: (slot [3] now free)

AFTER:
  idx:   [0]     [1]     [2]     [3]     [4]     [5]
       ┌──────┬──────┬──────┬──────┬──────┬──────┐
       │ sofa │table │chair │plant │ lamp │shelf │
       └──────┴──────┴──────┴──────┴──────┴──────┘

Worst case — insert at index 0 → ALL n elements must shift → O(n)

In memory: inserting 55 at index 2 of [10, 20, 30, 40, 50]

  BEFORE        shift →                AFTER INSERT
  ┌────┬────┬────┬────┬────┬────┐     ┌────┬────┬────┬────┬────┬────┐
  │ 10 │ 20 │ 30 │ 40 │ 50 │    │ →  │ 10 │ 20 │ 55 │ 30 │ 40 │ 50 │
  └────┴────┴────┴────┴────┴────┘     └────┴────┴────┴────┴────┴────┘
    0    1    2    3    4    5           0    1    2    3    4    5
              ↑                                   ↑
          insert here                         new value

Append (index n) = O(1)  →  no shifting needed
Insert at 0       = O(n)  →  shift all n elements
Insert at middle  = O(n/2) avg, O(n) worst
```

Inserting at the **end** (append) is O(1) — no shifting needed. That is why `list.append()` is fast and `list.insert(0, x)` is slow.

<a id="visual-deletion"></a>
## Visual: Deletion

Anya removes a box from the middle of her shelf. Now there is a gap. Every box after the gap must slide one position to the left to fill it.

```
Delete index 2 (value 30) from [10, 20, 30, 40, 50]:

  BEFORE
  ┌────┬────┬────┬────┬────┐
  │ 10 │ 20 │ 30 │ 40 │ 50 │
  └────┴────┴────┴────┴────┘
    0    1    2    3    4
              ↑
           delete

  SHIFT LEFT (fill the gap):
  ┌────┬────┬────┬────┬────┐
  │ 10 │ 20 │ 40 │ 40 │ 50 │  step 1: 40 ← one left
  └────┴────┴────┴────┴────┘
  ┌────┬────┬────┬────┬────┐
  │ 10 │ 20 │ 40 │ 50 │ 50 │  step 2: 50 ← one left
  └────┴────┴────┴────┴────┘

  AFTER (trim tail)
  ┌────┬────┬────┬────┐
  │ 10 │ 20 │ 40 │ 50 │  ✓
  └────┴────┴────┴────┘
    0    1    2    3

  Cost summary:
  ┌─────────────────────────────────────────┐
  │  Delete at end     → O(1)  (no shift)   │
  │  Delete at middle  → O(n)  (shift left) │
  │  Delete at front   → O(n)  (shift all)  │
  └─────────────────────────────────────────┘
```

Python's `list.pop()` with no arguments is O(1) — it removes from the end, no shifting needed.

<a id="modifying-while-iterating"></a>
## Modifying While Iterating

Anya is walking down the shelf counting boxes. Every time she finds a red box, she removes it. But when she removes one, all the boxes behind it slide forward — and she has already walked past that spot. She skips the box that slid into the gap without realizing it.

```python
# WRONG — skips elements!
numbers = [2, 4, 6]
for num in numbers:
    if num % 2 == 0:
        numbers.remove(num)

print(numbers)
# Expected: []
# Actual:   [4]  ← 4 was skipped!
```

Why it fails:

```
Step 0: index=0, num=2
  [2, 4, 6]
   ^
  remove(2) -> [4, 6]
  index advances to 1...

Step 1: index=1, num=6
  [4, 6]
      ^
  remove(6) -> [4]
  index advances to 2, out of range, loop ends.

  4 was NEVER visited! It slid into index 0,
  but we already passed index 0.
```

```python
# RIGHT — list comprehension (cleanest)
numbers = [num for num in numbers if num % 2 != 0]

# RIGHT — iterate over a copy
for num in numbers[:]:
    if num % 2 == 0:
        numbers.remove(num)

# RIGHT — iterate in reverse (for index-based deletion)
for i in range(len(numbers) - 1, -1, -1):
    if numbers[i] % 2 == 0:
        numbers.pop(i)
```

When you delete at index `i` and iterate right to left, the higher indices are already processed — no skipping.

> [↑ Back to Top](#top)

<a id="5-dynamic-resizing"></a>
# 5. Dynamic Resizing

Anya's warehouse has 4 shelves. All are full. A new shipment arrives. She cannot magically add one shelf — she has to rent a bigger warehouse with 8 shelves, carry all 4 boxes over, then place the new one. That move is expensive (O(n)), but it does not happen often. Most of the time she just places a box on the next empty shelf (O(1)).

When capacity is full:

1. A larger memory block is allocated (usually double the size)
2. All elements are copied to the new block
3. Old memory is freed

```
Capacity: 4
Elements: [10, 20, 30, 40]

Add 50:
  → Allocate new block, size 8
  → Copy 4 elements
  → Insert 50

Copying takes O(n). But this does not happen every time.
```

That is why append is **amortized O(1)** — if you average many operations, the cost per operation is constant.

<a id="static-vs-dynamic"></a>
## Static vs Dynamic Arrays

| | Static Array | Dynamic Array |
|---|---|---|
| **Size** | Fixed at creation | Grows automatically |
| **Resize** | Cannot grow | Allocates + copies |
| **Example** | C arrays, `array.array` | Python `list` |
| **Memory** | Exact fit | Extra capacity reserved |

Python uses dynamic arrays. In languages like C or Java, you must choose the size upfront.

> 📝 **Practice:** [Q4 — Initialize a 2D Grid Correctly](./practice.md#q4--2d-grid-init--initialize-a-2d-grid-correctly)

> [↑ Back to Top](#top)

<a id="6-multi-dimensional-arrays"></a>
# 6. Multi-Dimensional Arrays

Anya's warehouse expands — now she has multiple aisles, each with its own row of shelves. Aisle 0 has shelves [1, 2, 3]. Aisle 1 has shelves [4, 5, 6]. To find a box, she needs two numbers: aisle and shelf. That is a 2D array.

```python
matrix = [
    [1, 2, 3],
    [4, 5, 6]
]
```

In Python, this is not a real 2D contiguous block. It is an array of arrays — each row is a separate object on the heap.

```
[ref] → [1, 2, 3]
[ref] → [4, 5, 6]
```

This matters in performance discussions.

<a id="visual-2d-to-1d"></a>
## Visual: 2D to 1D Memory

Now imagine Anya's warehouse is actually a multi-story building. Each **floor** is a row. Each **space on that floor** is a column.

```
2D Concept — rows and columns (like floors in a building):

       col 0  col 1  col 2  col 3
row 0 ┌──────┬──────┬──────┬──────┐
      │  A   │  B   │  C   │  D   │
row 1 ├──────┼──────┼──────┼──────┤
      │  E   │  F   │  G   │  H   │   ← arr[1][2] = G
row 2 ├──────┼──────┼──────┼──────┤
      │  I   │  J   │  K   │  L   │
      └──────┴──────┴──────┴──────┘

RAM is one flat strip — rows are laid out end-to-end (row-major order):

Flat: ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
      │ A │ B │ C │ D │ E │ F │ G │ H │ I │ J │ K │ L │
      └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
        0   1   2   3   4   5   6   7   8   9  10  11
        ←── row 0 ───→ ←── row 1 ───→ ←── row 2 ───→

Formula:  flat_index = row × num_cols + col
For arr[1][2]:  1 × 4 + 2 = 6  →  value at index 6 = G  ✓

Cache behavior — row-by-row is fast, column-by-column is slow:

  Row-major (FAST)             Column-major (SLOW)
  for row → for col            for col → for row
  reads: A B C D E F G H …    reads: A E I  B F J  C G K …
         ←─── sequential ───→          ↑ jumps 4 bytes each time
         CPU cache loves this           cache misses on every step
```

```python
# Row-major loop (fast — sequential memory reads):
for i in range(rows):
    for j in range(cols):
        process(arr[i][j])

# Column-major loop (slow — jumping in memory):
for j in range(cols):
    for i in range(rows):
        process(arr[i][j])
```

<a id="list-multiplication-trap"></a>
## List Multiplication Trap

Anya tries to create 3 identical shelves using a shortcut. But the shortcut creates 3 labels pointing to the SAME shelf — change one, all three change.

```python
# WRONG — three references to the SAME inner list
grid = [[0] * 3] * 3
grid[0][0] = 9
print(grid)
# [[9, 0, 0], [9, 0, 0], [9, 0, 0]]  — ALL rows changed!
```

```
grid[0] ---> 0xABC --> [0, 0, 0]
grid[1] ---> 0xABC --> [0, 0, 0]   ← same object!
grid[2] ---> 0xABC --> [0, 0, 0]
```

```python
# RIGHT — list comprehension creates fresh lists
grid = [[0] * 3 for _ in range(3)]
grid[0][0] = 9
print(grid)
# [[9, 0, 0], [0, 0, 0], [0, 0, 0]]  — only row 0 changed
```

Each iteration of the comprehension calls `[0] * 3` again, creating a fresh list at a new memory address. Multiplication is safe for flat lists of immutables: `[0] * 5` works correctly because reassigning an element replaces a reference, it does not mutate the integer object.

> [↑ Back to Top](#top)

<a id="7-in-place-vs-out-of-place"></a>
# 7. In-Place vs Out-of-Place

Anya's boss asks her to sort all the boxes on the shelf. She can either rearrange them on the same shelf (in-place, no extra space) or copy them to a new shelf in sorted order (out-of-place, needs a second shelf). In interviews, always clarify: "Are we allowed to use extra space?" That question alone shows maturity.

| | In-Place | Out-of-Place |
|---|---|---|
| **Modifies** | Original array | Creates new array |
| **Space** | O(1) | O(n) |
| **Example** | `arr.sort()` | `sorted(arr)` |

<a id="shallow-vs-deep-copy"></a>
## Shallow vs Deep Copy Trap

Anya copies a shelf list to give to her colleague. But the copy only duplicated the labels — both lists still point to the same inner boxes. When her colleague rearranges a box, Anya's original changes too.

```python
# WRONG — shallow copy shares inner lists
grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
grid_copy = grid.copy()
grid_copy[1][1] = 9
print(grid[1])       # [0, 9, 0] — original CORRUPTED!
```

```python
import copy

# RIGHT — deep copy (any depth)
grid_copy = copy.deepcopy(grid)

# RIGHT — list comprehension (fast for 2D grids)
grid_copy = [row[:] for row in grid]
```

```
Method                  | New outer? | New inner? | Use when
------------------------|------------|------------|----------
b = a                   | No         | No         | Never for copying
b = a.copy()            | Yes        | No         | Flat lists only
b = [r[:] for r in a]   | Yes        | Yes (1 lv) | 2D grids
b = copy.deepcopy(a)    | Yes        | Yes (all)  | Deeply nested
```

> 📝 **Practice:** [Q5 — Reverse an Array In-Place](./practice.md#q5--reverse-in-place--reverse-an-array-in-place)

> [↑ Back to Top](#top)

<a id="8-array-thinking-patterns"></a>
# 8. Array Thinking Patterns

Anya discovers that most interview problems come down to a handful of patterns. Arrays are simple, but the problems on arrays are not simple. Recognizing the pattern is half the battle.

Key patterns:
- Two pointers
- Sliding window
- Prefix sum
- Kadane's algorithm
- Partitioning (Dutch National Flag)
- Sorting + scanning

> 📝 **Practice:** [Q13 — Two-Pointer Pair Sum](./practice.md#q13--two-pointer-pair-sum--two-pointer-pair-sum) · [Q14 — Three Sum](./practice.md#q14--three-sum--three-sum-triplets-to-zero) · [Q15 — Rotate Array](./practice.md#q15--rotate-array--rotate-array-right-by-k)

<a id="prefix-sum-arrays"></a>
## Prefix Sum Arrays — Precompute to Answer in O(1)

Think of a bank account ledger. Instead of adding up all transactions to find your balance on day N, you record a running total — then any range query is just two lookups.

A **prefix sum array** stores the running sum from index 0 to i at position i. This turns repeated range-sum queries from O(n) into O(1).

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]
prefix = [0] * (len(nums) + 1)

for i, x in enumerate(nums):
    prefix[i + 1] = prefix[i] + x

def range_sum(l, r):
    return prefix[r + 1] - prefix[l]  # O(1)

range_sum(2, 5)   # sum of indices 2,3,4,5 = 4+1+5+9 = 19
```

```
nums:    [ 3,  1,  4,  1,  5,  9,  2,  6 ]
prefix:  [ 0,  3,  4,  8,  9, 14, 23, 25, 31 ]
                                             ↑ prefix[r+1]
                                   ↑ prefix[l]
range_sum(2,5) = prefix[6] - prefix[2] = 23 - 4 = 19  ✓
```

**2D prefix sum** (for matrix range queries):

```python
matrix = [[1,2,3],[4,5,6],[7,8,9]]
rows, cols = len(matrix), len(matrix[0])
P = [[0]*(cols+1) for _ in range(rows+1)]

for r in range(rows):
    for c in range(cols):
        P[r+1][c+1] = matrix[r][c] + P[r][c+1] + P[r+1][c] - P[r][c]

def submatrix_sum(r1, c1, r2, c2):
    return P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
```

**When to use prefix sum:**
- Multiple range sum queries on a static array → O(1) per query after O(n) build
- Subarray with target sum → combine with hashmap `{prefix_sum: index}`
- 2D matrix range queries

**Difference array** (inverse — for range updates):

```python
diff = [0] * (n + 1)
diff[l] += val
diff[r + 1] -= val

import itertools
result = list(itertools.accumulate(diff[:n]))
```

**Complexity:** Build O(n), Query O(1), Space O(n)

> 📝 **Practice:** [Q9 — Build a Prefix Sum Array](./practice.md#q9--prefix-sum-build--build-a-prefix-sum-array) · [Q10 — Range Sum Query](./practice.md#q10--range-sum-query--range-sum-query) · [Q11 — Count Subarrays with Sum K](./practice.md#q11--subarray-sum-k--count-subarrays-with-sum-k) · [Q25 — Find Subarray with Exact Sum](./practice.md#q25--subarray-with-target-sum--find-subarray-with-exact-sum-hashmap--prefix)

<a id="visual-prefix-sum"></a>
## Visual: Prefix Sum — The Scoreboard

Anya's team plays 6 rounds. The scores per round are:

```
Original scores — 6 rounds:

  Round:    1    2    3    4    5    6
           ┌────┬────┬────┬────┬────┬────┐
  Score:   │  3 │  1 │  4 │  1 │  5 │  9 │
           └────┴────┴────┴────┴────┴────┘
  Index:     0    1    2    3    4    5

Build prefix sum — running total at each step:

  prefix[0] = 3
  prefix[1] = 3 + 1  =  4
  prefix[2] = 4 + 4  =  8
  prefix[3] = 8 + 1  =  9
  prefix[4] = 9 + 5  = 14
  prefix[5] = 14 + 9 = 23

           ┌────┬────┬────┬────┬────┬────┐
  Prefix:  │  3 │  4 │  8 │  9 │ 14 │ 23 │
           └────┴────┴────┴────┴────┴────┘
  Index:     0    1    2    3    4    5

Query: "Total score from round 2 to round 5?" (index 1 to 4)

           ┌────┬────┬────┬────┬────┬────┐
  Prefix:  │  3 │  4 │  8 │  9 │ 14 │ 23 │
           └────┴────┴────┴────┴────┴────┘
                  ↑                   ↑
             prefix[0]=3          prefix[4]=14

  sum(1, 4) = prefix[4] - prefix[0]
            =    14     -     3
            =    11   ✓

  Without prefix: add 1+4+1+5 → 4 operations    O(n) per query
  With prefix:    14 - 3       → 1 operation     O(1) per query

  ┌─────────────────────────────────────────────────┐
  │  Build once: O(n)   Query forever: O(1)          │
  │  1M rounds + 1M queries → O(n) not O(n²)         │
  └─────────────────────────────────────────────────┘
```

Build once in O(n). Answer every query in O(1). Total: O(n + q) instead of O(nq).

<a id="kadanes-algorithm"></a>
## Kadane's Algorithm — Maximum Subarray

Anya and her friends are running a tab at a bar. Some rounds she buys drinks (positive), some rounds someone splits (negative). She wants to find the best streak of consecutive rounds — the stretch of time when the tab was most in her favor.

The key insight: if the **running total goes negative, abandon ship. Start fresh.** A negative running total only drags down whatever comes next.

```
Value:      -2   1  -3   4  -1   2   1  -5   4
─────────────────────────────────────────────────
Running:    -2   1  -2   4   3   5   6   1   5
                     ↑           ↑
             reset here?     best so far = 6

Trace:
  i=0: current = max(-2, -2)         = -2   best = -2
  i=1: current = max(1, -2+1)        =  1   best =  1
  i=2: current = max(-3, 1-3)        = -2   best =  1
  i=3: current = max(4, -2+4)        =  4   best =  4
  i=4: current = max(-1, 4-1)        =  3   best =  4
  i=5: current = max(2, 3+2)         =  5   best =  5
  i=6: current = max(1, 5+1)         =  6   best =  6  ← answer
  i=7: current = max(-5, 6-5)        =  1   best =  6
  i=8: current = max(4, 1+4)         =  5   best =  6
```

The best subarray is `[4, -1, 2, 1]` with sum **6**.

```python
def kadane(arr):
    max_sum = arr[0]
    current = arr[0]
    for i in range(1, len(arr)):
        current = max(arr[i], current + arr[i])
        max_sum = max(max_sum, current)
    return max_sum
```

O(n) time, O(1) space. One of the most beautiful algorithms in DSA.

**Important edge case:** initialize `max_sum` and `current` to `arr[0]`, not `0`. If all elements are negative, returning `0` would imply an empty subarray — but the problem requires at least one element.

<a id="dutch-national-flag"></a>
## Dutch National Flag — Three-Way Partition

Dijkstra posed this problem: imagine you have a random arrangement of red, white, and blue balls. Sort them in a single pass.

**Three-pointer strategy:**
- `low` — everything before low is RED (sorted)
- `mid` — the current ball being examined
- `high` — everything after high is BLUE (sorted)

Rules:
- `arr[mid] == RED`: swap with `low`, advance both `low` and `mid`
- `arr[mid] == WHITE`: it is in the right zone, just advance `mid`
- `arr[mid] == BLUE`: swap with `high`, retreat `high` (do NOT advance mid)

```
Step-by-step on [W, R, B, W, R, R, B, W]:

i=0: arr[mid]=W → mid++
     [W, R, B, W, R, R, B, W]  low=0, mid=1, high=7

i=1: arr[mid]=R → swap(low,mid), low++, mid++
     [R, W, B, W, R, R, B, W]  low=1, mid=2, high=7

i=2: arr[mid]=B → swap(mid,high), high--
     [R, W, W, W, R, R, B, B]  low=1, mid=2, high=6

i=2: arr[mid]=W → mid++
     low=1, mid=3, high=6

i=3: arr[mid]=W → mid++
     low=1, mid=4, high=6

i=4: arr[mid]=R → swap(low,mid), low++, mid++
     [R, R, W, W, W, R, B, B]  low=2, mid=5, high=6

i=5: arr[mid]=R → swap(low,mid), low++, mid++
     [R, R, R, W, W, W, B, B]  low=3, mid=6, high=6

mid > high → done!
Result: [R, R, R, W, W, W, B, B]  ✓
```

One pass, O(n) time, O(1) space.

```python
def dutch_national_flag(arr, low_val, mid_val, high_val):
    low = 0
    mid = 0
    high = len(arr) - 1

    while mid <= high:
        if arr[mid] == low_val:
            arr[low], arr[mid] = arr[mid], arr[low]
            low += 1
            mid += 1
        elif arr[mid] == mid_val:
            mid += 1
        else:
            arr[mid], arr[high] = arr[high], arr[mid]
            high -= 1
```

This exact algorithm is used in the partition step of 3-way quicksort.

> [↑ Back to Top](#top)

<a id="9-real-world-impact"></a>
# 9. Real-World Impact

Anya graduates from the warehouse and joins a real engineering team. She discovers that arrays are not just for coding interviews — they are everywhere. Buffers, caches, batch processing, image processing, database pages, network packet queues — all backed by arrays. The reason is simple: contiguous memory means fast access and cache-friendly traversal.

<a id="cache-friendliness"></a>
## Cache Friendliness

When the CPU reads one element from an array, it loads a chunk of nearby memory into a fast cache line. Since array elements are contiguous, the next elements are already in cache — no expensive RAM trips. Linked lists scatter nodes across the heap, so every traversal step is a cache miss.

This is why arrays outperform linked lists in many real systems, even when the theoretical complexity is the same.

<a id="numpy-contiguous-memory"></a>
## NumPy and Contiguous Memory

A Python list is an array of pointers. Each element is a Python object stored separately on the heap. `[1, 2, 3]` in Python: the list stores 3 pointers (8 bytes each), and each integer is a full Python object (~28 bytes). Total: ~108 bytes for 3 integers.

A **NumPy array** stores raw numeric data contiguously. `np.array([1, 2, 3], dtype=int32)`: 3 × 4 bytes = 12 bytes. 9x less memory, and CPU cache lines are used efficiently.

```python
import numpy as np
import time

size = 10_000_000

# Python list approach
py_list = list(range(size))
start = time.time()
result = [x * 2 for x in py_list]
print(f"Python list multiply: {time.time() - start:.3f}s")  # ~0.8s

# NumPy array approach
np_array = np.arange(size, dtype=np.int32)
start = time.time()
result = np_array * 2  # single C-level loop over contiguous memory
print(f"NumPy multiply:       {time.time() - start:.3f}s")  # ~0.01s

# Strides — NumPy's way of describing memory layout
matrix = np.array([[1, 2, 3], [4, 5, 6]])
print(f"Shape: {matrix.shape}, Strides: {matrix.strides}")
# Strides: (12, 4) means moving one row = 12 bytes, one column = 4 bytes
```

**Strides** are NumPy's internal bookkeeping for how many bytes to skip to move one step in each dimension. This is how NumPy performs slicing without copying data. NumPy is the backbone of pandas, scikit-learn, TensorFlow, and PyTorch.

<a id="circular-buffers"></a>
## Circular Buffers

A **circular buffer** (ring buffer) is a fixed-size array used as a FIFO queue. The write pointer and read pointer advance modulo the buffer size. When the write pointer catches the read pointer, the buffer is full.

Used everywhere:
- Audio drivers: microphone samples written to a ring buffer; playback reads from it
- Linux kernel: `pipe`, `kfifo`, network socket receive buffers
- Video streaming: decoder writes decoded frames; renderer reads them

```python
class CircularBuffer:
    """Fixed-size ring buffer. O(1) enqueue and dequeue."""

    def __init__(self, capacity: int):
        self.buffer = [None] * capacity
        self.capacity = capacity
        self.read_pos = 0
        self.write_pos = 0
        self.size = 0

    def write(self, value) -> bool:
        if self.size == self.capacity:
            return False  # Buffer full — audio overrun
        self.buffer[self.write_pos] = value
        self.write_pos = (self.write_pos + 1) % self.capacity
        self.size += 1
        return True

    def read(self) -> object:
        if self.size == 0:
            return None  # Buffer empty — audio underrun
        value = self.buffer[self.read_pos]
        self.read_pos = (self.read_pos + 1) % self.capacity
        self.size -= 1
        return value

# Audio streaming simulation
audio_buffer = CircularBuffer(capacity=4096)
for sample in [0.1, 0.3, -0.2, 0.5, 0.8]:
    audio_buffer.write(sample)
while len(audio_buffer) > 0:
    sample = audio_buffer.read()

    def __len__(self):
        return self.size
```

The key property: **no dynamic memory allocation during operation.** Audio drivers cannot call `malloc` mid-stream (too slow, non-deterministic). The `% self.capacity` trick makes the array wrap around — turning a linear array into a logical ring.

<a id="prefix-sum-analytics"></a>
## Prefix Sum in Analytics

Analytics dashboards answer questions like: "What is the total revenue between day 30 and day 90?" Naive: iterate from index 30 to 90 = O(n) per query. With prefix sums: O(n) preprocessing, O(1) per range query.

```python
import random
random.seed(42)
daily_revenue = [random.randint(10000, 100000) for _ in range(365)]

prefix = [0] * (len(daily_revenue) + 1)
for i, rev in enumerate(daily_revenue):
    prefix[i + 1] = prefix[i] + rev

def range_sum(start: int, end: int) -> int:
    return prefix[end + 1] - prefix[start]  # O(1)

q1_revenue = range_sum(0, 89)    # Jan–Mar
q2_revenue = range_sum(90, 180)  # Apr–Jun
print(f"Q1 revenue: ${q1_revenue:,}")
print(f"Q2 revenue: ${q2_revenue:,}")
```

Google BigQuery, ClickHouse, and Redshift use prefix sum techniques internally for materialized aggregate queries.

> 📝 **Practice:** [Q20 — Shallow vs Deep Copy Trap](./practice.md#q20--shallow-vs-deep-copy--shallow-vs-deep-copy-trap) · [Q21 — NumPy vs Python List Tradeoffs](./practice.md#q21--numpy-vs-list--numpy-vs-python-list-tradeoffs) · [Q22 — Circular Buffer](./practice.md#q22--circular-buffer--implement-a-circular-buffer)

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

```
Operation               Time        Notes
──────────────────────────────────────────────────────────
Access arr[i]           O(1)        Base + offset formula
Search (unsorted)       O(n)        Must check each element
Search (sorted)         O(log n)    Binary search
Insert at end           O(1)        Amortized for dynamic array
Insert at middle/start  O(n)        Must shift elements
Delete at end           O(1)        Just shrink size
Delete at middle/start  O(n)        Must shift elements
Build prefix sum        O(n)        One pass
Range query (prefix)    O(1)        After build
Kadane's algorithm      O(n)        One pass, O(1) space
Dutch flag partition    O(n)        One pass, O(1) space
──────────────────────────────────────────────────────────
```

| Concept | Key Takeaway |
|---------|-------------|
| O(1) access | The superpower of arrays — use it |
| O(n) insert/delete | The weakness — use deque for front operations |
| Prefix sums | Convert O(n) range queries to O(1) |
| In-place algorithms | Kadane, Dutch flag save space by reusing the array |
| Cache friendliness | Contiguous memory = fast traversal |
| Dynamic resizing | Amortized O(1) append, occasional O(n) copy |

**Common professional mistakes:**
- Ignoring edge cases (empty list)
- Modifying array during iteration
- Using `list.pop(0)` instead of `deque.popleft()`
- Shallow copying nested arrays
- `[[0]*3]*3` creating shared references

**Interview depth — you should explain without memorizing:**
- Why indexing is constant time
- Why middle insert shifts elements
- How dynamic resizing works and what amortized means
- Why arrays are cache-friendly
- When arrays are not ideal (frequent front insertions)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [01_complexity_analysis → theory.md](../01_complexity_analysis/theory.md) |
| ➡ Next Module | [03_strings → theory.md](../03_strings/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[01 Complexity Analysis →](../01_complexity_analysis/theory.md) · [03 Strings →](../03_strings/theory.md) · [07 Linked List →](../07_linked_list/theory.md) · [11 Two Pointers →](../11_two_pointers/theory.md)

**Jump to specific topics in other files:**
- Two pointers pattern → [11_two_pointers § theory.md](../11_two_pointers/theory.md)
- Sliding window pattern → [12_sliding_window § theory.md](../12_sliding_window/theory.md)
- Binary search on sorted arrays → [13_binary_search § theory.md](../13_binary_search/theory.md)
- Dynamic array vs linked list → [07_linked_list § theory.md](../07_linked_list/theory.md)

> [↑ Back to Top](#top)
