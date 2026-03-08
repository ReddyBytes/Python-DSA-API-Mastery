# Linked Lists — Common Mistakes & Error Prevention

---

## Mistake 1: Losing the Next Pointer During Reversal

### The Bug
When reversing a linked list, you must save `curr.next` BEFORE changing any pointers.
The moment you write `curr.next = prev`, you lose access to the rest of the list.

### Wrong Code
```python
def reverse_list_wrong(head):
    prev = None
    curr = head
    while curr:
        prev = curr           # BUG: we haven't saved curr.next yet
        curr = curr.next      # this still works here...
        curr.next = prev      # CRASH or wrong: curr is now the NEXT node,
                              # so we're setting next_node.next = old_curr
                              # We've lost the chain entirely
    return prev
```

### Correct Code
```python
def reverse_list_correct(head):
    prev = None
    curr = head
    while curr:
        next_node = curr.next   # STEP 1: save next BEFORE any pointer changes
        curr.next = prev        # STEP 2: reverse the pointer
        prev = curr             # STEP 3: advance prev
        curr = next_node        # STEP 4: advance curr using the saved reference
    return prev
```

### Test Case That Exposes the Bug
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def list_to_array(head):
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result

def array_to_list(arr):
    if not arr:
        return None
    head = ListNode(arr[0])
    curr = head
    for val in arr[1:]:
        curr.next = ListNode(val)
        curr = curr.next
    return head

# Test: reverse [1, 2, 3, 4, 5]
head = array_to_list([1, 2, 3, 4, 5])
result = reverse_list_correct(head)
assert list_to_array(result) == [5, 4, 3, 2, 1], "Reversal failed"
print("Reversal test passed:", list_to_array(result))

# Edge case: single node
single = ListNode(42)
result = reverse_list_correct(single)
assert list_to_array(result) == [42]

# Edge case: two nodes
head2 = array_to_list([1, 2])
result2 = reverse_list_correct(head2)
assert list_to_array(result2) == [2, 1]
print("All reversal tests passed")
```

### Memory Aid
> "Save, Reverse, Advance, Advance" — always 4 lines inside the while loop.
> If you only have 3 lines, you forgot to save next_node first.

---

## Mistake 2: Off-by-One in "Remove Nth Node From End"

### The Bug
The two-pointer technique requires the fast pointer to be exactly `n+1` steps ahead of slow,
so that when fast reaches None, slow is sitting on the node BEFORE the target.

Advancing fast only `n` times leaves slow pointing AT the target instead of before it,
making it impossible to unlink the node.

### Wrong Code
```python
def remove_nth_from_end_wrong(head, n):
    dummy = ListNode(0)
    dummy.next = head
    fast = dummy
    slow = dummy

    # BUG: advance fast only n times instead of n+1
    for _ in range(n):          # should be range(n + 1)
        fast = fast.next

    while fast.next:
        fast = fast.next
        slow = slow.next

    # slow is NOW pointing AT the node to delete, not BEFORE it
    # slow.next is the node AFTER the target — we skip the wrong node
    slow.next = slow.next.next  # deletes wrong node
    return dummy.next
```

### Correct Code
```python
def remove_nth_from_end_correct(head, n):
    dummy = ListNode(0)
    dummy.next = head
    fast = dummy
    slow = dummy

    # Advance fast n+1 times so there is a gap of n+1 between fast and slow.
    # When fast reaches None, slow.next is the node to delete.
    for _ in range(n + 1):
        fast = fast.next

    while fast:
        fast = fast.next
        slow = slow.next

    # slow is now the node BEFORE the target
    slow.next = slow.next.next
    return dummy.next
```

### Visual Explanation
```
List: 1 -> 2 -> 3 -> 4 -> 5, remove 2nd from end (target = node 4)

WRONG (advance n=2 times):
dummy -> 1 -> 2 -> 3 -> 4 -> 5 -> None
         ^         ^
        slow      fast    (gap of 2)

After traversal:
dummy -> 1 -> 2 -> 3 -> 4 -> 5 -> None
                   ^         ^
                  slow      fast.next=None
slow.next = 4, but we want slow to be at 3 to delete 4.
Result: removes node 5 instead of 4. WRONG.

CORRECT (advance n+1=3 times):
dummy -> 1 -> 2 -> 3 -> 4 -> 5 -> None
         ^              ^
        slow           fast    (gap of 3)

After traversal:
dummy -> 1 -> 2 -> 3 -> 4 -> 5 -> None
                   ^              ^
                  slow          fast=None
