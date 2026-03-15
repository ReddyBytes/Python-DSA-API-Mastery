# Arrays — A Visual Story

---

## Chapter 1: The Parking Lot

Picture a parking lot designed by a very organized engineer.

Every space is **exactly the same size**.
Every space has a **number painted on the ground**: 0, 1, 2, 3, ...
The spaces are in a **straight row**, no gaps.

```
┌──────┬──────┬──────┬──────┬──────┬──────┐
│  42  │  17  │  99  │   5  │  88  │  23  │
└──────┴──────┴──────┴──────┴──────┴──────┘
  [0]    [1]    [2]    [3]    [4]    [5]
```

That is an array. Exactly that.

The "parking lot manager" (your CPU) knows:
- Where space [0] starts (the **base address**)
- How wide each space is (the **element size** — 4 bytes for an integer)
- Your requested index

So finding space [3] is a single arithmetic problem, not a search.

---

## Chapter 2: Why Random Access is O(1)

The formula is almost embarrassingly simple:

```
address_of(arr[i]) = base_address + (i × element_size)
```

Let us walk through it with real numbers.

Suppose your array starts at memory address `1000` and stores 4-byte integers.

```
Index   Address    Value
──────────────────────────
arr[0]  1000       42
arr[1]  1004       17
arr[2]  1008       99
arr[3]  1012        5
arr[4]  1016       88
arr[5]  1020       23
```

Want `arr[3]`?
- `1000 + (3 × 4) = 1000 + 12 = 1012`
- Go to address 1012. Done.

```
Memory (each cell = 4 bytes):

1000  1004  1008  1012  1016  1020
 │     │     │     │     │     │
 42    17    99    5    88    23
              ↑
         arr[3] = 1000 + (3 × 4)
              = address 1012
              = value 5   ✓
```

No looping. No searching. One arithmetic operation, one memory read.
It does not matter if the array has 10 elements or 10 million.
The math is the same. That is O(1).

---

## Chapter 3: Inserting in the Middle — Moving Furniture

You have an apartment. The furniture is arranged in a strict order:
sofa, table, chair, lamp, bookshelf.

Your friend says: "Can you put a new plant stand between the chair and the lamp?"

Now you have to shove everything after the chair one position to the right
to make room.

```
Before inserting "plant" at index 3:

[sofa] [table] [chair] [lamp] [bookshelf] [  ]
  0       1       2      3        4         5   ← empty slot at end

Step 1: Move bookshelf right
[sofa] [table] [chair] [lamp] [    ] [bookshelf]

Step 2: Move lamp right
[sofa] [table] [chair] [    ] [lamp] [bookshelf]

Step 3: Place plant at index 3
[sofa] [table] [chair] [plant] [lamp] [bookshelf]
```

How many moves did that take? We had to shift `(n - 3)` items.
In the worst case — inserting at index 0 — we shift ALL n items.

That is O(n). Every. Single. Time.

### In Memory

```
Original array, inserting 55 at index 2:

Before:
Index:  0    1    2    3    4
Value: [10] [20] [30] [40] [50]

Shift step 1 — move index 4 to index 5:
Index:  0    1    2    3    4    5
Value: [10] [20] [30] [40] [50] [50]  ← duplicate temporarily

Shift step 2 — move index 3 to index 4:
Index:  0    1    2    3    4    5
Value: [10] [20] [30] [40] [40] [50]

Shift step 3 — move index 2 to index 3:
Index:  0    1    2    3    4    5
Value: [10] [20] [30] [30] [40] [50]

Write 55 at index 2:
Index:  0    1    2    3    4    5
Value: [10] [20] [55] [30] [40] [50]  ✓
```

Inserting at the **end** (append) is O(1) — no shifting needed.
That is why `list.append()` is fast and `list.insert(0, x)` is slow.

---

## Chapter 4: Deleting from the Middle — Same Problem, Backwards

Delete index 2 from `[10, 20, 30, 40, 50]`:

