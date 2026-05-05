# Complexity Analysis — Cheatsheet

## Big-O Quick Reference Table

```
+------------+----------------+-----------------------------+----------------------------+
| Notation   | Name           | Example                     | n=1000 ops (approx)        |
+------------+----------------+-----------------------------+----------------------------+
| O(1)       | Constant       | Hash lookup, array index    | 1                          |
| O(log n)   | Logarithmic    | Binary search, BST ops      | ~10                        |
| O(n)       | Linear         | Linear scan, one-pass loop  | 1,000                      |
| O(n log n) | Linearithmic   | Merge sort, heap sort       | ~10,000                    |
| O(n^2)     | Quadratic      | Bubble/insertion sort, BF   | 1,000,000                  |
| O(n^3)     | Cubic          | Floyd-Warshall, matrix mult | 1,000,000,000              |
| O(2^n)     | Exponential    | Subsets, brute-force recsn  | 10^301  (impossible)       |
| O(n!)      | Factorial      | Permutations, TSP brute     | 10^2568 (never)            |
+------------+----------------+-----------------------------+----------------------------+
```

## Complexity Growth Visual

```
Fast  |  O(1) -------- flat line
      |  O(log n) ---- barely climbs
      |  O(n) -------- diagonal
      |  O(n log n) -- slightly curved diagonal
      |  O(n^2) ------- steep curve
      |  O(2^n) -------- wall
Slow  |  O(n!) --------- vertical cliff
```

---

## Time Complexity Rules

```
RULE 1 — Drop constants
  O(2n) => O(n)    |    O(500) => O(1)    |    O(3n^2 + 10n) => O(n^2)

RULE 2 — Keep dominant term only
  O(n^2 + n) => O(n^2)    |    O(n log n + n) => O(n log n)

RULE 3 — Sequential steps ADD
  step1: O(n)  +  step2: O(m)  =  O(n + m)
  If m == n then O(2n) => O(n)

RULE 4 — Nested loops MULTIPLY
  for i in range(n):          # O(n)
      for j in range(n):      # O(n)
  => O(n^2)

  for i in range(n):          # O(n)
      for j in range(log n):  # O(log n)
  => O(n log n)

RULE 5 — Independent inputs stay separate
  O(n * m) — do NOT reduce if n and m are unrelated inputs
```

---

## Space Complexity Rules

```
Extra data structure:
  array of size n    => O(n)
  2D matrix n x n    => O(n^2)
  hash map n keys    => O(n)

Recursion stack depth:
  linear recursion   => O(n)  stack frames
  binary recursion   => O(log n) if balanced, O(n) worst
  (fibonacci naive)  => O(n)  stack depth

Input space (usually excluded from space complexity unless asked):
  "auxiliary space"  = extra space beyond input
```

---

## Python Built-in Operations — Complexity

```
+---------------------------+----------+----------------------------------------+
| Operation                 | Time     | Note                                   |
+---------------------------+----------+----------------------------------------+
| list[i]                   | O(1)     | random access                          |
| list.append(x)            | O(1)*    | amortized                              |
| list.pop()                | O(1)     | from end                               |
| list.pop(i)               | O(n)     | shifts elements                        |
| list.insert(i, x)         | O(n)     | shifts elements                        |
| list[i:j]                 | O(k)     | k = slice length, CREATES COPY         |
| list.sort()               | O(n log n)| TimSort, in-place                     |
| sorted(list)              | O(n log n)| returns new list                      |
| x in list                 | O(n)     | linear scan                            |
| len(list)                 | O(1)     | stored attribute                       |
+---------------------------+----------+----------------------------------------+
| dict[k]                   | O(1)*    | average; O(n) worst (rare)             |
| dict[k] = v               | O(1)*    | average                                |
| k in dict                 | O(1)*    | average                                |
| del dict[k]               | O(1)*    | average                                |
+---------------------------+----------+----------------------------------------+
| set.add(x)                | O(1)*    | average                                |
| x in set                  | O(1)*    | average                                |
| set.remove(x)             | O(1)*    | average                                |
| set1 | set2               | O(n+m)   | union                                  |
| set1 & set2               | O(min)   | intersection                           |
+---------------------------+----------+----------------------------------------+
| deque.appendleft(x)       | O(1)     | use deque, NOT list for left ops       |
| deque.popleft()           | O(1)     | list.pop(0) is O(n) — avoid it         |
+---------------------------+----------+----------------------------------------+
```

---

## Common Algorithm Complexities

