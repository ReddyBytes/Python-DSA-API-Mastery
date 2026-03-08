# Linked Lists — Visual Explanation

---

## Chapter 1: The Treasure Hunt vs The Parking Lot

Imagine two ways to store your belongings.

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

---

## Chapter 2: The Price of the Treasure Hunt (No Random Access)

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

---

## Chapter 3: Singly vs Doubly Linked List

### Singly Linked List — The One-Way Street

Each node only knows where to go FORWARD. There is no going back.

```
HEAD
  ↓
[1] →→→ [2] →→→ [3] →→→ [4] →→→ [5] →→→ None

Like a one-way street. You can only move right.
Miss your turn? Start over from the beginning.
```

### Doubly Linked List — The Two-Way Street

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

---

## Chapter 4: Inserting at the Head — The Easy Win

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

---

## Chapter 5: Inserting in the Middle — The Surgery

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

WARNING: Do step 2 BEFORE step 3. If you do step 3 first, you lose the reference
to [33] and the rest of the list is gone forever!

```python
def insert_after(prev_node, val):
    new_node = Node(val)
    new_node.next = prev_node.next   # Step 2 first!
    prev_node.next = new_node        # Step 3 second
```

---

## Chapter 6: Deleting a Node — The Reverse Surgery

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

**The critical question: why do you need the previous node?**

In a singly linked list, each node only knows where to go FORWARD. Node [33] has no
idea who is pointing to it. So to remove it, you must tell its predecessor to stop
pointing to it. No predecessor reference = stuck.

This is exactly why doubly linked lists exist — each node knows its `prev`, so you
can delete yourself in O(1) without needing the predecessor.

---

## Chapter 7: Reversing a Linked List — The 3-Pointer Dance

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

---

## Chapter 8: Floyd's Cycle Detection — The Tortoise and the Hare

Imagine a circular running track. You put a slow tortoise and a fast hare on the
track at the same starting point. The hare runs at twice the tortoise's speed.

Will they ever meet again? **Yes, always — somewhere on the loop.**

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

**Why do they always meet inside the cycle?** Here is the intuition without the math:

Once the hare enters the cycle, it is running in circles. The tortoise will eventually
enter the cycle too. At that point, think of the hare as "behind" the tortoise from
its own perspective (since they're both circling). The hare gains 1 step per iteration
on the tortoise. It WILL close the gap and catch up.

If there is no cycle, the hare reaches `None` first — that is how you know there is
no cycle.

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

---

## Chapter 9: Finding the Middle — The Two-Speed Trick

Same two-pointer idea: one pointer moves 1 step, one moves 2 steps. When the fast
pointer hits the end, the slow pointer is at the middle.

**Why?** When fast has traveled distance `n`, slow has traveled `n/2`. So slow is
at the midpoint.

Let's trace this on `[1] → [2] → [3] → [4] → [5] → None`:

```
Start:
  slow=[1]
  fast=[1]

Step 1:
  slow=[2]  (moved 1)
  fast=[3]  (moved 2)

Step 2:
  slow=[3]  (moved 1)
  fast=[5]  (moved 2)

Step 3:
  slow=[4]  (moved 1)
  fast=None  (fast.next was None, so we stop)

  But wait — let's check the condition carefully.
  We stop when fast is None or fast.next is None.

Actually let's retrace with the correct stopping condition:

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

---

## Quick Reference

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

Key patterns:
  Reverse a list    → 3-pointer dance (prev, curr, next)
  Detect a cycle    → Floyd's tortoise and hare
  Find middle       → fast/slow pointers (2:1 speed ratio)
  Delete a node     → need prev node (singly) or use doubly
```

---

*Next up: Stacks — where plates are piled high and order matters.*
