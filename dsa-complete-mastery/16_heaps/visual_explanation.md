# Heaps — The Hospital ER That Never Plays Favorites

---

## The Waiting Room That Changed Everything

Picture a hospital emergency room on a busy Saturday night.

The old way: first come, first served. A guy with a paper cut walked in at 9pm. A woman
having a heart attack walked in at 9:05pm. By the rules, paper cut goes first.

Obviously, that's insane.

So hospitals invented **triage**. Every patient gets a priority number. 1 = critical.
10 = "you're fine, sit down." The sickest person always goes next, no matter who arrived
when.

That's a heap. That's all it is.

A heap answers one question with blazing speed:

> "What's the most important thing right now?"

Not second most important. Not a sorted list. Just: **what's next?**

---

## Scene 1: The ER Waiting Room in Action

Patients arrive. Each gets a priority score (lower = more urgent):

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

---

## Scene 2: Wait... It Lives in an Array?

Here's where it gets cool. A heap *looks* like a tree when you draw it:

```
                 1
               /   \
              3     5
             / \   / \
            7   9 8   6
```

But it *lives* in a plain array:

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

**The heap property:** Every parent is smaller than (or equal to) both its children.
(This is a min-heap. A max-heap flips it: every parent is *larger* than its children.)

---

## Scene 3: A New Patient Arrives — Insert (Heapify Up)

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

But wait — Frank (2) is smaller than his parent at index (7-1)//2 = 3, which is 7.

**The heap property is violated.** 2 should not be below 7.

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

**Time complexity:** O(log n) — we travel at most the height of the tree upward.

---

## Scene 4: Treating the Most Critical Patient — Extract Min (Heapify Down)

Dave (priority 1, root) gets called in. We need to remove the root.

We can't just delete it and restructure the whole tree. Too slow. Instead, we have a trick:

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

**Step 2:** Heapify down. 7 is at the root but is bigger than both its children (2 and 5).
Find the smaller child and swap.

```
7 vs children: left=2, right=5. Smaller child is 2. Swap 7 and 2.

                 2
               /   \
              7     5
             / \   / \
            3   9 8   6

Array: [2, 7, 5, 3, 9, 8, 6]
```

**Step 3:** 7 is now at index 1. Its children: left=3 (index 3), right=9 (index 4).
Smaller child is 3. 7 > 3, so swap.

```
                 2
               /   \
              3     5
             / \   / \
            7   9 8   6

Array: [2, 3, 5, 7, 9, 8, 6]
```

**Step 4:** 7 is at index 3. Its children would be at index 7 and 8 — beyond the array.
7 is a leaf. Stop.

The heap is restored. The new minimum (2) is at the root, ready to serve next.

**Time complexity:** O(log n) — we travel at most the height of the tree downward.

---

## Scene 5: Top K Problem — "Find the 5 Most Critical Patients from 1 Million Records"

Imagine you have 1,000,000 patients in a database. You need the 5 most critical.

**Bad approach:** Sort all 1 million. O(n log n). Slow. Wastes work on elements you'll never use.

**Heap approach:** Keep a min-heap of size K=5.

The trick is counterintuitive at first: to find the TOP 5 (highest priority), use a MIN-heap
of size 5. The min-heap's root is the *least* important of your current top-5 candidates.

Why? Because you want to quickly ask: "Is this new person MORE important than the least
important person in my current top-5?" If yes, kick the weakest out, insert the new one.

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

Heap: min=1
```

New patient: priority 8. Is 8 < heap's min (1)? No. Ignore. Move on.

New patient: priority 4. Is 4 < heap's min (1)? No. Ignore.

New patient: priority 6. Is 6 < heap's min (1)? No. Ignore.

New patient: priority 0 (critical emergency!). Is 0 < heap's min (1)? YES.

```
→ Pop 1, insert 0.

         0
        / \
       3   5
      / \
     7   9
```

After all 1 million patients: heap contains exactly the 5 most critical, and we only
ever stored 5 elements in memory at once.

**Time:** O(n log k) where k=5. For n=1,000,000 and k=5, log(5) ≈ 2.3. Essentially O(n).

Compare to sorting: O(n log n) = O(1,000,000 × 20) = 20,000,000 operations.
Heap approach: O(1,000,000 × 2.3) = 2,300,000 operations.

**8x faster.** For larger k the gap narrows, but for small k it's a massive win.

---

## Scene 6: Two Heaps for the Median — The Perfect Balance

Your hospital wants to track the **median** patient priority at all times as new patients arrive.

The median is the middle value. If you have 7 patients, it's the 4th smallest priority.

**The insight:** Split patients into two halves.
- Lower half (smaller priorities) → store in a **max-heap** (biggest of the small ones at top)
- Upper half (larger priorities) → store in a **min-heap** (smallest of the big ones at top)

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

The median is always one of the two tops!

- If both halves equal size → median = average of both tops = (3+5)/2 = 4.0
- If lower half is bigger by 1 → median = lower half's max = 3
- If upper half is bigger by 1 → median = upper half's min = 5

**Inserting a new patient (priority 4):**

```
Is 4 ≤ max-heap top (3)? No → put in upper half (min-heap).

Min-heap now: [4, 5, 7, 8, 9]  ← upper half has 5, lower has 3

Sizes: lower=3, upper=5 → difference is 2, rebalance!
Move min-heap's top (4) to max-heap.

Max-heap: [4, 3, 2, 1]   (lower half, 4 elements)
Min-heap: [5, 7, 8, 9]   (upper half, 4 elements)

Equal sizes → median = (4 + 5) / 2 = 4.5
```

Every insertion is O(log n). Every median query is O(1).

No sorting. No scanning. Just two heaps in perfect balance.

---

## Quick Reference

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

The key insight to hold onto: a heap does NOT give you a fully sorted order.
It only guarantees the min (or max) is instantly accessible. That constraint is exactly
what makes it so fast. You're not doing more work than the problem requires.

When someone asks "what's the best/worst/most/least right now?" — that's a heap problem.
