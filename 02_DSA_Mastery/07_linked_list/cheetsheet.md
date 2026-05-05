## LINKED LIST — QUICK REFERENCE CHEATSHEET

```
┌──────────────┬───────────────────────────────────────────────────────────┐
│ Type         │ Description                                               │
├──────────────┼───────────────────────────────────────────────────────────┤
│ Singly       │ node → node → None  (next pointer only)                   │
│ Doubly       │ None ← node ↔ node → None  (prev + next)                 │
│ Circular     │ tail.next = head  (no None terminus)                      │
└──────────────┴───────────────────────────────────────────────────────────┘
```

---

## COMPLEXITY TABLE

```
┌───────────────────────────┬──────────┬──────────┬──────────┬──────────┐
│ Operation                 │ Singly   │ Doubly   │ Array    │ Notes    │
├───────────────────────────┼──────────┼──────────┼──────────┼──────────┤
│ Access by index           │ O(n)     │ O(n)     │ O(1)     │          │
│ Search                    │ O(n)     │ O(n)     │ O(n)     │          │
│ Insert at head            │ O(1)     │ O(1)     │ O(n)     │ ★ fast   │
│ Insert at tail            │ O(1)*    │ O(1)     │ O(1)a    │ *w/ tail │
│ Insert at middle          │ O(n)     │ O(n)     │ O(n)     │ search   │
│ Delete at head            │ O(1)     │ O(1)     │ O(n)     │ ★ fast   │
│ Delete at tail            │ O(n)     │ O(1)     │ O(1)a    │ singly=  │
│ Delete at middle          │ O(n)     │ O(n)     │ O(n)     │ costly   │
└───────────────────────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## PYTHON NODE TEMPLATE

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# Build list from array
def build(arr):
    dummy = ListNode(0)
    cur = dummy
    for v in arr:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next

# Convert back to list
def to_list(head):
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result
```

---

## COLLECTIONS.DEQUE AS DOUBLY-LINKED LIST

```python
from collections import deque

dq = deque()
dq.appendleft(x)   # O(1) insert front
dq.append(x)       # O(1) insert back
dq.popleft()       # O(1) remove front
dq.pop()           # O(1) remove back
dq[0], dq[-1]      # O(1) peek both ends

# Use deque when: need O(1) both ends, no custom node traversal needed
```

---

## CORE TECHNIQUE TEMPLATES

### Floyd's Cycle Detection (Fast / Slow Pointers)
```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False

def cycle_start(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast: break
    else: return None           # no cycle
    slow = head                 # reset one pointer to head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    return slow                 # meeting point = cycle start
```

### Reverse a Linked List (Iterative)
```python
def reverse(head):
    prev = None
    curr = head
    while curr:
        nxt = curr.next    # save next — DON'T forget this
        curr.next = prev   # reverse pointer
        prev = curr        # advance prev
        curr = nxt         # advance curr
    return prev            # new head

# Recursive version
def reverse_rec(head):
    if not head or not head.next: return head
    new_head = reverse_rec(head.next)
    head.next.next = head
    head.next = None
    return new_head
```

### Find Middle Node
```python
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow     # for even length: returns second middle
                    # use "fast.next and fast.next.next" for first middle
```

### Merge Two Sorted Lists
```python
def merge(l1, l2):
    dummy = ListNode(0)
    cur = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            cur.next = l1; l1 = l1.next
        else:
            cur.next = l2; l2 = l2.next
        cur = cur.next
    cur.next = l1 or l2    # attach remainder
    return dummy.next
```

### Remove Nth Node from End
```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)    # dummy head protects against edge cases
    fast = slow = dummy
    for _ in range(n + 1):      # advance fast n+1 steps
        fast = fast.next
    while fast:
        slow = slow.next
        fast = fast.next
    slow.next = slow.next.next   # skip target node
    return dummy.next
```

---

## DUMMY HEAD NODE — WHEN TO USE

```
USE dummy = ListNode(0, head) when:
  ✓ Head node itself might be deleted
  ✓ Building a new list from scratch (merge, partition)
  ✓ Any operation where the head pointer might change
  ✓ Simplifies code: no special-case for empty list

SKIP dummy when:
  ✗ Only traversing, not modifying structure
  ✗ Guaranteed head is never removed
```

---

## COMMON GOTCHAS

```
TRAP 1: Losing next pointer during reversal
  ALWAYS save nxt = curr.next BEFORE modifying curr.next

TRAP 2: Off-by-one in "remove Nth from end"
  Advance fast n+1 steps (not n) so slow lands on node BEFORE target.

TRAP 3: Infinite loop in cycle-aware code
  Always check fast and fast.next before fast.next.next.

TRAP 4: Modifying list while iterating
  Keep a reference to the node being removed via prev pointer.

TRAP 5: Forgetting tail handling
  After while loop, attach cur.next = remaining_list (merge pattern).

TRAP 6: Circular list with standard traversal
  Use cycle detection or track visited nodes with a set.
```

---

## INTERVIEW QUICK PATTERNS

```
Two pointers on same list:
  • k steps apart  → remove Nth from end
  • fast=2x slow   → middle, cycle detection
  • both start=head → intersection of two lists

Reversal applications:
  • Palindrome check  → reverse second half, compare
  • Reverse in k-groups → iterative segment reversal
  • Rotate list by k  → find new tail, re-link

Dummy head applications:
  • Merge sorted lists
  • Remove duplicates
  • Partition list around pivot
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Visual Explanation](./visual_explanation.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
