<a id="top"></a>
# Linked List — Deep Conceptual Theory (Zero to Advanced)

> Linked Lists are about relationships, not positions.
>
> Arrays think in terms of index.
> Linked lists think in terms of connections.
>
> To master linked lists, you must visualize memory and pointer flow clearly.

## 📖 Table of Contents

1. [The Core Problem Linked Lists Solve](#1-the-core-problem)
2. [What Is a Linked List — Internally](#2-what-is-a-linked-list)
3. [Why Linked Lists Cannot Provide O(1) Access](#3-no-random-access)
4. [Types of Linked Lists — Detailed Understanding](#4-types-of-linked-lists)
5. [Insertion — What Really Happens](#5-insertion)
6. [Deletion — Detailed Mechanics](#6-deletion)
7. [Why Linked Lists Use More Memory](#7-memory-overhead)
8. [Cache Behavior and Performance](#8-cache-behavior)
9. [Classic Linked List Problems — Why They Matter](#9-classic-problems)
10. [When Linked Lists Are Actually Used in Real Systems](#10-real-systems)
11. [When NOT to Use Linked Lists](#11-when-not-to-use)
12. [Final Understanding](#12-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
pointer manipulation · insertion and deletion · cycle detection (Floyd's) · reverse

**Should Learn** — Important for real projects, comes up regularly:
doubly linked list · find middle · merge sorted lists · LRU cache pattern

**Good to Know** — Useful in specific situations, not always tested:
sentinel nodes · copy list with random pointer

**Reference** — Know it exists, look up syntax when needed:
XOR linked list · skip list

<a id="1-the-core-problem"></a>
# 1. The Core Problem Linked Lists Solve

Before understanding linked lists, understand what arrays struggle with.

Imagine you have:

```
[10, 20, 30, 40]
```

If you insert 5 at the beginning:

```
[5, 10, 20, 30, 40]
```

Every element must shift one position.

If this happens repeatedly,
cost becomes O(n) each time.

Now imagine a system where:

- New items are frequently added at the front
- Elements are frequently removed from the middle
- Size grows unpredictably

In such scenarios,
shifting entire blocks of memory becomes inefficient.

Linked lists solve this by removing the idea of shifting.

Instead of moving elements,
we change connections.

## Visual: The Parking Lot vs the Treasure Hunt

Think of two ways to store your belongings.

**Option A — The Parking Lot (Array):**
You rent 10 parking spots in a row. Spot 1, Spot 2, Spot 3... all numbered, all
side by side. To find your car in Spot 7, you just walk directly to Spot 7. Done.

**Option B — The Treasure Hunt (Linked List):**
Your belongings are scattered across the city. The first location is your friend's
basement. Inside, there is a clue: "your next item is at the coffee shop on 5th Ave."
At the coffee shop, there is another clue: "go to the library, third floor." And so on.
Each location holds your item AND a clue pointing to the next location.

```
ARRAY (parking lot):
[0]  [1]  [2]  [3]  [4]  [5]
 12   5   33   18   7    44
 ↑                       ↑
 directly addressable by index

LINKED LIST (treasure hunt):
[12] →→→ [5] →→→ [33] →→→ [18] →→→ [7] →→→ [44] →→→ None
  ↑        ↑
data    pointer to next node
```

Each box in the linked list is called a **node**. Every node holds:
1. A **value** (the data you actually care about)
2. A **next pointer** (the clue to the next node)

```python
class Node:
    def __init__(self, val):
        self.val = val
        self.next = None
```

> [↑ Back to Top](#top)

<a id="2-what-is-a-linked-list"></a>
# 2. What Is a Linked List — Internally

A linked list is a chain of nodes.

Each node contains:

- Data
- Reference (pointer) to next node

Important difference from array:

Array:
Memory is contiguous.

Linked List:
Nodes can be anywhere in memory.
Only the pointer connects them.

Visualization:

```
Memory:
Address 100 → [10 | 200]
Address 200 → [20 | 350]
Address 350 → [30 | None]
```

The nodes are scattered.
But connected via addresses.

This is why:

- Indexing is impossible in O(1)
- But insertion is cheap

> [↑ Back to Top](#top)

<a id="3-no-random-access"></a>
# 3. Why Linked Lists Cannot Provide O(1) Access

In array:

To get arr[3]:
We calculate address directly.

In linked list:

To get 4th node:
We must traverse:

```
Head → 1 → 2 → 3 → 4
```

Each step follows next pointer.

Traversal cost:
O(n)

This is fundamental limitation.

Linked lists sacrifice direct access for flexibility.

## Visual: The Price of the Treasure Hunt

Here is the catch with the treasure hunt: to find your item at location 5, you MUST
follow every clue in order. You cannot teleport to location 5.

```
Want to find the 5th node (index 4)?

Start → [12] → [5] → [33] → [18] → [7]
  step1   step2  step3  step4  step5
                                  ↑
                              FINALLY here

No shortcuts. You must visit every node before it.
```

- Array access by index: **O(1)** — just calculate the memory address
- Linked list access by index: **O(n)** — must walk from the head

This is the fundamental tradeoff. Arrays are fast for access, slow for insertion
(have to shift everything). Linked lists are slow for access, fast for insertion
at a known location (just update a pointer).

```
+--------------------------+----------+----------+
| Operation                | Array    | Linked   |
+--------------------------+----------+----------+
| Access by index          | O(1)     | O(n)     |
| Insert at head           | O(n)     | O(1)     |
| Insert at tail (w/ tail) | O(1)     | O(1)     |
| Insert in middle         | O(n)     | O(1)*    |
| Delete                   | O(n)     | O(1)*    |
| Search                   | O(n)     | O(n)     |
+--------------------------+----------+----------+
* O(1) only if you already have a pointer to the location
```

> [↑ Back to Top](#top)

<a id="4-types-of-linked-lists"></a>
# 4. Types of Linked Lists — Detailed Understanding

## Singly Linked List

Each node points forward only.

Structure:

```
Head → [10 | • ] → [20 | • ] → [30 | None]
```

Advantages:
- Simpler
- Less memory overhead

Limitation:
Cannot move backward.

> 📝 **Practice:** [Q26 · linked-list-operations](../dsa_practice_questions_100.md#q26--normal--linked-list-operations) · [Q30 · linked-list-tradeoffs](../dsa_practice_questions_100.md#q30--interview--linked-list-tradeoffs)

## Visual: Singly — The One-Way Street

Each node only knows where to go FORWARD. There is no going back.

```
HEAD
  ↓
[1] →→→ [2] →→→ [3] →→→ [4] →→→ [5] →→→ None

Like a one-way street. You can only move right.
Miss your turn? Start over from the beginning.
```

## Doubly Linked List

> 📝 **Practice:** [Q2 · doubly-node](./practice.md#q2) · [Q25 · lru-cache](./practice.md#q25)

Each node contains:

- prev pointer
- next pointer

Structure:

```
None ← [10] ⇄ [20] ⇄ [30] → None
```

Advantages:
- Bi-directional traversal
- Easier deletion when node reference given

Trade-off:
Extra memory for prev pointer.

## Visual: Doubly — The Two-Way Street

Each node knows both its previous and next neighbor.

```
         ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
HEAD                                         TAIL
  ↓                                            ↓
[1] ⇄ [2] ⇄ [3] ⇄ [4] ⇄ [5]
  →→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→

Each node: [prev | val | next]
```

```python
class DoublyNode:
    def __init__(self, val):
        self.val = val
        self.next = None
        self.prev = None   # the extra pointer
```

When do you want doubly linked? When you need to:
- Traverse backwards
- Delete a node without knowing the previous node
- Implement a browser's back/forward history

The cost: each node uses slightly more memory (one extra pointer).

## Circular Linked List

> 📝 **Practice:** [Q13 · cycle-detection](./practice.md#q13) · [Q22 · cycle-start](./practice.md#q22)

Last node points back to head.

```
1 → 2 → 3
↑       ↓
←←←←←←←←
```

Used in:
- Round-robin scheduling
- Circular buffer systems

Important:
Must handle traversal carefully to avoid infinite loops.

> [↑ Back to Top](#top)

<a id="5-insertion"></a>
# 5. Insertion — What Really Happens

Let's analyze insertion deeply.

## Insert at Beginning

> 📝 **Practice:** [Q5 · insert-head](./practice.md#q5)

Before:

```
Head → 10 → 20 → 30
```

Insert 5:

Step 1:
Create new node (5)

Step 2:
Point new_node.next to current head

Step 3:
Update head to new_node

After:

```
Head → 5 → 10 → 20 → 30
```

No shifting.
Only pointer updates.

Time:
O(1)

## Visual: Insert at Head — The Easy Win

Inserting at the beginning of a linked list is O(1). This is one place where linked
lists absolutely crush arrays (which need to shift every element right).

**Before:**

```
HEAD
  ↓
[5] →→→ [12] →→→ [33] →→→ None
```

**We want to insert 99 at the head.**

Step 1: Create the new node.
Step 2: Point the new node's `next` to the current head.
Step 3: Update HEAD to point to the new node.

```
Step 1: Create [99]

Step 2: [99] →→→ [5] →→→ [12] →→→ [33] →→→ None
         ↑
    new node's next points to old head

Step 3:
HEAD
  ↓
[99] →→→ [5] →→→ [12] →→→ [33] →→→ None
```

```python
def insert_at_head(head, val):
    new_node = Node(val)
    new_node.next = head
    return new_node          # new head
```

Only 2 pointer updates. Always O(1), regardless of list size.

## Insert at End

> 📝 **Practice:** [Q6 · insert-tail](./practice.md#q6)

If no tail pointer:

You must traverse entire list.

Traversal cost:
O(n)

Then update last node's next pointer.

If tail pointer maintained:

Insert becomes O(1).

This is why many implementations store both head and tail.

## Insert in Middle

> 📝 **Practice:** [Q9 · insert-after](./practice.md#q9)

Suppose inserting after node with value 20.

Steps:

1. Traverse until node found
2. Save next pointer
3. Update current.next to new_node
4. new_node.next = saved pointer

Traversal makes it O(n).
Pointer update itself is constant.

## Visual: Insert in Middle — The Surgery

Inserting in the middle is like performing surgery: you need to be careful not to
drop any connections before making the new ones.

**Before:** Insert 99 between node 12 and node 33.

```
[5] →→→ [12] →→→ [33] →→→ [44]
          ↑
    we want to insert after this node
```

**The 3-step surgery:**

```
Step 1: Create the new node [99]

[5] →→→ [12] →→→ [33] →→→ [44]
                  [99]

Step 2: Point [99].next → [33]  (save the connection BEFORE cutting!)

[5] →→→ [12] →→→ [33] →→→ [44]
                  ↑
         [99] ───┘

Step 3: Point [12].next → [99]  (now cut the old connection)

[5] →→→ [12] →→→ [99] →→→ [33] →→→ [44]
```

**Common mistake — wrong pointer order:** Do step 2 BEFORE step 3. If you do step 3 first, you lose the reference to [33] and the rest of the list is gone forever. Always save `new_node.next = prev_node.next` before setting `prev_node.next = new_node`.

```python
def insert_after(prev_node, val):
    new_node = Node(val)
    new_node.next = prev_node.next   # Step 2 first!
    prev_node.next = new_node        # Step 3 second
```

> [↑ Back to Top](#top)

<a id="6-deletion"></a>
# 6. Deletion — Detailed Mechanics

Deleting node is about bypassing it.

## Delete Head

> 📝 **Practice:** [Q7 · delete-head](./practice.md#q7)

```
Head → 10 → 20 → 30
```

Move head:

```
Head = head.next
```

Now 10 is disconnected.

Time:
O(1)

**Common mistake — deleting head without a dummy node:** If a function might delete the head node (e.g., "remove all nodes with value X"), returning `head` at the end gives back the deleted node. Use a dummy node whose `.next` points to `head` as a stable return point regardless of what happens to head.

```python
def remove_all_correct(head, val):
    dummy = ListNode(0)
    dummy.next = head       # dummy is always stable — never deleted
    curr = dummy

    while curr.next:
        if curr.next.val == val:
            curr.next = curr.next.next  # skip the matching node
        else:
            curr = curr.next

    return dummy.next       # dummy.next is the new head (may differ from original head)
```

Use a dummy node whenever:
- Deleting the first node based on a condition
- Inserting at the beginning conditionally
- Any operation where the returned head might not be the original head

## Delete Middle Node

> 📝 **Practice:** [Q10 · delete-val](./practice.md#q10) · [Q17 · nth-from-end](./practice.md#q17)

Suppose deleting node 20.

Need reference to previous node (10).

Update:

```
prev.next = current.next
```

20 is removed from chain.

Important:
If you lose previous pointer,
deletion becomes difficult in singly list.

## Visual: Deletion — The Reverse Surgery

To delete node [33] from:

```
[5] →→→ [12] →→→ [33] →→→ [44] →→→ None
```

You need to make [12] skip over [33] and point directly to [44].

```
Before:  [5] →→→ [12] →→→ [33] →→→ [44] →→→ None
                   ↓         ↓
                  prev      to delete

After:   [5] →→→ [12] ────────────→ [44] →→→ None
                              ↑
                     [33] is now unreachable (garbage collected)
```

```python
# prev is the node BEFORE the one we want to delete
prev.next = prev.next.next
```

**Why do you need the previous node?**

In a singly linked list, each node only knows where to go FORWARD. Node [33] has no
idea who is pointing to it. So to remove it, you must tell its predecessor to stop
pointing to it. No predecessor reference = stuck.

This is exactly why doubly linked lists exist — each node knows its `prev`, so you
can delete yourself in O(1) without needing the predecessor.

**Common mistake — off-by-one in "Remove Nth Node From End":** The two-pointer technique requires the fast pointer to be exactly `n+1` steps ahead of slow, so that when fast reaches None, slow sits on the node BEFORE the target. Advancing fast only `n` times leaves slow pointing AT the target, making it impossible to unlink the node.

```python
def remove_nth_from_end_correct(head, n):
    dummy = ListNode(0)
    dummy.next = head
    fast = dummy
    slow = dummy

    # Advance fast n+1 times so slow.next is the node to delete when fast reaches None.
    for _ in range(n + 1):
        fast = fast.next

    while fast:
        fast = fast.next
        slow = slow.next

    slow.next = slow.next.next
    return dummy.next
```

> [↑ Back to Top](#top)

<a id="7-memory-overhead"></a>
# 7. Why Linked Lists Use More Memory

Each node stores:

- Data
- Pointer(s)

If data is 4 bytes,
pointer might also be 8 bytes.

Memory overhead is significant.

Compared to array:

Array stores only data (contiguous).

Linked list trades memory for flexibility.

**Common mistake — shallow copy shares nodes:** A shallow copy creates new `ListNode` objects but copies the `.next` reference directly, so the "copy" and the original share the same chain of nodes. Mutating one mutates the other. Always create a new `ListNode` for every node in a deep copy.

```python
def copy_list_simple(head):
    if not head:
        return None
    new_head = ListNode(head.val)
    new_curr = new_head
    curr = head.next
    while curr:
        new_curr.next = ListNode(curr.val)   # always create a NEW node
        new_curr = new_curr.next
        curr = curr.next
    return new_head
```

> [↑ Back to Top](#top)

<a id="8-cache-behavior"></a>
# 8. Cache Behavior and Performance

Arrays:
Elements stored sequentially.

CPU loads nearby elements automatically (spatial locality).

Linked lists:
Nodes scattered in memory.

Each pointer jump may cause cache miss.

Even if time complexity looks similar,
arrays often perform faster in practice.

This is important in system design discussions.

> [↑ Back to Top](#top)

<a id="9-classic-problems"></a>
# 9. Classic Linked List Problems — Why They Matter

Linked lists test:

- Pointer manipulation
- Careful state tracking
- Logical precision

Common problems:

## Reverse Linked List

Requires reassigning next pointers one-by-one.

You must maintain:

- previous
- current
- next_node

Mismanaging pointer order causes data loss.

> 📝 **Practice:** [Q28 · linked-list-reversal](../dsa_practice_questions_100.md#q28--logical--linked-list-reversal)

## Visual: Reversing a Linked List — The 3-Pointer Dance

This is one of the most commonly asked interview questions. The trick is using three
pointers: `prev`, `curr`, and `next`.

**Starting state:** `[1] → [2] → [3] → [4] → [5] → None`

Goal: `None ← [1] ← [2] ← [3] ← [4] ← [5]`

```
Initial:
prev=None  curr=[1]  (next will be assigned in loop)
  ↓          ↓
None      [1] →→→ [2] →→→ [3] →→→ [4] →→→ [5] →→→ None

--- Step 1 ---
next = curr.next = [2]     (save [2] before we break the pointer)
curr.next = prev = None    (reverse the arrow: [1] now points backward to None)
prev = curr = [1]          (advance prev)
curr = next = [2]          (advance curr)

None ←←← [1]    [2] →→→ [3] →→→ [4] →→→ [5] →→→ None
            ↑     ↑
           prev  curr

--- Step 2 ---
next = [3]
curr.next = prev = [1]     (reverse: [2] now points to [1])
prev = [2]
curr = [3]

None ←←← [1] ←←← [2]    [3] →→→ [4] →→→ [5] →→→ None
                    ↑      ↑
                   prev   curr

--- Step 3 ---
None ←←← [1] ←←← [2] ←←← [3]    [4] →→→ [5] →→→ None
                              ↑     ↑
                             prev  curr

--- Step 4 ---
None ←←← [1] ←←← [2] ←←← [3] ←←← [4]    [5] →→→ None

--- Step 5 ---
None ←←← [1] ←←← [2] ←←← [3] ←←← [4] ←←← [5]    None
                                               ↑      ↑
                                              prev   curr

curr is now None — loop ends. prev is the new HEAD = [5].
```

```python
def reverse_linked_list(head):
    prev = None
    curr = head
    while curr:
        next_node = curr.next   # save next
        curr.next = prev        # reverse the arrow
        prev = curr             # advance prev
        curr = next_node        # advance curr
    return prev                 # prev is the new head
```

**Common mistake — losing the next pointer during reversal:** You must save `curr.next` BEFORE changing any pointers. The moment you write `curr.next = prev`, you lose access to the rest of the list. Memory aid: "Save, Reverse, Advance, Advance" — always 4 lines inside the while loop. If you only have 3 lines, you forgot to save `next_node` first.

## Detect Cycle

Two-pointer approach:

- Slow moves 1 step
- Fast moves 2 steps

If they meet → cycle exists.

Why it works:
Fast pointer eventually laps slow pointer in cycle.

Elegant mathematical reasoning.

> 📝 **Practice:** [Q27 · linked-list-cycle](../dsa_practice_questions_100.md#q27--thinking--linked-list-cycle) · [Q96 · debug-cycle-detection](../dsa_practice_questions_100.md#q96--debug--debug-cycle-detection)

## Visual: Floyd's Cycle Detection — The Tortoise and the Hare

Imagine a circular running track. You put a slow tortoise and a fast hare on the
track at the same starting point. The hare runs at twice the tortoise's speed.

Will they ever meet again? Yes, always — somewhere on the loop.

This is Floyd's algorithm. Use it to detect cycles in a linked list.

```
Linked list with a cycle:

[1] →→→ [2] →→→ [3] →→→ [4] →→→ [5]
                  ↑                 ↓
                  └←←←←←←←←← [6] ←┘

Tortoise moves 1 step at a time.
Hare moves 2 steps at a time.
```

```
Start: both at [1]

Step 1: Tortoise=[2], Hare=[3]
Step 2: Tortoise=[3], Hare=[5]
Step 3: Tortoise=[4], Hare=[3]  (hare lapped around the cycle!)
Step 4: Tortoise=[5], Hare=[5]  ← they meet!
```

Once the hare enters the cycle, it is running in circles. The tortoise will eventually
enter the cycle too. At that point, the hare gains 1 step per iteration on the tortoise.
It will close the gap and catch up. If there is no cycle, the hare reaches `None` first.

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True       # they met — cycle exists
    return False              # fast hit None — no cycle
```

**Common mistake — not guarding fast.next:** Floyd's cycle detection uses `fast.next.next`. If `fast.next` is `None`, accessing `fast.next.next` raises `AttributeError`. The guard must check BOTH `fast` and `fast.next`. Python short-circuits left to right: if `fast` is None, `fast.next` is never evaluated.

## Find Middle Node

> 📝 **Practice:** [Q14 · find-middle](./practice.md#q14)

Using slow/fast pointer:

When fast reaches end,
slow is at midpoint.

Avoids counting nodes first.

## Visual: Finding the Middle — The Two-Speed Trick

Same two-pointer idea: one pointer moves 1 step, one moves 2 steps. When the fast
pointer hits the end, the slow pointer is at the middle.

Why? When fast has traveled distance `n`, slow has traveled `n/2`. So slow is at the midpoint.

Let's trace this on `[1] → [2] → [3] → [4] → [5] → None`:

```
Start:  slow=[1], fast=[1]
Step 1: slow=[2], fast=[3]   (fast=fast.next.next)
Step 2: slow=[3], fast=[5]
Step 3: Check: fast.next = None → stop!
        slow = [3] ← this is the middle!

[1] →→→ [2] →→→ [3] →→→ [4] →→→ [5] →→→ None
                  ↑
                middle (slow stopped here)
```

```python
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow   # middle node
```

For even-length lists like `[1,2,3,4]`, this returns the second of the two middle
nodes. Adjust the stopping condition if you need the first.

**Common mistake — forgetting to set prev.next = None when splitting a list:** When you split a list at a midpoint (common in Merge Sort on linked lists), you must set the tail of the first half to `None`. If you don't, the first half still points into the second half — they're not actually separate lists, causing infinite recursion.

```python
def split_list_correct(head):
    if not head or not head.next:
        return head, None
    slow = head
    fast = head
    prev = None
    while fast and fast.next:
        prev = slow
        slow = slow.next
        fast = fast.next.next
    prev.next = None    # CRITICAL: cut the link so the two halves are independent
    return head, slow   # head = first half, slow = second half
```

## Merge Two Sorted Lists

Compare head nodes,
attach smaller one,
move pointer forward.

Time:
O(n + m)

Used in merge sort.

> 📝 **Practice:** [Q29 · merge-sorted-lists](../dsa_practice_questions_100.md#q29--normal--merge-sorted-lists)

Key patterns:
```
  Reverse a list    → 3-pointer dance (prev, curr, next)
  Detect a cycle    → Floyd's tortoise and hare
  Find middle       → fast/slow pointers (2:1 speed ratio)
  Delete a node     → need prev node (singly) or use doubly
```

> [↑ Back to Top](#top)

<a id="10-real-systems"></a>
# 10. When Linked Lists Are Actually Used in Real Systems

Linked lists are rarely used alone.

They are usually part of larger structures.

Examples:

## LRU Cache

> 📝 **Practice:** [Q25 · lru-cache](./practice.md#q25)

Uses:

- Hash map for O(1) lookup
- Doubly linked list for O(1) insert/delete

Combines fast access and fast removal.

## Graph Representation

Adjacency list uses linked lists.

Efficient for sparse graphs.

## Memory Allocators

Free memory blocks maintained in linked lists.

## Operating Systems

Process queues and scheduling systems.

> [↑ Back to Top](#top)

<a id="11-when-not-to-use"></a>
# 11. When NOT to Use Linked Lists

Avoid when:

- Frequent indexing required
- Random access needed
- Cache performance critical
- Memory limited

In many real-world systems,
arrays outperform linked lists.

> [↑ Back to Top](#top)

<a id="12-final-understanding"></a>
# 12. Final Understanding

Linked lists are:

- Pointer-based structures
- Flexible for insertion/deletion
- Poor for indexing
- Memory-heavy compared to arrays

They are foundational for:

- Stacks
- Queues
- Hash tables (chaining)
- LRU caches
- Graph algorithms

To master linked lists,
you must think in terms of pointer flow,
not index arithmetic.

Once pointer manipulation becomes intuitive,
advanced data structures become much easier.

> [↑ Back to Top](#top)

**[🏠 Back to README](../README.md)**

**Prev:** [← Searching — Interview Q&A](../06_searching/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