```
+--------------------+----------------+-----------+---------------------------+
| Algorithm          | Time           | Space     | Notes                     |
+--------------------+----------------+-----------+---------------------------+
| Binary search      | O(log n)       | O(1)      | sorted array required     |
| Linear search      | O(n)           | O(1)      |                           |
| BFS                | O(V + E)       | O(V)      | queue-based               |
| DFS                | O(V + E)       | O(V)      | stack/recursion           |
| Dijkstra           | O((V+E) log V) | O(V)      | with min-heap             |
| Bellman-Ford       | O(V * E)       | O(V)      | handles negative edges    |
| Floyd-Warshall     | O(V^3)         | O(V^2)    | all-pairs shortest path   |
| Merge sort         | O(n log n)     | O(n)      | stable, extra space       |
| Quick sort         | O(n log n)*    | O(log n)  | O(n^2) worst case         |
| Heap sort          | O(n log n)     | O(1)      | not stable                |
| Counting sort      | O(n + k)       | O(k)      | k = value range           |
| Radix sort         | O(d * n)       | O(n + k)  | d = digit count           |
| BST search/insert  | O(log n)*      | O(1)      | O(n) worst if unbalanced  |
| AVL/RB tree ops    | O(log n)       | O(1)      | balanced guarantee        |
| Heap push/pop      | O(log n)       | O(1)      | heapify = O(n)            |
| Hash table ops     | O(1)*          | O(n)      | amortized average         |
| KMP search         | O(n + m)       | O(m)      | n=text, m=pattern         |
+--------------------+----------------+-----------+---------------------------+
```

---

## Master Theorem (Divide and Conquer)

```
T(n) = a * T(n/b) + O(n^d)

  a = number of subproblems
  b = factor by which input shrinks
  d = exponent of work done outside recursive calls

CASE 1: d < log_b(a)  =>  T(n) = O(n^log_b(a))   [recursion dominates]
CASE 2: d == log_b(a) =>  T(n) = O(n^d * log n)   [equal work at each level]
CASE 3: d > log_b(a)  =>  T(n) = O(n^d)           [top-level work dominates]

Examples:
  Merge sort: T(n) = 2T(n/2) + O(n)  => a=2,b=2,d=1 => log_2(2)=1=d => O(n log n)
  Binary search: T(n) = T(n/2) + O(1) => a=1,b=2,d=0 => log_2(1)=0=d => O(log n)
  Naive matrix mult: T(n) = 8T(n/2) + O(n^2) => log_2(8)=3 > 2 => O(n^3)
```

---

## Recognizing Complexity from Code Patterns

```
O(1)       — no loop, direct index/hash access
O(log n)   — input halved each iteration: while lo <= hi: mid = (lo+hi)//2
O(n)       — single loop over input
O(n log n) — sort + single pass; divide-and-conquer with O(n) merge
O(n^2)     — nested loop both over n; comparing all pairs
O(2^n)     — generating all subsets; recursive calls branch factor 2
O(n!)      — generating all permutations; branching factor decreases by 1

HALVING TRICK — if you see any of these, think O(log n):
  mid = (lo + hi) // 2
  n = n // 2
  n >>= 1
  while n > 1: n //= base
```

---

## Interview Script — What To Say

```
When asked "What's the time complexity?":
  1. Identify the dominant loop structure
  2. State: "This is O(__) time and O(__) space"
  3. Justify: "because we iterate over n elements once / we use a hash map
     of size n / the recursion depth is log n..."
  4. Mention best/average/worst if they differ (e.g., quick sort)

When asked "Can you do better?":
  - O(n^2) -> try two pointers or hash map for O(n)
  - O(n) -> check if O(log n) is possible with binary search
  - O(n log n) sort -> check if counting sort / radix sort gives O(n)
  - Already O(n) -> lower bound is often O(n) if you must read input

Amortized vs worst-case — always clarify:
  "list.append is O(1) amortized, O(n) worst case due to resize"
```

---

## Gotchas / Traps

```
- list.pop(0) is O(n) — use collections.deque for O(1) popleft
- list slicing [i:j] creates a COPY — O(k) time AND space
- 'x in list' is O(n) — convert to set for O(1) membership checks
- Recursion in Python has default limit of 1000 frames (sys.setrecursionlimit)
- dict/set are O(1) AVERAGE — worst case O(n) with hash collisions (rare)
- String concatenation in a loop: s += c is O(n^2) total — use list + ''.join()
- sorted() on dict returns sorted keys, not items
- Nested list comprehension complexity: [x for row in matrix for x in row] = O(n*m)
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Visual Explanation](./visual_explanation.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