slow.next = 4. Skip it: slow.next = slow.next.next = 5. CORRECT.
```

### Test Case That Exposes the Bug
```python
head = array_to_list([1, 2, 3, 4, 5])
result = remove_nth_from_end_correct(head, 2)
assert list_to_array(result) == [1, 2, 3, 5], f"Got {list_to_array(result)}"
print("Remove 2nd from end passed:", list_to_array(result))

# Edge case: remove the head (n equals length)
head = array_to_list([1, 2, 3])
result = remove_nth_from_end_correct(head, 3)
assert list_to_array(result) == [2, 3]

# Edge case: single node list
head = ListNode(1)
result = remove_nth_from_end_correct(head, 1)
assert result is None
print("All remove-nth tests passed")
```

---

## Mistake 3: Cycle Detection — Not Guarding fast.next

### The Bug
Floyd's cycle detection uses `fast.next.next`. If `fast.next` is `None`, accessing
`fast.next.next` raises `AttributeError`. The guard must check BOTH `fast` and `fast.next`.

### Wrong Code
```python
def has_cycle_wrong(head):
    slow = head
    fast = head
    while fast.next.next:       # BUG: crashes if fast.next is None
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

### Correct Code
```python
def has_cycle_correct(head):
    slow = head
    fast = head
    while fast and fast.next:   # guard BOTH fast and fast.next
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

### Why the Order Matters in the Guard
```python
# "fast and fast.next" — Python short-circuits left to right.
# If fast is None, fast.next is never evaluated. Safe.
# If fast is not None but fast.next is None, fast.next.next is never evaluated. Safe.
```

### Test Cases That Expose the Bug
```python
# No cycle — list ends normally. Wrong version crashes here.
head = array_to_list([1, 2, 3, 4, 5])
assert has_cycle_correct(head) == False

# Even-length list with no cycle (fast lands exactly on None)
head = array_to_list([1, 2])
assert has_cycle_correct(head) == False

# List with cycle: 1 -> 2 -> 3 -> 4 -> 2 (cycle back to node 2)
n1 = ListNode(1)
n2 = ListNode(2)
n3 = ListNode(3)
n4 = ListNode(4)
n1.next = n2
n2.next = n3
n3.next = n4
n4.next = n2   # cycle
assert has_cycle_correct(n1) == True

# Single node, no cycle
assert has_cycle_correct(ListNode(1)) == False

# Empty list
assert has_cycle_correct(None) == False
print("All cycle detection tests passed")
```

---

## Mistake 4: Modifying Head Without a Dummy Node

### The Bug
If a function might delete the head node (e.g., "remove all nodes with value X"),
returning `head` at the end gives back the deleted node. A dummy node whose `.next`
points to `head` gives you a stable return point regardless of what happens to head.

### Wrong Code
```python
def remove_all_wrong(head, val):
    # Handle head separately — easy to forget edge cases
    while head and head.val == val:
        head = head.next

    curr = head
    while curr and curr.next:
        if curr.next.val == val:
            curr.next = curr.next.next  # BUG: this part is fine, but the
        else:                           # head-handling above is brittle.
            curr = curr.next            # What if ALL nodes match? curr = head = None,
                                        # then the second while loop crashes.
    return head
```

### Correct Code
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

### Test Cases That Expose the Bug
```python
# Remove value from the head
head = array_to_list([6, 1, 2, 6, 3, 6])
result = remove_all_correct(head, 6)
assert list_to_array(result) == [1, 2, 3], f"Got {list_to_array(result)}"

# Remove ALL nodes — the hardest case for the wrong version
head = array_to_list([7, 7, 7])
result = remove_all_correct(head, 7)
assert result is None

# Remove from tail
head = array_to_list([1, 2, 3, 3])
result = remove_all_correct(head, 3)
assert list_to_array(result) == [1, 2]

# Nothing to remove
head = array_to_list([1, 2, 3])
result = remove_all_correct(head, 9)
assert list_to_array(result) == [1, 2, 3]
print("All dummy-node tests passed")
```

### When to Always Use a Dummy Node
- Deleting the first node based on a condition
- Inserting at the beginning conditionally
- Any operation where the returned head might not be the original head

---

## Mistake 5: Shallow Copy vs Deep Copy of Linked List

### The Bug
A shallow copy creates new `ListNode` objects but copies the `.next` reference directly,
so the "copy" and the original share the same chain of nodes. Mutating one mutates the other.

### Wrong Code
```python
def copy_list_wrong(head):
    if not head:
        return None
    new_head = ListNode(head.val)
    new_head.next = head.next   # BUG: points to ORIGINAL node, not a copy
    # Result: new_head.next IS head.next — same object in memory
    return new_head
