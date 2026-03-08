# Binary Search Trees — Cheatsheet

---

## BST Property

```
For every node N:
  ALL values in left subtree  < N.val
  ALL values in right subtree > N.val

         8
        / \
       3   10
      / \    \
     1   6    14
        / \   /
       4   7 13

Inorder traversal → [1, 3, 4, 6, 7, 8, 10, 13, 14]  ← SORTED
```

---

## Operations Complexity

| Operation | Average (balanced) | Worst Case (skewed) |
|-----------|--------------------|---------------------|
| Search    | O(log n)           | O(n)                |
| Insert    | O(log n)           | O(n)                |
| Delete    | O(log n)           | O(n)                |
| Min/Max   | O(log n)           | O(n)                |
| Inorder   | O(n)               | O(n)                |
| Space     | O(n)               | O(n)                |

Worst case: sorted input creates a linked list (no balancing).
Self-balancing (AVL, Red-Black) guarantees O(log n) always.

---

## Python TreeNode

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

---

## BST Operations Templates

### Search

```python
def search(root, target):
    if not root or root.val == target:
        return root
    if target < root.val:
        return search(root.left, target)    # go left
    return search(root.right, target)       # go right

# Iterative — O(h) space saved
def search_iter(root, target):
    while root:
        if target == root.val: return root
        root = root.left if target < root.val else root.right
    return None
```

### Insert

```python
def insert(root, val):
    if not root:
        return TreeNode(val)                # create node here
    if val < root.val:
        root.left = insert(root.left, val)
    elif val > root.val:
        root.right = insert(root.right, val)
    # equal: BST typically doesn't allow duplicates (or goes right)
    return root
```

### Delete

```python
def delete(root, key):
    if not root: return None
    if key < root.val:
        root.left = delete(root.left, key)
    elif key > root.val:
        root.right = delete(root.right, key)
    else:                                   # found node to delete
        if not root.left:  return root.right   # no left child
        if not root.right: return root.left    # no right child
        # two children: replace with inorder successor (min of right)
        successor = root.right
        while successor.left:
            successor = successor.left
        root.val = successor.val            # copy successor value
        root.right = delete(root.right, successor.val)  # delete successor
    return root

# Deletion cases:
# Case 1: leaf node          → just remove (return None)
# Case 2: one child          → replace with that child
# Case 3: two children       → replace with inorder successor (min in right)
```

### Find Min / Max

```python
def find_min(root):
    while root.left:
        root = root.left
    return root                             # leftmost node

def find_max(root):
    while root.right:
        root = root.right
    return root                             # rightmost node
```

---

## Inorder = Sorted Order

```python
# Core insight: inorder traversal of BST gives sorted sequence
def inorder(root):
    if not root: return []
    return inorder(root.left) + [root.val] + inorder(root.right)

# In-place inorder with generator (memory efficient)
def inorder_gen(root):
    if root:
        yield from inorder_gen(root.left)
        yield root.val
        yield from inorder_gen(root.right)

# Use this to: verify BST, find kth smallest, convert to sorted array
```

---

## Validate BST

```python
# Wrong approach: only check immediate children
# Right approach: pass min/max bounds down the tree

def is_valid_bst(root, min_val=float('-inf'), max_val=float('inf')):
    if not root: return True
    if not (min_val < root.val < max_val):
        return False
    return (is_valid_bst(root.left,  min_val, root.val) and
            is_valid_bst(root.right, root.val, max_val))

# Alternative: inorder traversal must be strictly increasing
def is_valid_bst_inorder(root):
    prev = [float('-inf')]
    def inorder(node):
        if not node: return True
        if not inorder(node.left): return False
        if node.val <= prev[0]: return False    # not strictly increasing
        prev[0] = node.val
        return inorder(node.right)
    return inorder(root)
```

---

## Kth Smallest Element

```python
def kth_smallest(root, k):
    # Inorder gives sorted — return kth element
    count = [0]
    result = [None]
    def inorder(node):
        if not node or result[0] is not None: return
        inorder(node.left)
        count[0] += 1
        if count[0] == k:
            result[0] = node.val
            return
        inorder(node.right)
    inorder(root)
    return result[0]
# Time: O(k + h), Space: O(h)
```

---

## LCA in BST (Simpler than General Tree)

```python
# BST property lets us decide direction without searching both subtrees
def lca_bst(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left            # both in left subtree
        elif p.val > root.val and q.val > root.val:
            root = root.right           # both in right subtree
        else:
            return root                 # split point = LCA
    return None
# Time: O(h), no recursion stack needed
```

---

## BST to Greater Sum Tree (Reverse Inorder)

```python
# Each node's value becomes sum of all values >= itself
# Traverse in reverse inorder: right → root → left

def bst_to_gst(root):
    running = [0]
    def reverse_inorder(node):
        if not node: return
        reverse_inorder(node.right)     # process right first (larger vals)
        running[0] += node.val
        node.val = running[0]
        reverse_inorder(node.left)
    reverse_inorder(root)
    return root
```