```
Before:
Index:  0    1    2    3    4
Value: [10] [20] [30] [40] [50]

Remove 30 at index 2. Now shift everything left:

Step 1:
Value: [10] [20] [40] [40] [50]  ← 40 moved left

Step 2:
Value: [10] [20] [40] [50] [50]  ← 50 moved left

Trim last element:
Value: [10] [20] [40] [50]       ✓
```

Again O(n) in the worst case. The gap must be filled by shuffling.

Deleting from the **end** is O(1). Python's `list.pop()` with no arguments
is O(1) for exactly this reason.

---

## Chapter 5: 2D Arrays — The Apartment Building

Now imagine your parking lot is actually a multi-story structure.

- Each **floor** is a row
- Each **space on that floor** is a column

```
Floor 0:  [A] [B] [C] [D]
Floor 1:  [E] [F] [G] [H]
Floor 2:  [I] [J] [K] [L]
```

You want `arr[1][2]` — floor 1, space 2. That is `G`.

But RAM is a single flat strip of memory — no floors, just one long row.
So how does 2D map to 1D?

### Row-Major Order (how Python/C store it)

All of floor 0 comes first, then all of floor 1, then floor 2:

```
Flat memory:
[A][B][C][D][E][F][G][H][I][J][K][L]
  ←── row 0 ──→ ←── row 1 ──→ ←── row 2 ──→
  0   1   2   3   4   5   6   7   8   9  10  11
```

Formula:
```
address_of(arr[row][col]) = base + (row × num_cols + col) × element_size
```

For `arr[1][2]` with 4 columns:
```
base + (1 × 4 + 2) × 4 = base + 6 × 4 = base + 24
```

That is index 6 in flat memory = value `G`. Correct!

### Why does this matter?

Iterating row by row is **cache-friendly** — you read memory sequentially.
Iterating column by column is **cache-hostile** — you jump around in memory.

```
Row-major loop (fast — sequential memory reads):
for i in range(rows):
    for j in range(cols):
        process(arr[i][j])   ← reads arr[0][0], arr[0][1], arr[0][2]...

Column-major loop (slow — jumping in memory):
for j in range(cols):
    for i in range(rows):
        process(arr[i][j])   ← reads arr[0][0], arr[1][0], arr[2][0]...
                                          ↑ jumps by num_cols each time
```

---

## Chapter 6: Prefix Sums — The Cumulative Scoreboard

Your team plays 6 rounds. The scores per round are:

```
Round:    1    2    3    4    5    6
Score:   [3]  [1]  [4]  [1]  [5]  [9]
```

Question: "What was the total score from round 2 to round 5?"
Naive answer: `1 + 4 + 1 + 5 = 11`. You added 4 numbers.

Now imagine 1 million rounds and someone asks 1 million range queries.
That is O(n) per query = O(n²) total. Painful.

### Build the Prefix Sum Array

The prefix sum array stores the *running total* at each index.

```
Original:  [3,  1,  4,  1,  5,  9]
           [0]  [1] [2] [3] [4] [5]

prefix[0] = 3
prefix[1] = 3 + 1 = 4
prefix[2] = 4 + 4 = 8
prefix[3] = 8 + 1 = 9
prefix[4] = 9 + 5 = 14
prefix[5] = 14 + 9 = 23

Prefix:    [3,  4,  8,  9,  14, 23]
```

### Range Query in O(1)

"Total score from index 1 to index 4 (rounds 2 to 5)?"

```
sum(1, 4) = prefix[4] - prefix[0]
           = 14 - 3
           = 11   ✓
```

The formula: `sum(left, right) = prefix[right] - prefix[left - 1]`

```
prefix[4] represents "total from start up to index 4"
prefix[0] represents "total from start up to index 0" (not including left)

  [3] [1] [4] [1] [5] [9]
  ←── prefix[0]=3 ──→↑
  ←──────── prefix[4]=14 ──────→
            ↑─── range we want ─↑ = 14 - 3 = 11
```

Build once in O(n). Answer every query in O(1). Total: O(n + q) instead of O(nq).

```python
def build_prefix(arr):
    prefix = [0] * len(arr)
    prefix[0] = arr[0]
    for i in range(1, len(arr)):
        prefix[i] = prefix[i-1] + arr[i]
    return prefix

def range_sum(prefix, left, right):
    if left == 0:
        return prefix[right]
    return prefix[right] - prefix[left - 1]
```

