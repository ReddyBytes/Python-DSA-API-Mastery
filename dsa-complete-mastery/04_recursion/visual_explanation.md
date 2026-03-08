# Recursion — Visual Explanation

A collection of ASCII diagrams and step-by-step walkthroughs to build an
intuition for how recursion works, what it costs, and how to reason about it.

---

## 1. The Call Stack Model

Every function call pushes a **stack frame** onto the call stack. When the
function returns, its frame is popped. Recursion means a function pushes
multiple frames before any of them pop.

### factorial(4) — growing and shrinking

```
PHASE 1: CALLS ARE PUSHED (stack grows downward)

  [factorial(4)]  n=4  ← top of stack (most recent call)
  [factorial(3)]  n=3
  [factorial(2)]  n=2
  [factorial(1)]  n=1  ← base case hit, starts returning


PHASE 2: RETURNS ARE POPPED (stack shrinks upward)

  factorial(1) returns 1
  factorial(2) gets 1, computes 2*1=2, returns 2
  factorial(3) gets 2, computes 3*2=6, returns 6
  factorial(4) gets 6, computes 4*6=24, returns 24
```

### Tree view of the same execution

```
CALL factorial(4)                        ─── returns 24
├── CALL factorial(3)                    ─── returns 6
│   ├── CALL factorial(2)               ─── returns 2
│   │   ├── CALL factorial(1)           ─── returns 1
│   │   │   └── BASE CASE: n==1, return 1
│   │   └── computes 2 * 1 = 2
│   └── computes 3 * 2 = 6
└── computes 4 * 6 = 24
```

### Stack frame contents at peak depth

```
┌─────────────────────┐  ← top (most recent)
│  factorial(1)       │  n=1, waiting to return 1
├─────────────────────┤
│  factorial(2)       │  n=2, waiting for factorial(1)
├─────────────────────┤
│  factorial(3)       │  n=3, waiting for factorial(2)
├─────────────────────┤
│  factorial(4)       │  n=4, waiting for factorial(3)
├─────────────────────┤
│  main()             │  the original caller
└─────────────────────┘  ← bottom (oldest frame)
```

Space complexity = O(n) because n frames live on the stack simultaneously.

---

## 2. Recursion Tree for Fibonacci — Seeing Duplicate Work

```python
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
```

### fib(5) full tree

```
                        fib(5)
                       /      \
                  fib(4)        fib(3)*
                 /      \       /     \
            fib(3)*    fib(2)^ fib(2)^ fib(1)
            /    \     /   \
        fib(2)^ fib(1) fib(1) fib(0)
        /    \
    fib(1)  fib(0)

  * = called TWICE (duplicate subtree)
  ^ = called THREE times total
```

### Counting the calls

```
fib(5)  called: 1
fib(4)  called: 1
fib(3)  called: 2   ← duplicate!
fib(2)  called: 3   ← triplicate!
fib(1)  called: 5
fib(0)  called: 3
─────────────────
Total:  15 calls to compute fib(5)

Without memoization: T(n) = T(n-1) + T(n-2) + O(1)  ≈  O(2^n)
With memoization:    T(n) = O(n)    (each subproblem solved once)
```

### Side-by-side comparison

```
WITHOUT MEMO          WITH MEMO
O(2^n) calls          O(n) calls

fib(5)                fib(5)
├── fib(4)            ├── fib(4)
│   ├── fib(3)        │   ├── fib(3)
│   │   ├── fib(2)    │   │   ├── fib(2)
│   │   │   ├─ fib(1) │   │   │   ├─ fib(1) → 1
│   │   │   └─ fib(0) │   │   │   └─ fib(0) → 0
│   │   └── fib(1)    │   │   └─ fib(1) → 1 (cached)
│   └── fib(3)        │   └─ fib(3) → 2 (cached)
│       ├── fib(2)    └── fib(3) → 2 (cached)
│       │   ├─ fib(1)
│       │   └─ fib(0)
│       └── fib(1)
└── fib(3)  (again!)
    └── ... (entire subtree repeated)
```

