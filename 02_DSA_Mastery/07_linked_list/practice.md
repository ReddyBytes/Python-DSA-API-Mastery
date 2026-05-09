# 📝 Linked List — Practice Questions

> 25 questions. Start at Basic, work up to Advanced.
> Each question has a collapsible hint + full answer with explanation and complexity.

---

## Quick Index

| # | Topic | Level |
|---|-------|-------|
| [Q1](#q1) | Define a singly linked list node | Basic |
| [Q2](#q2) | Define a doubly linked list node | Basic |
| [Q3](#q3) | Build a linked list from an array | Basic |
| [Q4](#q4) | Traverse and print all values | Basic |
| [Q5](#q5) | Insert a node at the head | Basic |
| [Q6](#q6) | Insert a node at the tail | Basic |
| [Q7](#q7) | Delete the head node | Basic |
| [Q8](#q8) | Linked list vs array — when to choose each | Basic |
| [Q9](#q9) | Insert a node after a given value | Intermediate |
| [Q10](#q10) | Delete a node by value | Intermediate |
| [Q11](#q11) | Reverse a linked list (iterative) | Intermediate |
| [Q12](#q12) | Reverse a linked list (recursive) | Intermediate |
| [Q13](#q13) | Detect a cycle — Floyd's algorithm | Intermediate |
| [Q14](#q14) | Find the middle node | Intermediate |
| [Q15](#q15) | Merge two sorted linked lists | Intermediate |
| [Q16](#q16) | Remove duplicates from a sorted list | Intermediate |
| [Q17](#q17) | Remove Nth node from the end | Intermediate |
| [Q18](#q18) | Find the intersection point of two lists | Intermediate |
| [Q19](#q19) | Check if a linked list is a palindrome | Intermediate |
| [Q20](#q20) | Remove all nodes matching a value | Intermediate |
| [Q21](#q21) | Deep copy a list with random pointers | Advanced |
| [Q22](#q22) | Find the start of a cycle (Floyd's extended) | Advanced |
| [Q23](#q23) | Reverse a linked list in k-groups | Advanced |
| [Q24](#q24) | Flatten a multilevel doubly linked list | Advanced |
| [Q25](#q25) | Implement an LRU cache using a doubly linked list | Advanced |

---

## Basic (Q1–Q8)

---

<a id="q1"></a>
### Q1

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


**Define a singly linked list node in Python. Create a small list `1 → 2 → 3` manually (no helper function).**

<details>
<summary>💡 Hint</summary>

Each node needs two fields: `val` and `next`. Link them by assigning `node.next = next_node`.

</details>

<details>
<summary>✅ Answer</summary>

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

# Build 1 → 2 → 3 manually
n3 = ListNode(3)
n2 = ListNode(2, n3)
n1 = ListNode(1, n2)
head = n1
# head.val == 1, head.next.val == 2, head.next.next.val == 3
```

**Why:** A node is just an object holding data + a pointer. All linked list complexity comes from managing those pointers carefully.

**Time:** O(1) per node creation. **Space:** O(n) total for n nodes.

</details>

---

<a id="q2"></a>
### Q2

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


**Define a doubly linked list node. Build the list `A ↔ B ↔ C` manually with `prev` and `next` wired up correctly.**

<details>
<summary>💡 Hint</summary>

Each node needs `val`, `next`, and `prev`. Wire both directions: `a.next = b` AND `b.prev = a`.

</details>

<details>
<summary>✅ Answer</summary>

```python
class DoublyNode:
    def __init__(self, val=0):
        self.val = val
        self.next = None
        self.prev = None

a = DoublyNode("A")
b = DoublyNode("B")
c = DoublyNode("C")

a.next = b
b.prev = a
b.next = c
c.prev = b

# Traverse forward: a → b → c
# Traverse backward starting from c: c → b → a
```

**Why:** The extra `prev` pointer is what enables O(1) deletion without needing the predecessor — you already have it.

**Time:** O(1) per link. **Space:** O(n) — each node stores two pointers instead of one.

</details>

---

<a id="q3"></a>
### Q3

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


**Write a helper function `build(arr)` that converts a Python list into a linked list and returns the head.**

<details>
<summary>💡 Hint</summary>

Use a dummy head. Iterate through `arr`, creating a new `ListNode` for each value and appending it.

</details>

<details>
<summary>✅ Answer</summary>

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build(arr):
    dummy = ListNode(0)
    cur = dummy
    for v in arr:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next

head = build([1, 2, 3, 4, 5])
```

**Why:** A dummy node eliminates the special case for an empty list — you always append to `cur.next` and advance `cur`.

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q4"></a>
### Q4

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


**Write a function `to_list(head)` that traverses a linked list and returns its values as a Python list.**

<details>
<summary>💡 Hint</summary>

Start at `head`, append `node.val` to a result list, advance `node = node.next` until `None`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def to_list(head):
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result

# to_list(build([3, 1, 4])) == [3, 1, 4]
```

**Why:** There is no shortcut for traversal — you must follow each pointer in turn. This O(n) walk is the fundamental cost of linked list access.

**Time:** O(n). **Space:** O(n) for the output list.

</details>

---

<a id="q5"></a>
### Q5

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


**Write `insert_head(head, val)` — insert a new node with `val` at the front of the list. Return the new head.**

<details>
<summary>💡 Hint</summary>

Create a new node. Point its `next` to the current head. That new node becomes the new head.

</details>

<details>
<summary>✅ Answer</summary>

```python
def insert_head(head, val):
    new_node = ListNode(val)
    new_node.next = head
    return new_node          # caller updates their head reference

head = build([2, 3, 4])
head = insert_head(head, 1)
# to_list(head) == [1, 2, 3, 4]
```

**Why:** Only two pointer updates. No traversal needed. This is the fundamental O(1) advantage linked lists have over arrays for front insertion.

**Time:** O(1). **Space:** O(1).

</details>

---

<a id="q6"></a>
### Q6

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


**Write `insert_tail(head, val)` — append a node at the end of the list. Return the head.**

<details>
<summary>💡 Hint</summary>

Traverse until `curr.next is None`, then set `curr.next = new_node`. Handle the empty list case.

</details>

<details>
<summary>✅ Answer</summary>

```python
def insert_tail(head, val):
    new_node = ListNode(val)
    if not head:
        return new_node
    curr = head
    while curr.next:
        curr = curr.next
    curr.next = new_node
    return head

head = build([1, 2, 3])
head = insert_tail(head, 4)
# to_list(head) == [1, 2, 3, 4]
```

**Why:** Without a stored `tail` pointer, we must walk the whole list — O(n). If you store `tail` separately, this becomes O(1). Most production implementations store `tail`.

**Time:** O(n) without tail pointer; O(1) with tail. **Space:** O(1).

</details>

---

<a id="q7"></a>
### Q7

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


**Write `delete_head(head)` — remove the first node and return the new head. Handle the empty list case.**

<details>
<summary>💡 Hint</summary>

If `head` is `None`, return `None`. Otherwise return `head.next`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def delete_head(head):
    if not head:
        return None
    return head.next     # old head is unreferenced, garbage collected

head = build([1, 2, 3])
head = delete_head(head)
# to_list(head) == [2, 3]
```

**Why:** Deleting the head only requires updating one pointer. No shifting. This is O(1) vs O(n) for arrays.

**Time:** O(1). **Space:** O(1).

</details>

---

<a id="q8"></a>
### Q8

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


**In two sentences each, state one situation where you would choose a linked list over an array, and one where you would choose an array over a linked list.**

<details>
<summary>💡 Hint</summary>

Think about: insertion frequency, access patterns, memory, cache behavior.

</details>

<details>
<summary>✅ Answer</summary>

**Choose linked list when** you need frequent O(1) insertions and deletions at the front or a known interior position, and you never need random access by index — for example, implementing a queue, LRU cache, or undo history.

**Choose array when** you need fast O(1) random access by index, or when cache performance matters — arrays store elements contiguously so the CPU's prefetcher loads nearby elements automatically, while linked list pointer chasing causes cache misses on every step.

**Why:** The tradeoff is access speed vs. mutation flexibility. Arrays win on cache locality; linked lists win on structural mutations.

**Array access:** O(1). **Linked list access:** O(n). **Array insert at front:** O(n). **Linked list insert at front:** O(1).

</details>

---

## Intermediate (Q9–Q20)

---

<a id="q9"></a>
### Q9

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


**Write `insert_after(head, target_val, new_val)` — find the first node with `target_val` and insert a new node with `new_val` immediately after it. Return the head.**

<details>
<summary>💡 Hint</summary>

Traverse until you find the target. Then: new node's `next` = target's `next`, THEN target's `next` = new node. Order matters.

</details>

<details>
<summary>✅ Answer</summary>

```python
def insert_after(head, target_val, new_val):
    curr = head
    while curr:
        if curr.val == target_val:
            new_node = ListNode(new_val)
            new_node.next = curr.next   # Step 1: save the connection first
            curr.next = new_node        # Step 2: cut and reconnect
            return head
        curr = curr.next
    return head  # target not found — unchanged

head = build([1, 2, 4, 5])
head = insert_after(head, 2, 3)
# to_list(head) == [1, 2, 3, 4, 5]
```

**Why:** You must save `curr.next` before overwriting it. If you do step 2 first, you lose the tail of the list permanently.

**Time:** O(n) to find target. **Space:** O(1).

</details>

---

<a id="q10"></a>
### Q10

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


**Write `delete_val(head, val)` — delete the first node with `val`. Return the new head. Use a dummy node.**

<details>
<summary>💡 Hint</summary>

A dummy node before head means you never need to special-case deleting the head node. Traverse looking at `curr.next.val`, then unlink.

</details>

<details>
<summary>✅ Answer</summary>

```python
def delete_val(head, val):
    dummy = ListNode(0)
    dummy.next = head
    curr = dummy
    while curr.next:
        if curr.next.val == val:
            curr.next = curr.next.next   # bypass the target node
            break
        curr = curr.next
    return dummy.next

head = build([1, 2, 3, 4])
head = delete_val(head, 2)
# to_list(head) == [1, 3, 4]

# Also handles deleting the head:
head = build([1, 2, 3])
head = delete_val(head, 1)
# to_list(head) == [2, 3]
```

**Why:** The dummy node makes `dummy.next` a stable return point even if the original head is deleted. Without it, you need an ugly `if head.val == val` special case.

**Time:** O(n). **Space:** O(1).

</details>

---

<a id="q11"></a>
### Q11

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


**Reverse a linked list iteratively. Return the new head.**

<details>
<summary>💡 Hint</summary>

Three pointers: `prev = None`, `curr = head`. In each step: save `next_node`, reverse arrow, advance both pointers. Four lines inside the loop.

</details>

<details>
<summary>✅ Answer</summary>

```python
def reverse_iterative(head):
    prev = None
    curr = head
    while curr:
        next_node = curr.next   # 1. save next
        curr.next = prev        # 2. reverse the arrow
        prev = curr             # 3. advance prev
        curr = next_node        # 4. advance curr
    return prev                 # prev is the new head

head = build([1, 2, 3, 4, 5])
head = reverse_iterative(head)
# to_list(head) == [5, 4, 3, 2, 1]
```

**Why:** You need `next_node` saved at the start of each iteration because `curr.next = prev` destroys the forward link. The mnemonic is "Save, Reverse, Advance, Advance" — always exactly 4 lines inside the loop.

**Time:** O(n). **Space:** O(1) — in-place.

</details>

---

<a id="q12"></a>
### Q12

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


**Reverse a linked list recursively. Return the new head.**

<details>
<summary>💡 Hint</summary>

Base case: empty or single node. Recursive case: recurse on `head.next`, then make `head.next.next = head` and `head.next = None`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def reverse_recursive(head):
    if not head or not head.next:
        return head
    new_head = reverse_recursive(head.next)   # recurse to end
    head.next.next = head   # node after head points back to head
    head.next = None        # head is now the tail, so next = None
    return new_head         # the deepest node is always the new head

head = build([1, 2, 3])
head = reverse_recursive(head)
# to_list(head) == [3, 2, 1]
```

**Why:** The recursive call returns the new head (last node), while on the way back up we rewire each node to point at its predecessor. Elegant but uses O(n) call stack space.

**Time:** O(n). **Space:** O(n) call stack — iterative is preferred for large inputs.

</details>

---

<a id="q13"></a>
### Q13

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


**Detect whether a linked list has a cycle using Floyd's algorithm. Return `True` or `False`.**

<details>
<summary>💡 Hint</summary>

Tortoise (1 step) and hare (2 steps). If they ever point to the same node, there is a cycle. Guard `while fast and fast.next` — both checks needed.

</details>

<details>
<summary>✅ Answer</summary>

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:      # guard both: fast could be None or fast.next could be None
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False                   # fast hit None → no cycle
```

**Why:** In a cycle, the hare and tortoise are both trapped in the loop forever. The hare gains 1 step per iteration on the tortoise, so it must eventually lap and catch the tortoise. If there is no cycle, the hare exits through `None`.

**Time:** O(n). **Space:** O(1) — no visited set needed.

</details>

---

<a id="q14"></a>
### Q14

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


**Find the middle node of a linked list using the fast/slow pointer technique. For an even-length list, return the second middle node.**

<details>
<summary>💡 Hint</summary>

Fast moves 2 steps, slow moves 1. When `fast` or `fast.next` is `None`, slow is at the middle.

</details>

<details>
<summary>✅ Answer</summary>

```python
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow   # for even length, returns second of two middles

# [1, 2, 3, 4, 5] → returns node with val=3
# [1, 2, 3, 4]    → returns node with val=3 (second middle)
```

**Why:** When fast has traveled 2k steps, slow has traveled k steps. So when fast hits the end (n steps), slow is at n/2. No need to count the list first.

**Time:** O(n). **Space:** O(1).

</details>

---

<a id="q15"></a>
### Q15

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


**Merge two sorted linked lists into one sorted linked list. Return the new head.**

<details>
<summary>💡 Hint</summary>

Use a dummy head. Compare the heads of both lists, attach the smaller one, advance that pointer. After the loop, attach whatever remains.

</details>

<details>
<summary>✅ Answer</summary>

```python
def merge_sorted(l1, l2):
    dummy = ListNode(0)
    cur = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            cur.next = l1
            l1 = l1.next
        else:
            cur.next = l2
            l2 = l2.next
        cur = cur.next
    cur.next = l1 or l2    # attach the non-exhausted remainder
    return dummy.next

a = build([1, 3, 5])
b = build([2, 4, 6])
# to_list(merge_sorted(a, b)) == [1, 2, 3, 4, 5, 6]
```

**Why:** We rewire existing nodes — no new nodes created. The dummy head means we never special-case which list starts first. `cur.next = l1 or l2` attaches whichever list has remaining nodes.

**Time:** O(n + m). **Space:** O(1) — in-place rewiring.

</details>

---

<a id="q16"></a>
### Q16

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


**Remove duplicate values from a sorted linked list so each value appears only once.**

<details>
<summary>💡 Hint</summary>

Since the list is sorted, duplicates are always adjacent. Traverse and skip nodes where `curr.val == curr.next.val`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def remove_duplicates(head):
    curr = head
    while curr and curr.next:
        if curr.val == curr.next.val:
            curr.next = curr.next.next   # skip the duplicate
        else:
            curr = curr.next             # only advance when no duplicate found
    return head

head = build([1, 1, 2, 3, 3, 3, 4])
head = remove_duplicates(head)
# to_list(head) == [1, 2, 3, 4]
```

**Why:** Do NOT advance `curr` when you find a duplicate — there may be three or more consecutive duplicates. Only advance when the next value is different.

**Time:** O(n). **Space:** O(1).

</details>

---

<a id="q17"></a>
### Q17

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


**Remove the Nth node from the end of the list in one pass. Return the new head.**

<details>
<summary>💡 Hint</summary>

Advance `fast` by `n+1` steps (not `n`). Then move both pointers until `fast` is `None`. `slow.next` is the target. Use a dummy head to handle removing the first node.

</details>

<details>
<summary>✅ Answer</summary>

```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n + 1):       # n+1 gap: when fast=None, slow is before the target
        fast = fast.next
    while fast:
        slow = slow.next
        fast = fast.next
    slow.next = slow.next.next   # unlink the target node
    return dummy.next

head = build([1, 2, 3, 4, 5])
head = remove_nth_from_end(head, 2)
# to_list(head) == [1, 2, 3, 5]
```

**Why:** Advancing `fast` by `n+1` (not `n`) ensures `slow` ends up on the node BEFORE the target, not on the target itself. This lets us do `slow.next = slow.next.next` cleanly.

**Time:** O(n) — one pass. **Space:** O(1).

</details>

---

<a id="q18"></a>
### Q18

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


**Find the intersection node of two linked lists (the node where they merge and share the same tail). Return the node, or `None` if they do not intersect.**

<details>
<summary>💡 Hint</summary>

Two pointers. When pointer A reaches the end of list A, redirect it to the head of list B, and vice versa. They will meet at the intersection after traveling equal total distances.

</details>

<details>
<summary>✅ Answer</summary>

```python
def get_intersection(headA, headB):
    a, b = headA, headB
    while a is not b:
        a = a.next if a else headB   # when A exhausts, jump to head of B
        b = b.next if b else headA   # when B exhausts, jump to head of A
    return a   # either the intersection node, or None if they never met

# If A has length m+k and B has length n+k (k = shared tail):
# Pointer A travels m+k+n before reaching intersection.
# Pointer B travels n+k+m before reaching intersection. Equal.
```

**Why:** Both pointers travel the same total distance (m + n + k). They are guaranteed to meet at the intersection node, or both reach `None` simultaneously if no intersection exists.

**Time:** O(m + n). **Space:** O(1).

</details>

---

<a id="q19"></a>
### Q19

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


**Check whether a linked list is a palindrome. Return `True` or `False`. O(n) time, O(1) space.**

<details>
<summary>💡 Hint</summary>

Find the middle, reverse the second half in-place, compare both halves from each end. Optionally restore the list after.

</details>

<details>
<summary>✅ Answer</summary>

```python
def is_palindrome(head):
    # Step 1: find middle
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    # Step 2: reverse second half in-place
    prev, curr = None, slow
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    right = prev   # head of reversed second half

    # Step 3: compare
    left = head
    while right:
        if left.val != right.val:
            return False
        left = left.next
        right = right.next
    return True

# is_palindrome(build([1, 2, 3, 2, 1])) == True
# is_palindrome(build([1, 2, 3]))        == False
```

**Why:** Reversing the second half in-place avoids O(n) extra space. The comparison only needs to run through the (shorter) right half.

**Time:** O(n). **Space:** O(1).

</details>

---

<a id="q20"></a>
### Q20

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


**Remove all nodes from a linked list whose value equals `val`. Return the new head.**

<details>
<summary>💡 Hint</summary>

Use a dummy node. Iterate checking `curr.next.val`. When a match is found, skip it with `curr.next = curr.next.next` but do NOT advance `curr` — there may be consecutive matches.

</details>

<details>
<summary>✅ Answer</summary>

```python
def remove_all(head, val):
    dummy = ListNode(0, head)
    curr = dummy
    while curr.next:
        if curr.next.val == val:
            curr.next = curr.next.next   # skip the matching node
        else:
            curr = curr.next             # advance only when no match
    return dummy.next

head = build([6, 1, 2, 6, 3, 6])
head = remove_all(head, 6)
# to_list(head) == [1, 2, 3]

# Edge: all nodes match
head = build([7, 7, 7])
head = remove_all(head, 7)
# head is None
```

**Why:** Without the dummy node, you would need a separate `while head and head.val == val` loop to handle deletions at the front. The dummy makes the head just another `curr.next`.

**Time:** O(n). **Space:** O(1).

</details>

---

## Advanced (Q21–Q25)

---

<a id="q21"></a>
### Q21

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


**Deep copy a linked list where each node has `val`, `next`, and `random` (points to any node in the list or `None`). Return the head of the copy.**

<details>
<summary>💡 Hint</summary>

Two-pass approach using a hash map: pass 1 creates all new nodes; pass 2 wires `next` and `random` using the map from old nodes to new nodes.

</details>

<details>
<summary>✅ Answer</summary>

```python
class RandomNode:
    def __init__(self, val=0, next=None, random=None):
        self.val = val
        self.next = next
        self.random = random

def copy_random_list(head):
    if not head:
        return None

    old_to_new = {}

    # Pass 1: create every new node (no wiring yet)
    curr = head
    while curr:
        old_to_new[curr] = RandomNode(curr.val)
        curr = curr.next

    # Pass 2: wire next and random using the map
    curr = head
    while curr:
        if curr.next:
            old_to_new[curr].next = old_to_new[curr.next]
        if curr.random:
            old_to_new[curr].random = old_to_new[curr.random]
        curr = curr.next

    return old_to_new[head]
```

**Why:** The random pointer can point to any node including ones not yet copied, so you cannot wire it in one pass. The hash map maps every old node to its new clone so both `next` and `random` can be resolved in O(1).

**Time:** O(n). **Space:** O(n) for the hash map.

</details>

---

<a id="q22"></a>
### Q22

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


**Given a linked list with a cycle, find the node where the cycle begins. Return that node.**

<details>
<summary>💡 Hint</summary>

Step 1: Floyd's detection — find where slow and fast meet. Step 2: reset one pointer to `head` and advance both at speed 1. They meet at the cycle start.

</details>

<details>
<summary>✅ Answer</summary>

```python
def find_cycle_start(head):
    slow = fast = head

    # Phase 1: detect the cycle
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None   # no cycle

    # Phase 2: find cycle start
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    return slow   # cycle start node

# Math: if head-to-cycle-start = F, and meeting point is M steps into cycle,
# then resetting one pointer to head and stepping both at speed 1
# causes them to meet exactly at the cycle start after F more steps.
```

**Why:** The mathematical proof shows that the distance from the meeting point back to the cycle start equals the distance from the head to the cycle start. So both pointers converge at the start when moved at equal speeds.

**Time:** O(n). **Space:** O(1).

</details>

---

<a id="q23"></a>
### Q23

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


**Reverse a linked list in groups of k. If the final group has fewer than k nodes, leave it as-is.**

<details>
<summary>💡 Hint</summary>

Check if k nodes exist before reversing. Reverse exactly k nodes using the standard 3-pointer method. Recursively handle the rest.

</details>

<details>
<summary>✅ Answer</summary>

```python
def reverse_k_group(head, k):
    # Check if at least k nodes remain
    curr, count = head, 0
    while curr and count < k:
        curr = curr.next
        count += 1
    if count < k:
        return head   # fewer than k nodes — leave as-is

    # Reverse exactly k nodes
    prev, curr = None, head
    for _ in range(k):
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt

    # head is now the tail of the reversed group
    # curr is the head of the remaining list
    head.next = reverse_k_group(curr, k)
    return prev   # prev is the new head of the reversed group

# build([1,2,3,4,5]), k=2 → [2,1,4,3,5]
# build([1,2,3,4,5]), k=3 → [3,2,1,4,5]
```

**Why:** After reversing k nodes, the original `head` is now the tail of the reversed group. Recursion handles the rest and `head.next` stitches the groups together.

**Time:** O(n). **Space:** O(n/k) recursive call stack.

</details>

---

<a id="q24"></a>
### Q24

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


**Flatten a multilevel doubly linked list. Each node may have a `child` pointer pointing to another doubly linked list. The flattened list should follow depth-first order.**

<details>
<summary>💡 Hint</summary>

When you encounter a node with a `child`, insert the child list between the current node and `curr.next`. Find the tail of the child list first, then rewire four pointers.

</details>

<details>
<summary>✅ Answer</summary>

```python
class MLNode:
    def __init__(self, val=0, prev=None, next=None, child=None):
        self.val = val
        self.prev = prev
        self.next = next
        self.child = child

def flatten(head):
    curr = head
    while curr:
        if curr.child:
            child_head = curr.child
            child_tail = child_head
            while child_tail.next:        # find tail of child list
                child_tail = child_tail.next

            # Insert child list between curr and curr.next
            next_node = curr.next
            curr.next = child_head
            child_head.prev = curr
            child_tail.next = next_node
            if next_node:
                next_node.prev = child_tail
            curr.child = None             # clear the child pointer
        curr = curr.next
    return head
```

**Why:** Depth-first flattening means fully inserting each child sublist before continuing. By wiring `curr → child_head ↔ ... ↔ child_tail → next_node`, we merge the sublist inline and the main traversal naturally continues into it.

**Time:** O(n) where n is total nodes across all levels. **Space:** O(1).

</details>

---

<a id="q25"></a>
### Q25

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


**Implement an LRU (Least Recently Used) cache with O(1) `get` and O(1) `put` using a doubly linked list and a hash map.**

<details>
<summary>💡 Hint</summary>

Use sentinel head (MRU side) and tail (LRU side) nodes. On every `get` or `put`, move the node to just after the head. On eviction, remove from just before the tail.

</details>

<details>
<summary>✅ Answer</summary>

```python
class DLNode:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map = {}                      # key → DLNode
        self.head = DLNode()               # sentinel: MRU side
        self.tail = DLNode()               # sentinel: LRU side
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node)
        self._insert_front(node)           # mark as most recently used
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            self._remove(self.map[key])
        node = DLNode(key, value)
        self.map[key] = node
        self._insert_front(node)
        if len(self.map) > self.cap:
            lru = self.tail.prev           # node just before tail = LRU
            self._remove(lru)
            del self.map[lru.key]

# cache = LRUCache(2)
# cache.put(1, 1); cache.put(2, 2)
# cache.get(1)        → 1 (moves 1 to front)
# cache.put(3, 3)     → evicts key 2
# cache.get(2)        → -1 (evicted)
```

**Why:** The hash map gives O(1) lookup; the doubly linked list gives O(1) insert and remove at any position (because you have both `prev` and `next`). Sentinel nodes eliminate all edge cases for empty list and single-node list.

**Time:** O(1) get and put. **Space:** O(capacity).

</details>

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Stack — Theory →](../08_stack/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md) · [Practice Local](./practice_local.py)