---

## Chapter 7: Kadane's Algorithm — The Running Tab at a Bar

You and your friends are running a tab at a bar. Some rounds you buy drinks (positive),
some rounds someone splits (negative). You want to find the best streak of consecutive
rounds — the stretch of time when the tab was most in your favor.

Array: `[-2, 1, -3, 4, -1, 2, 1, -5, 4]`

The key insight: if your running total goes **negative**, abandon ship. Start fresh.
A negative running total only drags down whatever comes next.

```
Value:      -2   1  -3   4  -1   2   1  -5   4
─────────────────────────────────────────────────
Running:    -2   1  -2   4   3   5   6   1   5
                     ↑           ↑
             reset here?     best so far = 6 (at index 6)

When running = -2 at index 2:
  Adding 4 to -2 gives 2.
  Starting fresh at 4 gives 4.
  Fresh is better! So reset.

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

Clean, elegant, O(n) time, O(1) space. One of the most beautiful algorithms in DSA.

---

## Chapter 8: Dutch National Flag — Sorting Three Colors

Dijkstra posed this problem: imagine you have a random arrangement of red, white,
and blue balls. Sort them in a single pass.

```
Input:  [W, R, B, W, R, R, B, W]
Goal:   [R, R, R, W, W, W, B, B]
```

### Three-Pointer Strategy

Set up three guards:
- `low` — everything before low is RED (sorted)
- `mid` — the current ball we are examining
- `high` — everything after high is BLUE (sorted)
- Between mid and high is the unsorted middle (WHITE + unknown)

```
Initial:
low=0, mid=0, high=7

[W, R, B, W, R, R, B, W]
 ↑                    ↑
mid,low             high
```

Rules:
- `arr[mid] == RED`: swap with `low`, advance both `low` and `mid`
- `arr[mid] == WHITE`: it is in the right zone, just advance `mid`
- `arr[mid] == BLUE`: swap with `high`, retreat `high` (do NOT advance mid yet)

```
Step-by-step on [W, R, B, W, R, R, B, W]:

i=0: arr[mid]=W (white)  → mid++
     [W, R, B, W, R, R, B, W]  low=0, mid=1, high=7

i=1: arr[mid]=R (red)    → swap(low,mid), low++, mid++
     [R, W, B, W, R, R, B, W]  low=1, mid=2, high=7

i=2: arr[mid]=B (blue)   → swap(mid,high), high--
     [R, W, W, W, R, R, B, B]  low=1, mid=2, high=6
     (do not advance mid — the swapped value needs checking)

i=2: arr[mid]=W (white)  → mid++
     [R, W, W, W, R, R, B, B]  low=1, mid=3, high=6

i=3: arr[mid]=W (white)  → mid++
     [R, W, W, W, R, R, B, B]  low=1, mid=4, high=6

i=4: arr[mid]=R (red)    → swap(low,mid), low++, mid++
     [R, R, W, W, W, R, B, B]  low=2, mid=5, high=6

i=5: arr[mid]=R (red)    → swap(low,mid), low++, mid++
     [R, R, R, W, W, W, B, B]  low=3, mid=6, high=6

mid > high → done!

Result: [R, R, R, W, W, W, B, B]  ✓
```

One pass through the array, O(n) time, O(1) space.

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
        else:  # high_val
            arr[mid], arr[high] = arr[high], arr[mid]
            high -= 1
```

This exact algorithm is used in the partition step of 3-way quicksort.

---

## Chapter 9: Array Complexity Cheat Sheet

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

### The Key Intuitions

1. **O(1) access** is the superpower of arrays. Use it.
2. **O(n) insertion/deletion** is the weakness. If you need frequent inserts, use a linked list or deque.
3. **Prefix sums** convert O(n) range queries into O(1) — always useful.
4. **In-place algorithms** (Kadane, Dutch flag) save space by reusing the array.

---

*Next up: Strings — character arrays with special rules and fascinating algorithms.*

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
