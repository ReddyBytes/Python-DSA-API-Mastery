# Complexity Analysis — A Visual Story

---

## Chapter 1: The Question That Matters

Forget the formal definition for a moment.

Here is the only question Big-O is trying to answer:

> **If I double my input, how much more work does my program do?**

That is it. Everything else is a consequence of that question.

---

## Chapter 2: The Kitchen Analogy

Imagine you run a kitchen. A customer walks in and orders food.

### O(1) — The Microwave

You pull a pre-made sandwich out of the fridge and heat it.
Does it matter if 1 customer orders or 1000 customers ordered yesterday?
No. The time to heat *one* sandwich never changes.

```
Orders today: 1      → Time: 30 seconds
Orders today: 1000   → Time: 30 seconds (for this one sandwich)
Orders today: 1M     → Time: 30 seconds
```

Array lookup `arr[5]` is the microwave. The computer knows the address instantly.

---

### O(log n) — The Recipe Index

You have a giant recipe book sorted alphabetically. You want "Mushroom Risotto."
You don't read page 1, then page 2, then page 3...
You open the middle, see you're in the M's, then narrow it down again.

Every step you cut the remaining search in half.

```
1000 pages  → ~10 steps  (2^10 = 1024)
1,000,000   → ~20 steps  (2^20 ≈ 1M)
1,000,000,000 → ~30 steps
```

Doubling the book adds just ONE more step. That is the magic of logarithms.

---

### O(n) — Cooking Burgers One by One

You have an order for n burgers. Each takes 3 minutes.
Double the burgers? Double the time. Simple, proportional.

```
n = 10   → 30 minutes
n = 20   → 60 minutes
n = 100  → 300 minutes
```

Linear search through an array is flipping burgers one by one.

---

### O(n log n) — The Head Chef Strategy

You have n ingredients scattered on a table and you need them sorted by type.
The head chef splits the pile in half, gives each half to a sous chef,
who each split again, and so on — then everyone merges their sorted piles back.

It is better than O(n²) but has that log n overhead from all the splitting.
Most real sorting algorithms (merge sort, heapsort) live here.

---

### O(n²) — The Party Icebreaker

You throw a party with n guests. You decide *every person must meet every other person*.
For 10 guests: 10 × 9 = 90 introductions.
For 20 guests: 20 × 19 = 380 introductions.
Double the guests → roughly 4x the introductions.

```
n = 10    →   ~100 pairs
n = 100   → ~10,000 pairs
n = 1000  → ~1,000,000 pairs
```

Bubble sort, selection sort, and most naive nested-loop algorithms live here.

---

### O(2^n) — The Password Hacker

You are trying to crack a binary password of length n.
For each bit, it is either 0 or 1. The number of combinations is 2^n.

```
n = 10  →      1,024 combinations
n = 20  →  1,048,576 combinations
n = 30  →  1,073,741,824 combinations
```

Add ONE more bit → double the work. This explodes almost instantly.

---

## Chapter 3: The Growth Curve — ASCII Art

How fast does each complexity grow as n increases?
(Each row represents a rough relative magnitude)

```
                 n = 1   n = 4   n = 8   n = 16   n = 32
─────────────────────────────────────────────────────────
O(1)             1       1       1        1         1
O(log n)         0       2       3        4         5
O(n)             1       4       8       16        32
O(n log n)       0       8      24       64       160
O(n²)            1      16      64      256      1024
O(2^n)           2      16     256    65536  ~4 billion
─────────────────────────────────────────────────────────
```

Visualized as a graph (higher = more work):

```
 work
  ^
  |                                               2^n
  |                                         *
  |                                    *
  |                              *
  |                    n²   *  *
  |               *  *  * *
  |          *  *
  |     * * n log n
  |   *
  |  * n
  | *
  |* log n
  |_________ 1
  +-----------------------------------> n
  0    10   20   30   40   50
```

The gap between O(n²) and O(n log n) becomes enormous very quickly.
At n=1000, that gap is 1,000,000 vs 10,000 — a 100x difference.

