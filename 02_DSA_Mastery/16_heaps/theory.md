<a id="top"></a>
# Heaps — The Structure of Priority

> A heap is not about sorting everything.
>
> It is about knowing the most important element instantly.
>
> If BST organizes everything,
> Heap focuses only on the top priority.

Heaps power:

- Priority queues
- Scheduling systems
- Dijkstra's algorithm
- Top K problems
- System resource management

Heaps are extremely important in interviews.

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is a Heap?](#1-real-life-story)
  - [Visual: The Hospital ER](#visual-hospital-er)
- [2. Complete Binary Tree](#3-complete-binary-tree)
- [3. Heap Property](#4-heap-property)
  - [Min Heap](#min-heap)
  - [Max Heap](#max-heap)
- [4. Heap Stored as Array](#5-heap-stored-as-array)
  - [Visual: The Array Mapping](#visual-array-mapping)
- [5. Insert — Bubble Up](#6-insert-in-heap)
  - [Visual: Step-by-Step Bubble Up](#visual-bubble-up)
- [6. Delete — Bubble Down](#7-delete-from-heap)
  - [Visual: Step-by-Step Extract Min](#visual-extract-min)
- [7. Heapify — Build Heap Efficiently](#8-heapify)
- [8. Heaps in Python](#10-heaps-in-python)
- [9. Common Interview Patterns](#11-common-interview-patterns)
  - [Visual: Top K Problem](#visual-top-k)
  - [Visual: Two Heaps for Running Median](#visual-two-heaps)
- [10. Heap vs BST](#12-heap-vs-bst)
- [🔥 Summary](#summary)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
heap property · complete binary tree · bubble up/down · Python heapq module

**Should Learn** — Important for real projects, comes up regularly:
heapify · heap sort · k-th largest/smallest patterns

**Good to Know** — Useful in specific situations, not always tested:
heap vs BST trade-offs · array storage indexing

**Reference** — Know it exists, look up syntax when needed:
D-ary heaps · Fibonacci heaps · binomial heaps

Otto is a triage nurse in a hospital emergency room. Every few minutes, a new patient walks in. Otto does not care who arrived first — he cares who is most critical. His job: always know the most urgent patient instantly, even as new people keep arriving and treated patients keep leaving. He needs a system that gives him O(1) access to the highest priority patient and O(log n) updates when patients arrive or are treated. That system is a **heap** — the data structure of priority.

<a id="1-real-life-story"></a>
# 1. What Is a Heap?

Otto starts his shift. He explains to a new resident: "A heap answers one question with blazing speed: what is the most important thing RIGHT NOW? Not second most important. Not a sorted list. Just: what's next?"

## Visual: The Hospital ER — A Better Analogy

Picture a hospital emergency room on a busy Saturday night.

The old way: first come, first served. A guy with a paper cut walked in at 9pm. A woman having a heart attack walked in at 9:05pm. By the rules, paper cut goes first.

Obviously, that's insane.

So hospitals invented **triage**. Every patient gets a priority number. 1 = critical. 10 = "you're fine, sit down." The sickest person always goes next, no matter who arrived when.

That's a heap. That's all it is.

A heap answers one question with blazing speed:

> "What's the most important thing right now?"

Not second most important. Not a sorted list. Just: **what's next?**

```
Arrival order:          Priority:
─────────────────────────────────────
1. Bob (sprained ankle)     7
2. Alice (chest pain)       2
3. Carol (broken arm)       5
4. Dave (stroke symptoms)   1
5. Eve (bad headache)       4
```

In a regular queue (FIFO), the order of treatment would be:
Bob → Alice → Carol → Dave → Eve

In a min-heap (priority queue), the order is:
Dave(1) → Alice(2) → Eve(4) → Carol(5) → Bob(7)

Dave gets seen immediately even though he arrived 4th.
Bob waits even though he arrived 1st.

The heap is constantly asking: **"Among everyone here, who needs help most?"**

> [↑ Back to Top](#top)

<a id="2-what-is-a-heap"></a>
# 2. Heap Definition

Otto formalizes the structure: a heap is a complete binary tree where the root is always the min (or max). It is not fully sorted — only the top is guaranteed. That limited guarantee is exactly what makes it fast.

> 📝 **Practice:** [Q1 · min-heap property](./practice.md#q1--min-heap-property-check) · [Q2 · max-heap property](./practice.md#q2--max-heap-property-check)

A heap is:

A complete binary tree that satisfies heap property.

Two types:

- Min Heap
- Max Heap

> [↑ Back to Top](#top)

<a id="3-complete-binary-tree"></a>
# 3. Complete Binary Tree (Very Important)

Otto's triage system has one structural rule: patients fill seats from left to right, level by level, with no gaps. This completeness guarantee is what allows the heap to be stored in a simple array — no pointers needed.

- All levels filled
- Last level filled from left to right

Example:

```
        10
       /  \
     20    30
    /  \
  40   50
```

Valid complete tree.

But this is NOT complete:

```
        10
       /  \
     20    30
           /
         40
```

Because left child missing.

Completeness is mandatory.

**Common mistake — forgetting completeness:** A tree where the last level fills from right instead of left is not a valid heap structure. Always fill left-to-right on the bottom level, or the array indexing formulas break.

> [↑ Back to Top](#top)

<a id="4-heap-property"></a>
# 4. Heap Property

> 📝 **Practice:** [Q40 · heap-property](../dsa_practice_questions_100.md#q40--normal--heap-property)

## Min Heap

Parent ≤ children.

Smallest element at root.

## Max Heap

Parent ≥ children.

Largest element at root.

Example Min Heap:

```
        2
       / \
      5   8
     / \
    10 12
```

Root always smallest.

**Common mistake — confusing heap with sorted structure:** A heap is NOT a sorted array. In a min-heap, the root is the minimum, but the rest of the elements have no guaranteed order beyond the parent-child relationship. `heap[1]` is not necessarily the second smallest.

> [↑ Back to Top](#top)

<a id="5-heap-stored-as-array"></a>
# 5. Heap Stored as Array

> 📝 **Practice:** [Q3 · push and pop](./practice.md#q3--heapq-push-and-pop) · [Q4 · heapify](./practice.md#q4--heapq-heapify--on-batch-build)

Very important:

Heap is stored in array.

No pointers needed.

If index = i

Left child = 2i + 1
Right child = 2i + 2
Parent = (i - 1) // 2

This works because tree is complete.

Efficient memory usage.

## Visual: The Array Mapping

Here's where it gets cool. A heap looks like a tree when you draw it:

```
                 1
               /   \
              3     5
             / \   / \
            7   9 8   6
```

But it lives in a plain array:

```
Index:  [ 0   1   2   3   4   5   6 ]
Value:  [ 1   3   5   7   9   8   6 ]
```

The mapping is pure math. No pointers needed.

```
For any node at index i:
┌─────────────────────────────────────┐
│  Left child  → index  2i + 1        │
│  Right child → index  2i + 2        │
│  Parent      → index  (i - 1) // 2  │
└─────────────────────────────────────┘
```

Let's verify with the root's children:
- Root is at index 0
- Left child:  2(0)+1 = 1  → value 3  ✓
- Right child: 2(0)+2 = 2  → value 5  ✓

Let's check node 7 (index 3):
- Parent: (3-1)//2 = 1  → value 3  ✓  (3 is above 7 in the tree)

This is why heaps are so cache-friendly. It's just a contiguous block of memory.
No tree node objects. No pointers chasing each other around RAM.

**Common mistake — incorrect index calculations:** Off-by-one errors in index math (using `2i` instead of `2i+1` for left child, or `i // 2` instead of `(i-1) // 2` for parent in 0-based arrays) silently corrupt heap operations. Always double-check with a small example before coding.

> [↑ Back to Top](#top)

<a id="6-insert-in-heap"></a>
# 6. Insert in Heap (Bubble Up)

Steps:

1. Insert at end.
2. Compare with parent.
3. Swap if heap property violated.
4. Continue upward.

Example:

Insert 1 in min heap:

```
        2
       / \
      5   8
```

Insert at end:

```
        2
       / \
      5   8
     /
    1
```

Bubble up:

Swap with 5.

Swap with 2.

New root = 1.

Time:
O(log n)

Because height ≈ log n.

## Visual: Step-by-Step Bubble Up

A new patient walks in: Frank, priority 2 (second-most critical).

**Step 1:** Frank is placed at the end of the array (the "bottom" of the tree).

```
Before:
                 1
               /   \
              3     5
             / \   / \
            7   9 8   6

Array: [1, 3, 5, 7, 9, 8, 6]

After appending Frank (priority 2) at index 7:

                 1
               /   \
              3     5
             / \   / \
            7   9 8   6
           /
          2  ← Frank just arrived here

Array: [1, 3, 5, 7, 9, 8, 6, 2]
```

Frank (2) is smaller than his parent at index (7-1)//2 = 3, which is 7. The heap property is violated.

**Step 2:** Bubble up. Compare Frank to his parent. If Frank is smaller, swap.

```
Frank (2) vs Parent (7) → Frank wins! Swap.

                 1
               /   \
              3     5
             / \   / \
            2   9 8   6
           /
          7

Array: [1, 3, 5, 2, 9, 8, 6, 7]
```

Frank is now at index 3. His new parent is at index (3-1)//2 = 1, which is 3.

**Step 3:** Compare Frank (2) to parent (3). Frank is still smaller. Swap again.

```
Frank (2) vs Parent (3) → Frank wins! Swap.

                 1
               /   \
              2     5
             / \   / \
            3   9 8   6
           /
          7

Array: [1, 2, 5, 3, 9, 8, 6, 7]
```

Frank is now at index 1. His parent is the root at index 0, value 1.

**Step 4:** Compare Frank (2) to root (1). Root wins. Stop.

```
Final state:
                 1
               /   \
              2     5
             / \   / \
            3   9 8   6
           /
          7

Array: [1, 2, 5, 3, 9, 8, 6, 7]
```

Frank found his place. The heap property is restored.

> [↑ Back to Top](#top)

<a id="7-delete-from-heap"></a>
# 7. Delete from Heap (Bubble Down)

Remove root.

Replace with last element.

Heapify downward.

Example:

Remove 2 from:

```
        2
       / \
      5   8
```

Replace with 8:

```
        8
       /
      5
```

Bubble down:

Swap with smaller child.

Time:
O(log n)

## Visual: Step-by-Step Extract Min (Heapify Down)

Dave (priority 1, root) gets called in. We need to remove the root.

**Step 1:** Swap the root with the LAST element. Then remove the last element.

```
Before:
                 1   ← Dave leaves
               /   \
              2     5
             / \   / \
            3   9 8   6
           /
          7

Swap root (1) with last element (7):

                 7   ← now temporarily at root
               /   \
              2     5
             / \   / \
            3   9 8   6

Array: [7, 2, 5, 3, 9, 8, 6]   (1 is removed)
```

**Step 2:** Heapify down. 7 is at the root but is bigger than both its children (2 and 5). Find the smaller child and swap.

```
7 vs children: left=2, right=5. Smaller child is 2. Swap 7 and 2.

                 2
               /   \
              7     5
             / \   / \
            3   9 8   6

Array: [2, 7, 5, 3, 9, 8, 6]
```

**Step 3:** 7 is now at index 1. Its children: left=3 (index 3), right=9 (index 4). Smaller child is 3. 7 > 3, so swap.

```
                 2
               /   \
              3     5
             / \   / \
            7   9 8   6

Array: [2, 3, 5, 7, 9, 8, 6]
```

**Step 4:** 7 is at index 3. Its children would be at index 7 and 8 — beyond the array. 7 is a leaf. Stop.

The heap is restored. The new minimum (2) is at the root, ready to serve next.

**Common mistake — heap[0] vs heappop():** `heap[0]` is O(1) peek without removing. `heappop()` is O(log n) and removes the minimum. Using `heappop()` when you only want to look causes silent logic bugs (and infinite loops if you rely on the element still being there). Use `heap[0]` to inspect, `heappop()` to consume.

> [↑ Back to Top](#top)

<a id="8-heapify"></a>
# 8. Heapify (Build Heap Efficiently)

> 📝 **Practice:** [Q4 · heapify O(n)](./practice.md#q4--heapq-heapify--on-batch-build) · [Q20 · heapify in loop mistake](./practice.md#q20--heapify-in-loop--on-mistake)

Given array:

Build heap in O(n).

Start from last non-leaf node.
Heapify downward.

Important insight:

Heapify is O(n), not O(n log n).

This surprises many.

**Common mistake — calling heapify() on streaming data:** `heapify()` runs O(n) on a list that is already fully populated. Calling `heapify()` inside a loop after each new element does O(n) work every iteration — total cost O(n²) instead of O(n log n). For streaming data, always use `heappush()`.

```
heapify(list)          O(n)        Use when ALL elements are already in a list
heappush(heap, item)   O(log n)    Use when elements arrive one at a time (streaming)

Building from scratch with n pushes = O(n log n)
Building with heapify on complete list = O(n)

If you have the data: heapify is 2-3x faster in practice.
If data streams in: heappush is the only correct option.
```

> [↑ Back to Top](#top)

<a id="9-why-heap-is-powerful"></a>
# 9. Why Heap Is Powerful

Operations:

Insert → O(log n)
Delete → O(log n)
Peek → O(1)

Always know min or max instantly.

That's powerful.

## Visual: Quick Reference

```
┌──────────────────────────────────────────────────────────┐
│  HEAP CHEAT SHEET                                        │
├──────────────────────────────────────────────────────────┤
│  Structure:  Complete binary tree stored as array        │
│  Property:   Parent ≤ children (min-heap)                │
│                                                          │
│  Operations:                                             │
│    insert(val)      → O(log n)   heapify up              │
│    extract_min()    → O(log n)   heapify down            │
│    peek_min()       → O(1)       just look at index 0    │
│    heapify(array)   → O(n)       build from scratch      │
│                                                          │
│  Index math (0-based):                                   │
│    left  = 2i + 1                                        │
│    right = 2i + 2                                        │
│    parent = (i - 1) // 2                                 │
│                                                          │
│  Classic patterns:                                       │
│    Top K elements      → min-heap of size K              │
│    K closest points    → max-heap of size K              │
│    Running median      → two heaps                       │
│    Merge K sorted      → min-heap of K elements          │
│    Task scheduler      → max-heap of frequencies         │
└──────────────────────────────────────────────────────────┘
```

> [↑ Back to Top](#top)

<a id="10-heaps-in-python"></a>
# 10. Heaps in Python

> 📝 **Practice:** [Q3 · push/pop](./practice.md#q3--heapq-push-and-pop) · [Q5 · nlargest/nsmallest](./practice.md#q5--nlargest-and-nsmallest) · [Q6 · max-heap negation](./practice.md#q6--max-heap-via-negation) · [Q7 · peek](./practice.md#q7--peek-without-popping--heap0)

Python provides:

```python
import heapq

heap = []
heapq.heappush(heap, 5)
heapq.heappop(heap)
```

Python has min heap by default.

For max heap:
Insert negative values.

**Common mistake — Python heapq is min-heap only:** Using `heapq` directly for "find K largest elements" gives you the K smallest instead. You must negate values to simulate a max-heap. Common pattern: `heappush(heap, (-priority, item))` for priority queues. Negate on push, negate again on pop.

```python
import heapq

# Wrong: gives smallest, not largest
def k_largest_wrong(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, num)    # BUG: min-heap
    return [heapq.heappop(heap) for _ in range(k)]  # pops smallest

# Correct: negate for max-heap behavior
def k_largest_negate(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, -num)   # store negated
    return [-heapq.heappop(heap) for _ in range(k)]  # negate back
```

**Common mistake — tuple TypeError on equal priorities:** When two tuples have equal first elements, Python compares the second element. If the second element is a custom object (dict, custom class), Python raises `TypeError: '<' not supported`. Fix: add a unique counter as a tiebreaker.

```python
import heapq, itertools

counter = itertools.count()   # unique, always-increasing integer
heap = []

# Safe pattern: (priority, unique_count, item)
# count is always unique — Python never needs to compare item
heapq.heappush(heap, (priority, next(counter), item))
```

> [↑ Back to Top](#top)

<a id="11-common-interview-patterns"></a>
# 11. Common Interview Patterns

> 📝 **Practice:** [Q9 · kth largest](./practice.md#q9--kth-largest-element) · [Q11 · top-K](./practice.md#q11--top-k-largest-elements) · [Q13 · merge K sorted](./practice.md#q13--merge-k-sorted-lists) · [Q21 · median stream](./practice.md#q21--median-of-data-stream--two-heaps) · [Q15 · task scheduler](./practice.md#q15--task-scheduler-with-cooldown)

Heaps are used in:

- Top K elements
- Kth largest element
- Merge k sorted lists
- Median of stream
- Dijkstra's shortest path
- Task scheduling
- Priority queues

Very common in medium-hard interviews.

## Visual: Top K Problem — "Find the 5 Most Critical Patients from 1 Million Records"

Imagine you have 1,000,000 patients in a database. You need the 5 most critical.

**Bad approach:** Sort all 1 million. O(n log n). Slow. Wastes work on elements you'll never use.

**Heap approach:** Keep a min-heap of size K=5.

The trick is counterintuitive at first: to find the TOP 5 (highest priority), use a MIN-heap of size 5. The min-heap's root is the least important of your current top-5 candidates.

Why? Because you want to quickly ask: "Is this new person MORE important than the least important person in my current top-5?" If yes, kick the weakest out, insert the new one.

```
Start: heap is empty. Process first 5 patients.

Patients:  [7, 2, 5, 3, 9]  (priority numbers — lower is more urgent)

After inserting all 5:
         2
        / \
       3   5
      / \
     7   9

Heap (top-5 so far): min=2
```

Now a new patient arrives: priority 1 (extremely critical).

```
New patient: 1
Is 1 < heap's min (2)? YES.
→ Pop 2 from heap, insert 1.

         1
        / \
       3   5
      / \
     7   9
```

New patient: priority 8. Is 8 < heap's min (1)? No. Ignore.

After all 1 million patients: heap contains exactly the 5 most critical, and we only ever stored 5 elements in memory at once.

**Time:** O(n log k) where k=5. For n=1,000,000 and k=5, that's ~8x faster than sorting.

**Common mistake — max-heap for top-K streaming:** Using a max-heap for top-K requires storing ALL n elements before extracting. A min-heap of size K processes each element in O(log k) and never stores more than K elements. Use `heapreplace` instead of pop+push for efficiency.

```python
import heapq

def top_k_min_heap_correct(stream, k):
    heap = []
    for item in stream:
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)  # faster than pop+push
    return sorted(heap, reverse=True)
    # Space: O(k)   Time: O(n log k)
```

## Visual: Two Heaps for Running Median

Your hospital wants to track the median patient priority at all times as new patients arrive.

The median is the middle value. Split patients into two halves:
- Lower half (smaller priorities) — store in a **max-heap** (biggest of the small ones at top)
- Upper half (larger priorities) — store in a **min-heap** (smallest of the big ones at top)

```
Patients so far (sorted): [1, 2, 3, | 5, 7, 8, 9]
                                     ↑ median boundary

Max-heap (lower half):    Min-heap (upper half):
        3                       5
       / \                     / \
      2   1                   7   8
                              /
                             9

Lower half tops out at 3.   Upper half starts at 5.
```

The median is always one of the two tops:
- If both halves equal size: median = average of both tops = (3+5)/2 = 4.0
- If lower half is bigger by 1: median = lower half's max = 3
- If upper half is bigger by 1: median = upper half's min = 5

Every insertion is O(log n). Every median query is O(1).

> [↑ Back to Top](#top)

<a id="12-heap-vs-bst"></a>
# 12. Heap vs BST

Heap:
Only root guaranteed min/max.
Not fully sorted.

BST:
Fully ordered.
Inorder gives sorted list.

Heap:
Faster top element access.

BST:
Better for range queries.

Choose wisely.

> 📝 **Practice:** [Q42 · heap-vs-bst](../dsa_practice_questions_100.md#q42--interview--heap-vs-bst) · [Q83 · heap-vs-bst-compare](../dsa_practice_questions_100.md#q83--interview--heap-vs-bst-compare)

> [↑ Back to Top](#top)

<a id="13-real-world-applications"></a>
## Real-World Applications

- CPU scheduling (OS picks highest-priority process)
- Network packet priority (QoS routing)
- Event-driven simulation (next event by timestamp)
- Job schedulers (Kubernetes pod priority)
- Load balancing (assign to least-loaded server)
- Dijkstra's shortest path algorithm
- A* pathfinding (game AI)

Heaps manage priorities in real systems.

**Common mistake — lazy deletion with wrong virtual size:** When using lazy deletion (marking elements as invalid instead of removing them, as in Dijkstra's), forgetting to track virtual size separately from real heap size corrupts any size-dependent logic like median finding. Always maintain a separate `_size` counter that reflects pending removals.

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

| Concept | Key Takeaway |
|---------|-------------|
| Heap | Complete binary tree with priority ordering |
| Min-heap | Parent ≤ children. Root = minimum |
| Max-heap | Parent ≥ children. Root = maximum |
| Array storage | Left=2i+1, Right=2i+2, Parent=(i-1)//2 |
| Insert | Append + bubble up — O(log n) |
| Delete | Swap root with last + bubble down — O(log n) |
| Peek | O(1) — just look at index 0 |
| Heapify | Build from existing array — O(n) |
| Top K | Min-heap of size K — O(n log k) |
| Running median | Two heaps (max-heap lower + min-heap upper) |

**Mental model:** A heap is a mountain. The peak (root) is always the highest (max-heap) or lowest (min-heap). Everything else is somewhere below. You only guarantee the peak — and that constraint is what makes it fast.

When someone asks "what's the best/worst/most/least right now?" — that is a heap problem.

Mastering heaps prepares you for: Dijkstra, A*, scheduling problems, median maintenance, and advanced system design.

> 📝 **Practice:** [Q1 · min-heap property](./practice.md#q1--min-heap-property-check) · [Q2 · max-heap property](./practice.md#q2--max-heap-property-check) · [Q41 · heap-kth-largest](../dsa_practice_questions_100.md#q41--design--heap-kth-largest)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [15_binary_search_trees → theory.md](../15_binary_search_trees/theory.md) |
| ➡ Next Module | [17_trie → theory.md](../17_trie/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[15 BST →](../15_binary_search_trees/theory.md) · [17 Trie →](../17_trie/theory.md) · [09 Queue →](../09_queue/theory.md) · [25 Advanced Graphs →](../25_advanced_graphs/theory.md)

**Jump to specific topics in other files:**
- Priority queue basics → [09_queue § Priority Queue](../09_queue/theory.md#6-priority-queue)
- Dijkstra uses heaps → [25_advanced_graphs § theory.md](../25_advanced_graphs/theory.md)
- BST comparison → [15_binary_search_trees § theory.md](../15_binary_search_trees/theory.md)
- Tree fundamentals → [14_trees § theory.md](../14_trees/theory.md)

> [↑ Back to Top](#top)