---

## Floor and Ceiling in BST

```python
def floor_bst(root, key):
    # Largest value <= key
    floor = None
    while root:
        if root.val == key: return root.val
        elif root.val < key:
            floor = root.val            # candidate — go right for closer
            root = root.right
        else:
            root = root.left            # too large — go left
    return floor

def ceiling_bst(root, key):
    # Smallest value >= key
    ceil = None
    while root:
        if root.val == key: return root.val
        elif root.val > key:
            ceil = root.val             # candidate — go left for closer
            root = root.left
        else:
            root = root.right           # too small — go right
    return ceil
```

---

## Convert Sorted Array to Balanced BST

```python
def sorted_array_to_bst(nums):
    if not nums: return None
    mid = len(nums) // 2
    root = TreeNode(nums[mid])
    root.left  = sorted_array_to_bst(nums[:mid])
    root.right = sorted_array_to_bst(nums[mid+1:])
    return root
# Choosing mid as root guarantees balanced height
```

---

## BST vs Sorted Array vs Hash Map

| Operation        | BST (balanced)  | Sorted Array    | Hash Map       |
|------------------|-----------------|-----------------|----------------|
| Search           | O(log n)        | O(log n)        | O(1) avg       |
| Insert           | O(log n)        | O(n)            | O(1) avg       |
| Delete           | O(log n)        | O(n)            | O(1) avg       |
| Min / Max        | O(log n)        | O(1)            | O(n)           |
| Floor / Ceiling  | O(log n)        | O(log n)        | O(n)           |
| Ordered iteration| O(n)            | O(n)            | O(n log n)     |
| Space            | O(n)            | O(n)            | O(n)           |

Use BST when: need ordered data + frequent insert/delete + range queries.
Use sorted array when: static data + binary search + O(1) min/max.
Use hash map when: only exact lookup + no ordering needed.

---

## Self-Balancing BSTs (Conceptual)

### AVL Tree
- Strict balance: |height(left) - height(right)| <= 1 at every node
- Rotations: LL, RR, LR, RL (single/double rotations)
- More rotations on insert/delete → faster reads
- Use case: read-heavy workloads

### Red-Black Tree
- Color property: every node is red or black
- Rules ensure no path is 2x longer than any other
- Fewer rotations than AVL → faster writes
- Used in: Python's `sortedcontainers`, Java's `TreeMap`, Linux kernel
- Guarantees: insert O(log n), delete O(log n), search O(log n)

```
AVL vs Red-Black:
  AVL      → stricter balance → faster search → more rotations on update
  Red-Black → looser balance  → faster update → used in most stdlib implementations
```

---

## Python: sortedcontainers.SortedList (BST Substitute)

```python
from sortedcontainers import SortedList

sl = SortedList([3, 1, 4, 1, 5, 9])
sl.add(2)                              # insert O(log n)
sl.remove(1)                           # remove first 1 O(log n)
sl.discard(99)                         # remove if exists, no error
sl[0]                                  # min  O(1)
sl[-1]                                 # max  O(1)
sl.bisect_left(4)                      # index of floor/ceiling
sl.irange(2, 6)                        # range query O(log n + k)
len(sl)                                # O(1)
4 in sl                                # O(log n)

# sortedcontainers is ~10x slower than built-in list for large n
# but O(log n) insert/delete vs O(n) for list
```

---

## Common BST Interview Patterns

| Problem                              | Key Insight                                     |
|--------------------------------------|-------------------------------------------------|
| Validate BST (LC 98)                 | Pass min/max bounds; inorder must be increasing |
| Kth Smallest (LC 230)                | Inorder traversal, stop at k                    |
| LCA of BST (LC 235)                  | Compare both values to root, no full search     |
| Convert Sorted Array to BST (LC 108) | Always pick midpoint as root                    |
| BST to Greater Sum Tree (LC 538)     | Reverse inorder with running sum                |
| Delete Node in BST (LC 450)          | Three cases; inorder successor for 2-child case |
| Recover BST (LC 99)                  | Inorder finds 2 swapped nodes                   |
| Closest BST Value (LC 270)           | Walk tree, track min abs diff                   |
| Inorder Successor in BST (LC 285)    | Go right then leftmost; or track last > current |
| Range Sum of BST (LC 938)            | Prune subtrees outside [low, high]              |

---

## Common Mistakes

| Mistake                                  | Fix                                                  |
|------------------------------------------|------------------------------------------------------|
| Validate BST by checking only parent     | Must pass bounds — a node is < ALL ancestors on left  |
| Forgetting duplicate handling in insert  | Decide: duplicates go right, or ignore, or count     |
| Delete: replacing with predecessor       | Prefer inorder successor (min of right) — cleaner    |
| Off-by-one: `<=` vs `<` in valid check   | BST requires strict inequality: left < root < right  |
| Assuming BST is balanced                 | It's not unless explicitly stated / self-balancing   |
| Using inorder on non-BST for sorted data | Only valid on BSTs — general trees give unsorted     |