---

## Chapter 4: A Concrete Story — "Find if 42 is in a list"

You have 1000 numbers. Is 42 in there?

### Approach 1: Unsorted List — O(n)

You have 1000 slips of paper shuffled randomly.
You pick them up one by one until you find 42 (or run out).

```
[73, 5, 19, 42, 88, ...]  ← could be anywhere
 ^    ^   ^   ^ found!    ← average case: 500 checks
```

Worst case: 42 is at position 999, or not there at all → 1000 checks.

---

### Approach 2: Sorted List — O(log n)

The slips are sorted: 1, 2, 3, ... 1000.
You use binary search.

```
Step 1: Check position 500  → value 500 → too high, look left
Step 2: Check position 250  → value 250 → too high, look left
Step 3: Check position 125  → value 125 → too high, look left
Step 4: Check position  62  → value  62 → too high, look left
Step 5: Check position  31  → value  31 → too low,  look right
Step 6: Check position  46  → value  46 → too high, look left
Step 7: Check position  38  → value  38 → too low,  look right
Step 8: Check position  42  → value  42 → FOUND!
```

8 steps instead of 500 on average. For 1,000,000 numbers? Still ~20 steps.

---

### Approach 3: Hash Set — O(1)

You build a hash table from the list.
Now you just ask: "Is 42 in the table?"
The hash function computes a memory address directly.

```
hash(42) → go to memory slot 42 → yes, it's there!
```

1 step. Every time. Regardless of list size.

The trade-off: you need O(n) extra memory and O(n) time to build the table first.

---

## Chapter 5: Best / Average / Worst — The Phone Book Story

You are looking for "Williams" in a phone book (remember those?).

```
Phone book entries (simplified):
  Adams, Baker, Chen, Davis, ... Williams, ... Young, Zhao
  [0]    [1]    [2]   [3]         [n-2]         [n-1]  [n]
```

**Best case:** "Williams" is the very first entry you check. 1 comparison.
(Astronomically unlikely, but theoretically possible.)

**Average case:** You find "Williams" roughly halfway through.
On average, you check n/2 entries.

**Worst case:** "Williams" is the very last entry, or is not in the book at all.
You check all n entries before knowing.

```
Best     Average     Worst
  |         |           |
  v         v           v
[W.....................................] ← "Williams" at start
[.................W....................]  ← "Williams" at middle
[.....................................W] ← "Williams" at end (or not found)
```

Big-O almost always refers to **worst case** unless stated otherwise.
The worst case is your guarantee — it cannot get worse than this.

---

## Chapter 6: Space Complexity — The RAM Bill

Time is not the only resource. Memory costs money too (and time to allocate).

### Stack vs Heap — Two Different Bills

**The Stack** is like a notepad on your desk.
Fast to write on, but limited in size.
Each function call adds a "frame" to the stack — local variables, parameters.

```python
def factorial(n):
    if n == 0: return 1
    return n * factorial(n-1)   # each call adds a stack frame
```

Calling `factorial(5)` creates 5 frames stacked on top of each other:

```
|  factorial(0)  |  ← top of stack
|  factorial(1)  |
|  factorial(2)  |
|  factorial(3)  |
|  factorial(4)  |
|  factorial(5)  |  ← bottom (original call)
+────────────────+
```

Space complexity: O(n) — the stack depth equals the input n.
If n = 100,000, you might get a stack overflow!

**The Heap** is like renting a warehouse.
Bigger, slower, and you have to manage it (or let a garbage collector do it).
`list = [0] * n` allocates O(n) heap memory.

---

### Quick Space Complexity Examples

```
Operation                          Space
─────────────────────────────────────────
Iterative loop over array          O(1)   — no extra memory
Building a copy of array           O(n)   — new array of same size
2D matrix (n × n)                  O(n²)  — n² cells
Recursive DFS on tree of depth d   O(d)   — stack depth = tree depth
Storing all subsets of n items     O(2^n) — exponential
```