```

### Correct Code — Using a Hash Map (Required for Lists with Random Pointers)
```python
def copy_list_correct(head):
    if not head:
        return None

    # Pass 1: create a new node for every original node
    old_to_new = {}
    curr = head
    while curr:
        old_to_new[curr] = ListNode(curr.val)
        curr = curr.next

    # Pass 2: wire up .next pointers using the map
    curr = head
    while curr:
        if curr.next:
            old_to_new[curr].next = old_to_new[curr.next]
        curr = curr.next

    return old_to_new[head]
```

### Correct Code — Single Pass for Simple Lists
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

### Test Case That Exposes the Bug
```python
original = array_to_list([1, 2, 3])
shallow = copy_list_wrong(original)
deep = copy_list_correct(original)

# Mutate the original list
original.next.val = 99   # change node with value 2

# Shallow copy reflects the change — they share node objects
print("Shallow copy after mutation:", list_to_array(shallow))
# Output: [1, 99, 3]  <-- WRONG, we didn't change the copy

# Deep copy is unaffected
print("Deep copy after mutation:", list_to_array(deep))
# Output: [1, 2, 3]   <-- CORRECT

assert list_to_array(deep) == [1, 2, 3], "Deep copy was mutated — it's not truly deep"
print("Deep copy test passed")
```

---

## Mistake 6: Forgetting to Set `prev.next = None` When Splitting a List

### The Bug
When you split a list at a midpoint (common in Merge Sort on linked lists), you must
set the tail of the first half to `None`. If you don't, the first half still points
into the second half — they're not actually separate lists.

### Wrong Code
```python
def get_middle_wrong(head):
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    # slow is now at the midpoint
    # BUG: we return slow as the start of the second half,
    # but the first half's tail still points to slow.
    # The two halves are NOT independent.
    return slow
```

### Correct Code
```python
def split_list_correct(head):
    """Returns (first_half_head, second_half_head) as two independent lists."""
    if not head or not head.next:
        return head, None

    slow = head
    fast = head
    prev = None

    while fast and fast.next:
        prev = slow
        slow = slow.next
        fast = fast.next.next

    # prev is the last node of the first half
    prev.next = None    # CRITICAL: cut the link so the two halves are independent

    return head, slow   # head = first half, slow = second half

def merge_sort_linked_list(head):
    if not head or not head.next:
        return head

    left, right = split_list_correct(head)  # must use the correct split
    left = merge_sort_linked_list(left)
    right = merge_sort_linked_list(right)
    return merge(left, right)

def merge(l1, l2):
    dummy = ListNode(0)
    curr = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            curr.next = l1
            l1 = l1.next
        else:
            curr.next = l2
            l2 = l2.next
        curr = curr.next
    curr.next = l1 or l2
    return dummy.next
```

### Test Case That Exposes the Bug
```python
# Using the wrong split causes infinite recursion in merge sort
# because the first half never shrinks — it still contains the full list.

head = array_to_list([4, 2, 1, 3, 5])
sorted_head = merge_sort_linked_list(head)
assert list_to_array(sorted_head) == [1, 2, 3, 4, 5], f"Got {list_to_array(sorted_head)}"
print("Merge sort test passed:", list_to_array(sorted_head))

# Verify split itself
head = array_to_list([1, 2, 3, 4, 5])
first, second = split_list_correct(head)
assert list_to_array(first) == [1, 2]
assert list_to_array(second) == [3, 4, 5]
# Prove they are independent: first half tail is None
curr = first
while curr.next:
    curr = curr.next
assert curr.next is None, "First half tail should be None after split"
print("Split test passed — halves are independent")
```

---

## Quick Reference Summary

| Mistake | Root Cause | One-Line Fix |
|---|---|---|
| Losing next during reversal | Pointer overwritten before saving | `next_node = curr.next` as first line |
| Off-by-one remove nth from end | Fast pointer not far enough ahead | Advance fast `n+1` times, not `n` |
| Cycle detection crash | `fast.next` not guarded | `while fast and fast.next` |
| Deleting head returns garbage | No stable return reference | Always use a `dummy` node |
| Shallow copy shares nodes | `.next` copied by reference | Create new `ListNode` for every node |
| Split list stays connected | Tail of first half not cut | Set `prev.next = None` after finding midpoint |
