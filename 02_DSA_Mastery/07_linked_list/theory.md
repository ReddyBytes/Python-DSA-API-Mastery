<a id="top"></a>
# 📘 07 – Linked List in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is a Linked List?](#1-what-is-a-linked-list)
  - [Visual: Parking Lot vs Treasure Hunt](#visual-parking-treasure)
  - [How Nodes Work in Memory](#nodes-in-memory)
- [2. Why No Random Access](#2-no-random-access)
  - [Visual: The Price of the Treasure Hunt](#visual-price)
  - [Array vs Linked List Operations](#operations-table)
- [3. Types of Linked Lists](#3-types)
  - [Singly Linked List](#singly)
  - [Doubly Linked List](#doubly)
  - [Circular Linked List](#circular)
- [4. Insertion — What Really Happens](#4-insertion)
  - [Insert at Head](#insert-head)
  - [Insert at End](#insert-end)
  - [Insert in Middle — The Surgery](#insert-middle)
- [5. Deletion — Detailed Mechanics](#5-deletion)
  - [Delete Head](#delete-head)
  - [Delete Middle Node](#delete-middle)
  - [Visual: Deletion — The Reverse Surgery](#visual-deletion)
- [6. Memory, Cache, and Performance](#6-memory-cache)
  - [Why Linked Lists Use More Memory](#memory-overhead)
  - [Cache Behavior](#cache-behavior)
- [7. Classic Linked List Problems](#7-classic-problems)
  - [Reverse Linked List — The 3-Pointer Dance](#reverse)
  - [Detect Cycle — Floyd's Tortoise and Hare](#detect-cycle)
  - [Find Middle Node — The Two-Speed Trick](#find-middle)
  - [Merge Two Sorted Lists](#merge-sorted)
- [8. Real-World Impact](#8-real-world)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
pointer manipulation · insertion and deletion · cycle detection (Floyd's) · reverse

**Should Learn** — Important for real projects, comes up regularly:
doubly linked list · find middle · merge sorted lists · LRU cache pattern

**Good to Know** — Useful in specific situations, not always tested:
sentinel nodes · copy list with random pointer

**Reference** — Know it exists, look up syntax when needed:
XOR linked list · skip list

Milo is a train conductor. His train is not like a normal rigid machine — each wagon is independent, parked somewhere in the rail yard, connected to the next wagon by a coupling hook. To add a wagon, Milo does not push every other wagon down the track. He just unhooks two wagons and hooks the new one between them. To remove a wagon, he unhooks it and reconnects its neighbors. But to find wagon number 47, he must walk from the engine through every wagon in order — there is no shortcut. That trade-off — easy coupling changes, slow lookups — is exactly what a linked list is.

<a id="1-what-is-a-linked-list"></a>
# 1. What Is a Linked List?

Milo's first lesson: understand why his train works differently from a parking lot. In a parking lot (array), every space is numbered and adjacent — you walk straight to spot 7. In Milo's rail yard (linked list), wagons are scattered everywhere, connected only by coupling hooks (pointers). You must follow the hooks to find anything.

Linked lists solve the problem arrays struggle with: **frequent insertions and deletions**. Instead of shifting every element, you just change connections.

<a id="visual-parking-treasure"></a>
## Visual: Parking Lot vs Treasure Hunt

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

Each box is called a **node**. Every node holds:
1. A **value** (the data)
2. A **next pointer** (the coupling to the next wagon)

```python
class Node:
    def __init__(self, val):
        self.val = val
        self.next = None
```

<a id="nodes-in-memory"></a>
## How Nodes Work in Memory

Milo learns that his wagons are not lined up neatly — they are scattered across the rail yard. Only the coupling hooks connect them. In memory, nodes can be anywhere. The pointer is the address of the next node.

```
Memory:
Address 100 → [10 | 200]
Address 200 → [20 | 350]
Address 350 → [30 | None]
```

The nodes are scattered. But connected via addresses. This is why:
- Indexing is impossible in O(1)
- But insertion is cheap (just change a coupling)

> [↑ Back to Top](#top)

<a id="2-no-random-access"></a>
# 2. Why No Random Access

Milo needs wagon 5. In a parking lot, he would walk straight to spot 5. But in his rail yard, he must start at the engine and walk through wagons 1, 2, 3, 4 before reaching 5. Every. Single. Time.

In an array, `arr[3]` calculates the address directly — O(1).
In a linked list, reaching the 4th node requires traversal — O(n).

<a id="visual-price"></a>
## Visual: The Price of the Treasure Hunt

```
Want to find the 5th node (index 4)?

Start → [12] → [5] → [33] → [18] → [7]
  step1   step2  step3  step4  step5
                                  ↑
                              FINALLY here

No shortcuts. You must visit every node before it.
```

Linked lists sacrifice direct access for flexibility.

<a id="operations-table"></a>
## Array vs Linked List Operations

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

<a id="3-types"></a>
# 3. Types of Linked Lists

Milo discovers his rail yard has three types of coupling systems. Some wagons only hook forward. Some hook both forward and backward. And some form a loop where the last wagon hooks back to the first.

<a id="singly"></a>
## Singly Linked List

Each node points forward only. Like a one-way street — miss your turn, start over from the beginning.

```
HEAD
  ↓
[1] →→→ [2] →→→ [3] →→→ [4] →→→ [5] →→→ None

Like a one-way street. You can only move right.
Miss your turn? Start over from the beginning.
```

Advantages: simpler, less memory. Limitation: cannot move backward.

> 📝 **Practice:** [Q26 · linked-list-operations](../dsa_practice_questions_100.md#q26--normal--linked-list-operations) · [Q30 · linked-list-tradeoffs](../dsa_practice_questions_100.md#q30--interview--linked-list-tradeoffs)

<a id="doubly"></a>
## Doubly Linked List

Each node has both `prev` and `next` pointers — Milo can walk forward or backward along the train.

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
        self.prev = None
```

Use doubly linked when you need to: traverse backwards, delete a node without knowing the previous node, implement browser back/forward history. Cost: one extra pointer per node.

> 📝 **Practice:** [Q2 · doubly-node](./practice.md#q2) · [Q25 · lru-cache](./practice.md#q25)

<a id="circular"></a>
## Circular Linked List

Last node points back to head — Milo's train forms a loop.

```
1 → 2 → 3
↑       ↓
←←←←←←←←
```

Used in: round-robin scheduling, circular buffer systems. Must handle traversal carefully to avoid infinite loops.

> 📝 **Practice:** [Q13 · cycle-detection](./practice.md#q13) · [Q22 · cycle-start](./practice.md#q22)

> [↑ Back to Top](#top)

<a id="4-insertion"></a>
# 4. Insertion — What Really Happens

Milo needs to add a new wagon to his train. Unlike a parking lot where every car must shift, Milo just unhooks two wagons and hooks the new one between them. The key: save the old coupling BEFORE cutting it, or the rest of the train rolls away.

<a id="insert-head"></a>
## Insert at Head

Milo adds a wagon at the front — O(1). This is where linked lists crush arrays.

```
Before:
HEAD
  ↓
[5] →→→ [12] →→→ [33] →→→ None

Insert 99 at head:

Step 1: Create [99]
Step 2: [99].next → [5]  (point new wagon to old engine)
Step 3: HEAD → [99]      (new wagon becomes the engine)

After:
HEAD
  ↓
[99] →→→ [5] →→→ [12] →→→ [33] →→→ None
```

```python
def insert_at_head(head, val):
    new_node = Node(val)
    new_node.next = head
    return new_node
```

Only 2 pointer updates. Always O(1).

> 📝 **Practice:** [Q5 · insert-head](./practice.md#q5)

<a id="insert-end"></a>
## Insert at End

Without a tail pointer: traverse entire list → O(n). With a tail pointer maintained: O(1). This is why many implementations store both head and tail.

> 📝 **Practice:** [Q6 · insert-tail](./practice.md#q6)

<a id="insert-middle"></a>
## Insert in Middle — The Surgery

Milo performs surgery on the coupling chain. Insert 99 between node 12 and node 33:

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

**Common mistake — wrong pointer order:** Do step 2 BEFORE step 3. If you do step 3 first, you lose the reference to [33] and the rest of the list is gone forever.

```python
def insert_after(prev_node, val):
    new_node = Node(val)
    new_node.next = prev_node.next   # Step 2 first!
    prev_node.next = new_node        # Step 3 second
```

> 📝 **Practice:** [Q9 · insert-after](./practice.md#q9)

> [↑ Back to Top](#top)

<a id="5-deletion"></a>
# 5. Deletion — Detailed Mechanics

Milo needs to remove a wagon. He cannot just yank it out — he must first connect the wagons on either side, then unhook the target. Deleting is bypassing: make the predecessor skip over the target and point directly to the successor.

<a id="delete-head"></a>
## Delete Head

```
Head → 10 → 20 → 30
Head = head.next
→ Now 10 is disconnected. Time: O(1)
```

**Common mistake — deleting head without a dummy node:** If a function might delete the head, use a dummy node as a stable anchor.

```python
def remove_all_correct(head, val):
    dummy = ListNode(0)
    dummy.next = head
    curr = dummy
    while curr.next:
        if curr.next.val == val:
            curr.next = curr.next.next
        else:
            curr = curr.next
    return dummy.next
```

> 📝 **Practice:** [Q7 · delete-head](./practice.md#q7)

<a id="delete-middle"></a>
## Delete Middle Node

Need reference to previous node. Update: `prev.next = current.next`. If you lose the previous pointer, deletion becomes difficult in a singly linked list — this is exactly why doubly linked lists exist.

> 📝 **Practice:** [Q10 · delete-val](./practice.md#q10) · [Q17 · nth-from-end](./practice.md#q17)

<a id="visual-deletion"></a>
## Visual: Deletion — The Reverse Surgery

Delete node [33] from the chain:

```
Before:  [5] →→→ [12] →→→ [33] →→→ [44] →→→ None
                   ↓         ↓
                  prev      to delete

After:   [5] →→→ [12] ────────────→ [44] →→→ None
                              ↑
                     [33] is now unreachable (garbage collected)
```

```python
prev.next = prev.next.next
```

**Common mistake — off-by-one in "Remove Nth From End":** The fast pointer must be `n+1` steps ahead of slow, so when fast reaches None, slow sits on the node BEFORE the target.

```python
def remove_nth_from_end_correct(head, n):
    dummy = ListNode(0)
    dummy.next = head
    fast = slow = dummy
    for _ in range(n + 1):
        fast = fast.next
    while fast:
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next
    return dummy.next
```

> [↑ Back to Top](#top)

<a id="6-memory-cache"></a>
# 6. Memory, Cache, and Performance

Milo notices something: each of his wagons carries not just cargo but also a heavy coupling mechanism. An array is like a flatbed truck — pure cargo, tightly packed. A linked list is like Milo's train — each wagon needs its own coupling hardware on top of the cargo.

<a id="memory-overhead"></a>
## Why Linked Lists Use More Memory

Each node stores data AND pointer(s). If data is 4 bytes, the pointer is 8 bytes — the overhead can exceed the actual data.

Compared to arrays: arrays store only data contiguously. Linked lists trade memory for flexibility.

**Common mistake — shallow copy shares nodes:** A shallow copy creates new node wrappers but copies `.next` references directly, so both lists share the same chain. Always create a new `ListNode` for every node.

```python
def copy_list(head):
    if not head:
        return None
    new_head = ListNode(head.val)
    new_curr = new_head
    curr = head.next
    while curr:
        new_curr.next = ListNode(curr.val)
        new_curr = new_curr.next
        curr = curr.next
    return new_head
```

<a id="cache-behavior"></a>
## Cache Behavior

Arrays: elements stored sequentially. CPU loads nearby elements automatically (spatial locality). Linked lists: nodes scattered in memory. Each pointer jump may cause a cache miss.

Even when time complexity looks similar, arrays often perform faster in practice. This matters in system design discussions.

> [↑ Back to Top](#top)

<a id="7-classic-problems"></a>
# 7. Classic Linked List Problems

Milo faces four challenges that every train conductor must master. These problems test pointer manipulation, careful state tracking, and logical precision — the core skills that make linked lists tricky.

<a id="reverse"></a>
## Reverse Linked List — The 3-Pointer Dance

Milo needs to reverse his entire train — the last wagon becomes the engine. He uses three hands: one holding the previous wagon, one on the current wagon, and one saving the next wagon before he flips the coupling.

Starting: `[1] → [2] → [3] → [4] → [5] → None`
Goal: `None ← [1] ← [2] ← [3] ← [4] ← [5]`

```
Initial:
prev=None  curr=[1]
  ↓          ↓
None      [1] →→→ [2] →→→ [3] →→→ [4] →→→ [5] →→→ None

--- Step 1 ---
next = curr.next = [2]     (save before breaking)
curr.next = prev = None    (reverse the coupling)
prev = curr = [1]          (advance prev)
curr = next = [2]          (advance curr)

None ←←← [1]    [2] →→→ [3] →→→ [4] →→→ [5] →→→ None
            ↑     ↑
           prev  curr

--- Step 2 ---
next = [3]
curr.next = prev = [1]
prev = [2], curr = [3]

None ←←← [1] ←←← [2]    [3] →→→ [4] →→→ [5] →→→ None

--- Steps 3-5 ---
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
        curr.next = prev        # reverse the coupling
        prev = curr             # advance prev
        curr = next_node        # advance curr
    return prev                 # prev is the new head
```

**Common mistake — losing the next pointer:** Save `curr.next` BEFORE changing any pointers. Memory aid: "Save, Reverse, Advance, Advance" — always 4 lines inside the loop.

> 📝 **Practice:** [Q28 · linked-list-reversal](../dsa_practice_questions_100.md#q28--logical--linked-list-reversal)

<a id="detect-cycle"></a>
## Detect Cycle — Floyd's Tortoise and Hare

Milo suspects his track loops back on itself. He sends two inspectors: a slow tortoise (1 wagon per step) and a fast hare (2 wagons per step). If the track loops, the hare will lap the tortoise and they will meet. If not, the hare reaches the end.

```
Linked list with a cycle:

[1] →→→ [2] →→→ [3] →→→ [4] →→→ [5]
                  ↑                 ↓
                  └←←←←←←←←← [6] ←┘

Start: both at [1]

Step 1: Tortoise=[2], Hare=[3]
Step 2: Tortoise=[3], Hare=[5]
Step 3: Tortoise=[4], Hare=[3]  (hare lapped!)
Step 4: Tortoise=[5], Hare=[5]  ← they meet!
```

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

**Common mistake — not guarding fast.next:** `fast.next.next` crashes if `fast.next` is `None`. Guard must check BOTH `fast` and `fast.next`.

> 📝 **Practice:** [Q27 · linked-list-cycle](../dsa_practice_questions_100.md#q27--thinking--linked-list-cycle) · [Q96 · debug-cycle-detection](../dsa_practice_questions_100.md#q96--debug--debug-cycle-detection)

<a id="find-middle"></a>
## Find Middle Node — The Two-Speed Trick

Milo sends two inspectors again: slow (1 step) and fast (2 steps). When fast hits the end, slow is at the midpoint. Why? When fast has traveled distance `n`, slow has traveled `n/2`.

```
[1] →→→ [2] →→→ [3] →→→ [4] →→→ [5] →→→ None

Start:  slow=[1], fast=[1]
Step 1: slow=[2], fast=[3]
Step 2: slow=[3], fast=[5]
Step 3: fast.next = None → stop!
        slow = [3] ← middle!
```

```python
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

For even-length lists, this returns the second of the two middle nodes.

**Common mistake — not cutting the link when splitting:** When splitting at midpoint for merge sort, set the tail of the first half to `None`. Otherwise both halves still share nodes — infinite recursion.

```python
def split_list(head):
    if not head or not head.next:
        return head, None
    slow, fast, prev = head, head, None
    while fast and fast.next:
        prev = slow
        slow = slow.next
        fast = fast.next.next
    prev.next = None    # CRITICAL: cut the link
    return head, slow
```

> 📝 **Practice:** [Q14 · find-middle](./practice.md#q14)

<a id="merge-sorted"></a>
## Merge Two Sorted Lists

Milo merges two sorted trains into one. Compare head wagons, attach the smaller one, advance that pointer. Time: O(n + m). Used in merge sort on linked lists.

> 📝 **Practice:** [Q29 · merge-sorted-lists](../dsa_practice_questions_100.md#q29--normal--merge-sorted-lists)

Key patterns summary:
```
  Reverse a list    → 3-pointer dance (prev, curr, next)
  Detect a cycle    → Floyd's tortoise and hare
  Find middle       → fast/slow pointers (2:1 speed ratio)
  Delete a node     → need prev node (singly) or use doubly
```

> [↑ Back to Top](#top)

<a id="8-real-world"></a>
# 8. Real-World Impact

Milo graduates from the rail yard and discovers that linked lists are rarely used alone in production — they are usually part of larger structures that combine their strengths with other data structures.

## LRU Cache

Uses a hash map for O(1) lookup AND a doubly linked list for O(1) insert/delete. Combines fast access and fast removal — the best of both worlds.

> 📝 **Practice:** [Q25 · lru-cache](./practice.md#q25)

## Graph Representation

Adjacency lists use linked lists. Efficient for sparse graphs where most nodes connect to few neighbors.

## Memory Allocators

Free memory blocks are maintained in linked lists. The OS allocator (`malloc`/`free`) uses free lists to track available memory chunks.

## Operating Systems

Process queues and scheduling systems use linked lists. Round-robin scheduling uses circular linked lists.

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

| Concept | Key Takeaway |
|---------|-------------|
| What it is | Chain of nodes connected by pointers — not contiguous |
| Random access | O(n) — must traverse from head |
| Insert at head | O(1) — just update pointers |
| Insert at tail | O(1) with tail pointer, O(n) without |
| Delete | O(1) if you have prev pointer, O(n) to find it |
| Memory | Higher per-element overhead (data + pointer) |
| Cache | Poor — nodes scattered in memory |
| Singly | One direction only, simpler |
| Doubly | Both directions, easier deletion |
| Circular | Last points to first — scheduling/buffers |

**When NOT to use linked lists:**
- Frequent indexing required (use array)
- Random access needed (use array)
- Cache performance critical (arrays win)
- Memory limited (pointer overhead too high)

In many real-world systems, arrays outperform linked lists. Linked lists shine when insertions/deletions at known positions are frequent and access patterns are sequential.

Linked lists are foundational for stacks, queues, hash tables (chaining), LRU caches, and graph algorithms. To master them, think in terms of pointer flow, not index arithmetic.

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [06_searching → theory.md](../06_searching/theory.md) |
| ➡ Next Module | [08_stack → theory.md](../08_stack/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[06 Searching →](../06_searching/theory.md) · [08 Stack →](../08_stack/theory.md) · [09 Queue →](../09_queue/theory.md) · [10 Hashing →](../10_hashing/theory.md)

**Jump to specific topics in other files:**
- Stack using linked list → [08_stack § theory.md](../08_stack/theory.md)
- Queue using linked list → [09_queue § theory.md](../09_queue/theory.md)
- Hash table chaining → [10_hashing § theory.md](../10_hashing/theory.md)
- Graph adjacency list → [18_graphs § theory.md](../18_graphs/theory.md)

> [↑ Back to Top](#top)