---

## Chapter 7: Rules for Simplifying — Why Drop Constants?

You measured your algorithm: it does exactly `3n + 7` operations.
Big-O says it is O(n). Why do we throw away the 3 and the 7?

### Rule 1: Drop Constants

`3n + 7` → O(n)

Because Big-O describes *growth rate*, not the exact count.
At n = 1,000,000: `3n = 3,000,000` and `7` is irrelevant noise.
Whether it is `3n` or `100n`, it still grows *linearly*.

A computer 3x faster running O(n) beats a slow computer running O(n²) once n is large enough.

```
3n vs 100n:   constant factor, same growth shape
3n vs n²:     fundamentally different growth, n² always wins eventually
```

### Rule 2: Drop Lower Order Terms

`n² + n + 100` → O(n²)

At n = 1000:
- n² = 1,000,000
- n  = 1,000
- 100 = 100

The `n` term is 0.1% of `n²`. The 100 is 0.01%.
They are noise at scale.

### Rule 3: Keep the Dominant Term

When you have nested loops or combined operations, the slowest part wins:

```python
for i in range(n):          # O(n)
    print(i)

for i in range(n):          # O(n²)
    for j in range(n):
        print(i, j)
```

Total: O(n) + O(n²) = O(n²). The quadratic dominates.

---

## Chapter 8: Reading Constraints Like a Pro

In competitive programming (and system design interviews), the input size tells you what algorithm is expected.

```
Constraint          Max operations    What algorithm fits
────────────────────────────────────────────────────────────
n ≤ 10              ~1,000            O(n!) backtracking OK
n ≤ 20              ~1,000,000        O(2^n) bitmask DP OK
n ≤ 100             ~1,000,000        O(n³) OK
n ≤ 1,000           ~1,000,000        O(n²) OK
n ≤ 10,000          ~100,000,000      O(n²) maybe, O(n log n) safe
n ≤ 100,000         ~1,000,000,000    Must be O(n log n) or O(n)
n ≤ 1,000,000       huge              Must be O(n) or O(n log n)
n ≤ 100,000,000     enormous          Must be O(n) or O(log n)
```

**Rule of thumb:** A modern computer does roughly **10^8 simple operations per second**.

So if n = 10^5 and you have an O(n²) algorithm, that is 10^10 operations — about 100 seconds.
Way too slow. You need O(n log n): 10^5 × 17 ≈ 1.7 × 10^6 operations — well under a second.

### Practical Example

Problem: "Given n ≤ 10^5 numbers, find if any two sum to target."

- O(n²) approach: check every pair → 10^10 ops → too slow
- O(n log n) approach: sort + two pointers → fast enough
- O(n) approach: hash set → even faster

The constraint `n ≤ 10^5` is the interviewer quietly telling you: "Please don't use nested loops."

---

## Chapter 9: Quick Reference Card

```
Complexity   Name           Example                     Real feeling
──────────────────────────────────────────────────────────────────────
O(1)         Constant       Array index, hash lookup    Instant
O(log n)     Logarithmic    Binary search               Almost instant
O(n)         Linear         Single loop, linear scan    Proportional
O(n log n)   Linearithmic   Merge sort, heap sort       Pretty fast
O(n²)        Quadratic      Bubble sort, nested loops   Gets slow fast
O(n³)        Cubic          3-nested loops              Very slow
O(2^n)       Exponential    Subsets, brute force        Practically unusable
O(n!)        Factorial      All permutations            Truly hopeless
──────────────────────────────────────────────────────────────────────
```

### The Mental Model to Keep

Think of Big-O as a *tier list* for algorithms.
An O(n log n) algorithm is always in a higher tier than O(n²),
regardless of constants or small inputs.

When you are designing a solution, ask: "Which tier is this in?"
If it is in the wrong tier, no amount of micro-optimization will save it.

---

*Next up: Arrays — where memory layout makes everything O(1) or O(n).*

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