---

## 3. Recursion as Telescoping — The Problem Shrinks Each Call

Think of nested Russian dolls (Matryoshka). To open the outermost doll you
must first open the one inside it, and so on until you reach the smallest doll
that has nothing inside (the base case).

```
PROBLEM SIZE n=5

 ╔═══════════════════════════╗
 ║  solve(5)                 ║
 ║  ╔═══════════════════╗    ║
 ║  ║  solve(4)         ║    ║
 ║  ║  ╔═══════════╗    ║    ║
 ║  ║  ║  solve(3) ║    ║    ║
 ║  ║  ║  ╔═════╗  ║    ║    ║
 ║  ║  ║  ║ s(2)║  ║    ║    ║
 ║  ║  ║  ║ ╔═╗ ║  ║    ║    ║
 ║  ║  ║  ║ ║1║ ║  ║    ║    ║
 ║  ║  ║  ║ ╚═╝ ║  ║    ║    ║
 ║  ║  ║  ╚═════╝  ║    ║    ║
 ║  ║  ╚═══════════╝    ║    ║
 ║  ╚═══════════════════╝    ║
 ╚═══════════════════════════╝

Each shell represents one stack frame.
The innermost shell is the base case.
Results bubble OUT from the center.
```

The key insight: **trust that solve(n-1) already works, and build solve(n) on top of it**.

---

## 4. Divide and Conquer — Merge Sort Visualized

```
SPLIT PHASE (top-down)

[5, 3, 8, 1, 9, 2, 7, 4]
         /          \
  [5, 3, 8, 1]   [9, 2, 7, 4]
    /      \        /      \
 [5, 3]  [8, 1]  [9, 2]  [7, 4]
  / \     / \     / \     / \
 [5][3]  [8][1]  [9][2]  [7][4]
          ↑ base cases (size 1)

MERGE PHASE (bottom-up)

 [5][3]  [8][1]  [9][2]  [7][4]
   ↓       ↓       ↓       ↓
 [3,5]  [1,8]  [2,9]  [4,7]
     \   /         \   /
  [1,3,5,8]     [2,4,7,9]
         \         /
     [1,2,3,4,5,7,8,9]
```

Each merge step does O(n) work across all calls at that level, and there are
O(log n) levels, giving T(n) = O(n log n).

---

## 5. Tree Recursion vs Linear Recursion — Shape Comparison

### Linear recursion (e.g., factorial)

```
factorial(5)
    │
factorial(4)
    │
factorial(3)
    │
factorial(2)
    │
factorial(1)   ← base case

Shape: a straight line
Depth: O(n)
Calls: O(n)
```

### Binary tree recursion (e.g., Fibonacci)

```
              fib(5)
            /        \
        fib(4)        fib(3)
        /    \        /    \
    fib(3)  fib(2) fib(2) fib(1)
    / \      / \    / \
  ...  ... ...  ... ...

Shape: a binary tree
Depth:  O(n)
Calls:  O(2^n)   ← exponential blowup
```

### Divide-and-conquer (e.g., merge sort)

```
          mergeSort([8 elements])
          /                     \
 mergeSort([4])         mergeSort([4])
   /        \             /        \
ms([2])  ms([2])      ms([2])   ms([2])
  / \      / \          / \       / \
ms  ms   ms  ms       ms  ms    ms  ms

Shape: a balanced binary tree
Depth: O(log n)
Calls: O(n)      ← efficient!
```

---

## 6. Tail Recursion — How It Can Become a Loop

A function is **tail-recursive** when the recursive call is the very last
operation — there is no pending computation after it returns.

### Non-tail-recursive factorial

```python
def factorial(n):
    if n == 1: return 1
    return n * factorial(n-1)   # ← multiplication PENDING after call returns
                                 #   must keep frame on stack
```

### Tail-recursive factorial (accumulator pattern)

```python
def factorial(n, acc=1):
    if n == 1: return acc
    return factorial(n-1, acc * n)   # ← nothing pending, frame can be reused
```

### Stack behaviour side-by-side

