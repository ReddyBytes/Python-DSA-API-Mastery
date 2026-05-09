<a id="top"></a>
# 📘 01 – Complexity Analysis

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is Complexity Analysis?](#1-what-is-complexity-analysis)
  - [Why It Matters](#why-it-matters)
  - [The Core Question](#the-core-question)
  - [Two Types: Time and Space](#two-types-time-and-space)
- [2. Time Complexity — Best, Average, Worst](#2-time-complexity)
  - [Best Case](#best-case)
  - [Worst Case](#worst-case)
  - [The Phone Book Story](#the-phone-book-story)
- [3. Big-O Notation](#3-big-o-notation)
- [4. Common Time Complexities](#4-common-time-complexities)
  - [O(1) — Constant Time](#o1-constant-time)
  - [O(n) — Linear Time](#on-linear-time)
  - [O(n²) — Quadratic Time](#on2-quadratic-time)
  - [O(log n) — Logarithmic Time](#olog-n-logarithmic-time)
  - [O(2ⁿ) — Exponential Time](#o2n-exponential-time)
  - [Growth Comparison](#growth-comparison)
- [5. How to Calculate Time Complexity](#5-how-to-calculate-time-complexity)
  - [Step 1: Ignore Constants](#step-1-ignore-constants)
  - [Step 2: Focus on Input Size](#step-2-focus-on-input-size)
  - [Step 3: Nested Loops Multiply](#step-3-nested-loops-multiply)
  - [Step 4: Consecutive Loops Add](#step-4-consecutive-loops-add)
  - [Step 5: Drop Lower Terms](#step-5-drop-lower-terms)
  - [Choosing Algorithm by Input Size](#choosing-algorithm-by-input-size)
- [6. Real-World Impact](#6-real-world-impact)
  - [Database Index — O(n) vs O(log n)](#database-index)
  - [Hidden List Cost — list.insert(0) vs deque](#hidden-list-cost)
  - [Amortized Append — Dynamic Array](#amortized-append)
- [7. Space Complexity](#7-space-complexity)
- [8. Recursion and Stack Space](#8-recursion-and-stack-space)
  - [The Factorial Call Stack](#the-factorial-call-stack)
- [9. Pattern Recognition](#9-pattern-recognition)
  - [How to Think Like a Problem Solver](#how-to-think-like-a-problem-solver)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Big-O notation · time vs space trade-offs · common complexity classes (O(1) O(n) O(log n) O(n²) O(2^n)) · worst/average/best case

**Should Learn** — Important for real projects, comes up regularly:
amortized complexity · input size constraints · recursion space complexity

**Good to Know** — Useful in specific situations, not always tested:
Omega and Theta notation · complexity comparison edge cases

**Reference** — Know it exists, look up syntax when needed:
little-o notation · Master Theorem

Ravi was a curious 10-year-old boy.

One day, he asked the Code Wizard:

> "I wrote two programs. Both give correct answers.
> But one runs very fast… and the other takes forever. Why?"

The Code Wizard smiled.

> "Ravi… today you are entering the most powerful level of programming.
> Before learning Data Structures…
> Before learning Algorithms…
> You must learn how to measure **thinking speed**."

And that is where **Complexity Analysis** begins.

<a id="1-what-is-complexity-analysis"></a>
# 1. What Is Complexity Analysis?

Imagine you and your friend both need to find a word in a dictionary. You start from page 1 and flip through every single page. Your friend opens the middle, decides which half the word is in, and repeats. Both of you will find the word — but your friend finishes in seconds while you are still flipping after ten minutes. Complexity analysis is the science of measuring that difference.

<a id="why-it-matters"></a>
## Why It Matters

You have 2 ways to count 1,000,000 numbers.

Way 1: Count one by one.
Way 2: Use a formula.

Both are correct. But one is smarter.

Complexity Analysis helps us answer:

- Which solution is faster?
- Which solution uses less memory?
- Which solution will survive large inputs?
- Which solution will fail in interviews?

It is not about correctness. It is about **efficiency**.

<a id="the-core-question"></a>
## The Core Question

Imagine you have to:

- Find your friend in a class (30 students)
- Find your friend in a stadium (50,000 people)

If you check one by one, the stadium will take forever.

Complexity tells us:

> "How does time grow when input grows?"

If input becomes 10x bigger:
- Does time become 10x?
- 100x?
- 1000x?

That growth is complexity.

<a id="two-types-time-and-space"></a>
## Two Types: Time and Space

Think of cooking a meal. **Time complexity** is how long the recipe takes. **Space complexity** is how many pots and pans you need on the counter. A recipe can be fast but need every pot in the kitchen, or slow but use just one pan.

1. **Time Complexity** — How long the program runs.
2. **Space Complexity** — How much memory it uses.

> [↑ Back to Top](#top)

<a id="2-time-complexity"></a>
# 2. Time Complexity — Best, Average, Worst

Imagine Ravi searching for his red ball in a box full of toys. Sometimes the ball is right on top (lucky!), sometimes it is buried at the very bottom (unlucky). The time it takes depends on where the ball is — and that is why we measure best, average, and worst case.

<a id="best-case"></a>
## Best Case

Ball is on top. He finds it in 1 step.

```
[Ball]
[Toy]
[Toy]
[Toy]
```

Time = 1

<a id="worst-case"></a>
## Worst Case

Ball is at bottom. He checks all items.

```
[Toy]
[Toy]
[Toy]
[Ball]
```

Time = n

<a id="the-phone-book-story"></a>
## The Phone Book Story

You are looking for "Williams" in a phone book.

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

**Big-O almost always refers to worst case** unless stated otherwise.
The worst case is your guarantee — it cannot get worse than this.

**Common mistake — ignoring worst case:** Saying "my algorithm is fast because it often finishes early" is not a complexity analysis — it is optimism. Worst case is what interviewers and production systems care about. Always answer worst case unless explicitly asked for average.

> [↑ Back to Top](#top)

<a id="3-big-o-notation"></a>
# 3. Big-O Notation

Think of Big-O as a speed label on a car. You do not care whether the car is red or blue, has leather seats or cloth — you care about its top speed class. Big-O works the same way: it strips away the small details and tells you the growth class of your algorithm.

It tells how time grows as input grows.

We ignore:
- small numbers
- constants
- small differences

We focus only on growth.

**Common mistake — faster hardware ≠ better algorithm:** Doubling CPU speed saves you at best 2x. Changing O(n²) to O(n log n) saves you 1000x at n=10,000. Hardware is a constant factor; Big-O strips constants away. Always fix the algorithm first.

> 📝 **Practice:** [Q1 — What Big-O measures](./practice.md#q1--big-o-definition--what-does-big-o-actually-measure-)

> [↑ Back to Top](#top)

<a id="4-common-time-complexities"></a>
# 4. Common Time Complexities

Each complexity class has a personality. Once you can picture them, you will recognize them instantly in any code.

<a id="o1-constant-time"></a>
## O(1) — Constant Time

Ravi opens first page of book. Doesn't matter if book has 10 pages or 1000 pages. Still 1 step.

```python
arr = [1, 2, 3]
print(arr[0])
```

Time does not change.

## Visual: The Microwave

You pull a pre-made sandwich out of the fridge and heat it.
Does it matter if 1 customer orders or 1000 customers ordered yesterday?
No. The time to heat one sandwich never changes.

```
Orders today: 1      → Time: 30 seconds
Orders today: 1000   → Time: 30 seconds (for this one sandwich)
Orders today: 1M     → Time: 30 seconds
```

Array lookup `arr[5]` is the microwave. The computer knows the address instantly.

> 📝 **Practice:** [Q2 — Identify all O(1) operations](./practice.md#q2--constant-time--identify-all-o1-operations-)

<a id="on-linear-time"></a>
## O(n) — Linear Time

Ravi checks every student in class to find Rahul. If there are n students, he checks n times.

```python
for num in arr:
    print(num)
```

## Visual: Cooking Burgers One by One

You have an order for n burgers. Each takes 3 minutes.
Double the burgers? Double the time. Simple, proportional.

```
n = 10   → 30 minutes
n = 20   → 60 minutes
n = 100  → 300 minutes
```

Linear search through an array is flipping burgers one by one.

> 📝 **Practice:** [Q3 — Linear time complexity](./practice.md#q3--linear-time--write-a-function-and-predict-its-complexity-)

<a id="on2-quadratic-time"></a>
## O(n²) — Quadratic Time

Ravi compares every student with every other student. If students = 10 → 100 comparisons. If students = 100 → 10,000. Danger grows fast.

```python
for i in students:
    for j in students:
        compare(i, j)
```

## Visual: The Party Icebreaker

You throw a party with n guests. Every person must meet every other person.
Double the guests — roughly 4x the introductions.

```
n = 10    →   ~100 pairs
n = 100   → ~10,000 pairs
n = 1000  → ~1,000,000 pairs
```

Bubble sort, selection sort, and most naive nested-loop algorithms live here.

> 📝 **Practice:** [Q4 — Spot O(n²) in nested loops](./practice.md#q4--quadratic-time--spot-on-in-nested-loops-)

<a id="olog-n-logarithmic-time"></a>
## O(log n) — Logarithmic Time

Ravi searches in a dictionary. He opens the middle. Eliminates half. Then half again.

```
1000 → 500 → 250 → 125 → 62 → ...
```

This is how **Binary Search** works.

## Visual: The Recipe Index

You have a giant recipe book sorted alphabetically. You want "Mushroom Risotto."
You open the middle, see you're in the M's, then narrow it down again.
Every step you cut the remaining search in half.

```
1000 pages    → ~10 steps  (2^10 = 1024)
1,000,000     → ~20 steps  (2^20 ≈ 1M)
1,000,000,000 → ~30 steps
```

Doubling the book adds just ONE more step. That is the magic of logarithms.

> 📝 **Practice:** [Q5 — Trace through binary search](./practice.md#q5--logarithmic-time--trace-through-binary-search-)

<a id="o2n-exponential-time"></a>
## O(2ⁿ) — Exponential Time

Imagine Ravi trying all combinations of passwords. Each extra character doubles the work.

This happens in:
- Recursion without optimization
- Backtracking
- Brute force combinations

## Visual: The Password Hacker

You are trying to crack a binary password of length n.
For each bit, it is either 0 or 1. The number of combinations is 2^n.

```
n = 10  →      1,024 combinations
n = 20  →  1,048,576 combinations
n = 30  →  1,073,741,824 combinations
```

Add ONE more bit — double the work. This explodes almost instantly.

> 📝 **Practice:** [Q14 — Why O(2ⁿ) is practically unusable](./practice.md#q14--exponential-growth--why-o2-is-practically-unusable-)

<a id="growth-comparison"></a>
## Growth Comparison

How fast does each complexity grow as n increases?

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

> [↑ Back to Top](#top)

<a id="5-how-to-calculate-time-complexity"></a>
# 5. How to Calculate Time Complexity

Calculating complexity is like weighing luggage at the airport. You do not weigh each sock individually — you weigh the suitcase. Similarly, you ignore tiny constant operations and focus on what scales with the input.

<a id="step-1-ignore-constants"></a>
## Step 1: Ignore Constants

```python
for i in range(100):
    print(i)
```

This is O(1) — because 100 is fixed, it does not grow with input.

<a id="step-2-focus-on-input-size"></a>
## Step 2: Focus on Input Size

```python
for i in range(n):
    print(i)
```

This is O(n) — scales linearly with input.

<a id="step-3-nested-loops-multiply"></a>
## Step 3: Nested Loops Multiply

```python
for i in range(n):
    for j in range(n):
        print(i, j)
```

O(n × n) = O(n²)

<a id="step-4-consecutive-loops-add"></a>
## Step 4: Consecutive Loops Add

```python
for i in range(n):
    print(i)

for j in range(n):
    print(j)
```

O(n + n) → O(n)

<a id="step-5-drop-lower-terms"></a>
## Step 5: Drop Lower Terms

```
O(n² + n + 5)
→ O(n²)
```

Only the biggest term matters.

**Common mistake — counting every line as a separate operation:** Each assignment `x = 5` is O(1). The total complexity is about how counts *scale* with n, not how many lines you wrote. Similarly, constants inside loops (doing 3 things per iteration vs 1) are irrelevant — drop them.

**Common mistake — forgetting nested loops multiply:** Two nested loops over n → O(n²), not O(2n). An outer loop over n with an inner loop over m → O(n×m). Parallel loops (sequential, not nested) *add*: O(n) + O(n) = O(n).

> 📝 **Practice:** [Q6 — Drop constants rule](./practice.md#q6--drop-constants--simplify-these-big-o-expressions-)

<a id="choosing-algorithm-by-input-size"></a>
## Choosing Algorithm by Input Size

In interviews and production, the question isn't just "what is the complexity?" —
it's "given the input size, will this actually run in time?"

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Input Size (n)  │  Max Complexity     │  Example Algorithm              │
├──────────────────┼─────────────────────┼─────────────────────────────────┤
│  n ≤ 10          │  O(n!)              │  Permutation brute force        │
│  n ≤ 20          │  O(2ⁿ)             │  Subset enumeration             │
│  n ≤ 100         │  O(n³)             │  Floyd-Warshall, 3-loop DP      │
│  n ≤ 1,000       │  O(n²)             │  Bubble sort, naive DP          │
│  n ≤ 100,000     │  O(n log n)        │  Merge sort, heap sort          │
│  n ≤ 10,000,000  │  O(n)              │  Linear scan, hash map          │
│  n > 10,000,000  │  O(log n) or O(1)  │  Binary search, lookup table    │
└──────────────────────────────────────────────────────────────────────────┘
```

Modern computers execute roughly 10⁸ to 10⁹ simple operations per second.

```
If n = 1,000,000 and your algorithm is O(n²):
  operations = (10⁶)² = 10¹² operations
  time ≈ 10¹² / 10⁸ = 10,000 seconds ≈ 2.7 hours

If n = 1,000,000 and your algorithm is O(n log n):
  operations = 10⁶ × 20 = 2 × 10⁷ operations
  time ≈ 2 × 10⁷ / 10⁸ = 0.2 seconds ✓
```

**The interview move:** When you see the constraints, immediately decide complexity.
- `n ≤ 10⁵` → O(n log n) is fine, O(n²) is not
- `n ≤ 10³` → O(n²) is acceptable
- `n ≤ 20` → exponential approaches are OK

> 📝 **Practice:** [Q17 — Pick the right algorithm from constraints](./practice.md#q17--input-size-constraints--pick-the-right-algorithm-from-constraints-)

> [↑ Back to Top](#top)

<a id="6-real-world-impact"></a>
# 6. Real-World Impact

Big-O is not an academic exercise. It is the difference between a system that hums along at a million users and one that collapses at 3am while your phone won't stop ringing.

<a id="database-index"></a>
## Database Index — O(n) vs O(log n)

Imagine you are a backend engineer at a mid-sized company. You have a `users` table with 1,000,000 rows. The user profile page is loading in 8 seconds. You look at the query:

```sql
SELECT * FROM users WHERE email = 'alice@example.com';
```

Without an index, the database does a **full table scan** — it reads every single row, one by one, checking whether the email matches. This is pure O(n).

```
Row 1:   alice123@example.com   → no match
Row 2:   bob@gmail.com          → no match
...
Row 487,293: alice@example.com  → MATCH
...
Row 1,000,000: last_user@...    → no match

Total reads: 1,000,000
```

When you add a database index on `email`, the database builds a **B-tree** — a balanced tree structure that allows binary-search-style lookups. The same query becomes O(log n).

```
B-Tree Index Lookup for 'alice@example.com'

Level 0 (root):    [m_______] → left half (a-m)
Level 1:           [g_______] → left half (a-g)
Level 2:           [c_______] → right half (c-g)
Level 3:           [e_______] → left half (c-e)
Level 4:           [al______] → found the leaf page

Total comparisons: ~20
(log₂(1,000,000) ≈ 20)
```

| Rows in Table | Full Scan O(n) | B-Tree O(log n) | Speedup    |
|---------------|----------------|-----------------|------------|
| 1,000         | 1,000 reads    | ~10 reads       | ~100x      |
| 10,000        | 10,000 reads   | ~13 reads       | ~770x      |
| 100,000       | 100,000 reads  | ~17 reads       | ~5,900x    |
| 1,000,000     | 1,000,000 reads| ~20 reads       | ~50,000x   |
| 10,000,000    | 10,000,000 reads| ~23 reads      | ~435,000x  |

At 10 million rows, a 435,000x speedup. The index query takes microseconds while the full scan takes minutes.

<a id="hidden-list-cost"></a>
## Hidden List Cost — list.insert(0) vs deque

A developer builds a queue of tasks using a Python list. She adds new tasks to the front using `list.insert(0, item)` in a loop. It works. Six months later, the task queue spikes to 50,000 items and the insert operations, which took microseconds at size 100, now take milliseconds each.

Why? Because `list.insert(0, item)` is **O(n)**.

Python's `list` is backed by a dynamic array — all elements stored contiguously in memory. To insert at position 0, every existing element must shift one position to the right:

```
Inserting 'X' at index 0 of [A, B, C, D, E]:

Before:  [A, B, C, D, E]
Step 1:  shift E right → [A, B, C, D, E, _]
Step 2:  shift D right → [A, B, C, D, _, E]
Step 3:  shift C right → [A, B, C, _, D, E]
Step 4:  shift B right → [A, B, _, C, D, E]
Step 5:  shift A right → [A, _, B, C, D, E]
Step 6:  place X at 0 → [X, A, B, C, D, E]

Total shifts = n (the entire list)
```

The fix: Python's `collections.deque` uses a doubly linked list of blocks. Appending to either end is **O(1) amortized**.

```
deque.appendleft('X'):

Before:  ... <-> [A] <-> [B] <-> [C] <-> ...
After:   ... <-> [X] <-> [A] <-> [B] <-> [C] <-> ...

O(1) always.
```

## Hidden Costs Cheat Sheet

```
Operation                   | Complexity | Common Mistake
-----------------------------------------------------------------
list.insert(0, x)           | O(n)       | Use deque.appendleft(x) instead
list.pop(0)                 | O(n)       | Use deque.popleft() instead
'x in list'                 | O(n)       | Use 'x in set' for O(1)
sorted(list)                | O(n log n) | Fine, but don't call inside a loop
list.index(x)               | O(n)       | Use dict for O(1) by-value lookup
list + list (concatenation) | O(n+m)     | Use extend() to avoid copy
set.add(x)                  | O(1)*      | *Amortized; rare O(n) on resize
dict[key]                   | O(1)*      | *Amortized
list.append(x)              | O(1)*      | *Amortized (dynamic array)
str + str (in a loop)       | O(n²)!     | Use ''.join(list_of_strings)
```

**Common mistake — string concatenation in loops:** `result = result + word` copies the entire existing string on each iteration. For 10,000 words that is roughly n²/2 = 50,000,000 character copies. Use `"".join(words)` instead — it copies each character exactly once.

<a id="amortized-append"></a>
## Amortized Append — Dynamic Array

You know that `list.append(x)` is O(1) amortized. But occasionally it is O(n). How can something be both?

The answer is **amortized analysis** — analyzing algorithms by looking at the total cost of a sequence of operations, not just individual ones.

Python's list is backed by a dynamic array. When the array is full and you append, it must allocate a new array of double the size and copy all existing elements. That copy is O(n). But doublings are rare:

```
Append 1:  [1]           capacity=1   → no copy needed
Append 2:  [1,2]         capacity=2   → resize! copy 1 element
Append 3:  [1,2,3]       capacity=4   → resize! copy 2 elements
Append 4:  [1,2,3,4]     capacity=4   → no resize
Append 5:  [1,...,5]     capacity=8   → resize! copy 4 elements
Append 6–8:              capacity=8   → no resize
Append 9:  [1,...,9]     capacity=16  → resize! copy 8 elements
Append 10–16:            capacity=16  → no resize
Append 17: [1,...,17]    capacity=32  → resize! copy 16 elements

Resize costs: 1, 2, 4, 8, 16 = 31 total copy operations for 17 appends
```

For n appends, total copy cost is `1 + 2 + 4 + ... + n/2 = n - 1`. That is O(n) total copy work. Divided by n appends: **O(1) amortized per append**.

Think of it like a savings account. Each cheap append (no resize) puts a coin in the bank. Each expensive append (with a resize) withdraws coins to pay for the copying. Because the array doubles each time, by the time you resize again you have twice as many saved coins as the resize will cost. The bank never goes negative.

> [↑ Back to Top](#top)

<a id="7-space-complexity"></a>
# 7. Space Complexity

Imagine Ravi packing for a trip. If he is going for 1 day, he packs 1 shirt. For 5 days, 5 shirts. For 100 days, 100 shirts. The suitcase grows with the trip length — that is O(n) space. But if he always wears the same outfit and washes it every night, he only needs 1 shirt no matter how long the trip — that is O(1) space.

```python
# O(n) space — stores n items
def create_list(n):
    arr = []
    for i in range(n):
        arr.append(i)
    return arr

# O(1) space — only a few variables regardless of input
def sum_two(a, b):
    return a + b
```

```
Space grows with input:

O(1):  [x]                    ← same size always
O(n):  [x, x, x, ..., x]     ← grows with n
O(n²): [[x,x,...], [x,x,...]] ← grows with n²
```

> 📝 **Practice:** [Q9 — Classify functions by space usage](./practice.md#q9--space-complexity--classify-these-by-space-usage-)

> [↑ Back to Top](#top)

<a id="8-recursion-and-stack-space"></a>
# 8. Recursion and Stack Space

Imagine a stack of plates in a cafeteria. Every time a function calls itself, Python adds a new plate to the stack. When the function returns, the plate is removed. If you call yourself 1000 times, you have 1000 plates stacked up — and Python's default limit is exactly 1000 before it crashes.

```python
def count(n):
    if n == 0:
        return
    count(n-1)
```

Call stack:

```
count(3)
count(2)
count(1)
count(0)
```

Stack grows → O(n) space

<a id="the-factorial-call-stack"></a>
## The Factorial Call Stack

Each recursive call adds a **stack frame** — local variables and return address — to the call stack.

```python
def factorial(n):
    if n == 0: return 1
    return n * factorial(n-1)   # each call adds a stack frame
```

```
|  factorial(0)  |  ← top of stack
|  factorial(1)  |
|  factorial(2)  |
|  factorial(3)  |
|  factorial(4)  |
|  factorial(5)  |  ← bottom (original call)
+────────────────+
```

Space complexity: O(n) — the stack depth equals the input n. If n = 100,000, you might get a stack overflow. Python's default recursion limit is 1,000. For problems where depth is O(n), consider an iterative solution.

**Common mistake — ignoring recursive call stack space:** "My function uses no arrays" does not mean O(1) space. Every recursive call consumes a stack frame. A recursive tree of depth n always costs O(n) space, even if each frame is tiny.

> 📝 **Practice:** [Q12 — Stack frames and space complexity](./practice.md#q12--recursion-space--stack-frames-and-space-complexity-)

> [↑ Back to Top](#top)

<a id="9-pattern-recognition"></a>
# 9. Pattern Recognition

After enough practice, complexity analysis becomes instant pattern matching. You see a code shape, you know the class. Like a chef who can tell if a dish needs salt just by smelling it — you will see a nested loop and immediately think "O(n²)."

| Pattern | Complexity |
|---------|------------|
| Single loop | O(n) |
| Nested loop | O(n²) |
| Halving input | O(log n) |
| Divide and conquer | O(n log n) |
| All subsets | O(2ⁿ) |
| All permutations | O(n!) |

<a id="how-to-think-like-a-problem-solver"></a>
## How to Think Like a Problem Solver

Always ask these six questions:

1. What grows?
2. How fast does it grow?
3. Can I reduce it?
4. Can I trade space for time?
5. Can I sort first?
6. Can I precompute?

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

> "Ravi…
> Correct code makes programs work.
> Efficient code makes engineers powerful."

| Concept | Key Takeaway |
|---------|-------------|
| Complexity Analysis | Measures how time/space grows with input size |
| Big-O | Worst-case growth rate, ignoring constants |
| O(1) | Constant — does not grow |
| O(log n) | Halving — grows very slowly |
| O(n) | Linear — proportional to input |
| O(n log n) | Efficient sorting — the sweet spot |
| O(n²) | Quadratic — nested loops, danger zone |
| O(2ⁿ) | Exponential — explodes, avoid if possible |
| Space complexity | Memory used — stack frames count |
| Amortized | Average cost per operation over many operations |

**Interview Roadmap:**

- **0–2 Years** — Master O(n), O(n²), O(log n). Identify nested loops. Understand best vs worst case.
- **3–5 Years** — Analyze recursive trees. Master amortized complexity. Understand space optimization.
- **FAANG Level** — Derive recurrence relations. Solve Master Theorem. Optimize exponential to polynomial.

**How to Revise:**

1. Take random code
2. Predict complexity
3. Increase input mentally
4. Visualize growth
5. Compare two solutions

Next level: Arrays — where data begins its journey.

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | *(first module — no previous)* |
| ➡ Next Module | [02_arrays → theory.md](../02_arrays/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[02 Arrays →](../02_arrays/theory.md) · [05 Sorting →](../05_sorting/theory.md) · [06 Searching →](../06_searching/theory.md)

**Jump to specific topics in other files:**
- Binary Search complexity → [06_searching § Binary Search](../06_searching/theory.md)
- Sorting algorithm complexities → [05_sorting § Comparison of Sorting Algorithms](../05_sorting/theory.md)
- Array operation costs → [02_arrays § Core Operations](../02_arrays/theory.md)

> [↑ Back to Top](#top)