```
NON-TAIL                         TAIL (with TCO)

[fact(4)]  n=4, pending *4       [fact(4, acc=1)]   → reuse frame
[fact(3)]  n=3, pending *3       [fact(3, acc=4)]   → reuse frame
[fact(2)]  n=2, pending *2       [fact(2, acc=12)]  → reuse frame
[fact(1)]  n=1, returns 1        [fact(1, acc=24)]  → returns 24

Stack depth: O(n)                Stack depth: O(1)  (constant!)
```

### Equivalent iterative loop (what the compiler emits with TCO)

```python
def factorial_iter(n):
    acc = 1
    while n > 1:
        acc *= n
        n  -= 1
    return acc
```

Note: CPython does NOT perform TCO. Use iteration explicitly in Python.

---

## 7. Common Recursion Shapes and Their Complexities

### Shape 1 — Linear: T(n) = T(n-1) + O(1)

```
Call 1 ──► Call 2 ──► Call 3 ──► ... ──► Call n ──► BASE

Work per level: O(1)
Number of levels: n
Total: O(n)
```

Examples: factorial, linked-list traversal, reverse a string

### Shape 2 — Linear with O(n) work: T(n) = T(n-1) + O(n)

```
Call 1 ████████████████████  (n work)
  Call 2 ████████████████    (n-1 work)
    Call 3 ██████████████    (n-2 work)
      ...
        Call n █             (1 work)

Total: n + (n-1) + ... + 1 = O(n²)
```

Examples: insertion sort (recursive), bubble sort (recursive)

### Shape 3 — Divide and conquer: T(n) = 2T(n/2) + O(n)

```
Level 0:  [────────── n work ──────────]
Level 1:  [─── n/2 ───][─── n/2 ───]
Level 2:  [n/4][n/4][n/4][n/4]
...
Level log(n): n leaves of O(1)

Work per level: O(n)   (spreads across all calls)
Number of levels: O(log n)
Total: O(n log n)       ← Master Theorem Case 2
```

Examples: merge sort, closest pair of points

### Shape 4 — Exponential: T(n) = 2T(n-1) + O(1)

```
Level 0:        ●              (1 call)
Level 1:      ●   ●            (2 calls)
Level 2:    ● ● ● ●            (4 calls)
Level 3:  ●●●●●●●●             (8 calls)
...
Level n:  2^n leaves

Total calls: 1 + 2 + 4 + ... + 2^n = O(2^n)
```

Examples: naive Fibonacci, brute-force subsets, Tower of Hanoi

### Master Theorem quick reference

```
T(n) = aT(n/b) + f(n)

Let  c = log_b(a)

Case 1:  f(n) = O(n^(c-ε))    → T(n) = Θ(n^c)
Case 2:  f(n) = Θ(n^c)        → T(n) = Θ(n^c · log n)
Case 3:  f(n) = Ω(n^(c+ε))    → T(n) = Θ(f(n))

Merge sort: a=2, b=2, c=1, f(n)=n  → Case 2 → O(n log n)
Binary search: a=1, b=2, c=0, f(n)=1 → Case 2 → O(log n)
```

---

## Summary Cheat-Sheet

```
Pattern               Recurrence             Complexity
─────────────────────────────────────────────────────────
Linear work           T(n) = T(n-1) + O(1)   O(n)
Linear + linear work  T(n) = T(n-1) + O(n)   O(n²)
Binary divide         T(n) = 2T(n/2) + O(n)  O(n log n)
Binary divide cheap   T(n) = 2T(n/2) + O(1)  O(n)
Exponential branches  T(n) = 2T(n-1) + O(1)  O(2^n)
```

The diagram to keep in mind:

```
             PROBLEM(n)
            /           \
   PROBLEM(n/2 or n-1)  ...
        |
   smaller and smaller
        |
    BASE CASE
        ↓
   answers bubble back up
```

Recursion is nothing more than **trusting your past self**: assume the smaller
problem is already solved, write the one step that connects size n to size n-1,
and define what "done" looks like. The call stack handles the rest.
