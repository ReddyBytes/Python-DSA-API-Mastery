# Binary Search Trees — Practice Questions

> 25 questions covering every major BST concept and pattern.
> Work through Basic first — they build vocabulary for Intermediate and Advanced.

---

## Quick Index

| # | Topic | Level |
|---|-------|-------|
| [Q1](#q1) | BST property — left < root < right | Basic |
| [Q2](#q2) | BST property — subtree-wide, not just direct children | Basic |
| [Q3](#q3) | Search in a BST — trace the path | Basic |
| [Q4](#q4) | Insert into a BST — step by step | Basic |
| [Q5](#q5) | Find minimum and maximum | Basic |
| [Q6](#q6) | Inorder traversal gives sorted output | Basic |
| [Q7](#q7) | BST vs sorted array vs hash map — when to choose what | Basic |
| [Q8](#q8) | Worst-case O(n) — when does BST degrade? | Basic |
| [Q9](#q9) | Delete a leaf node | Intermediate |
| [Q10](#q10) | Delete a node with one child | Intermediate |
| [Q11](#q11) | Delete a node with two children — inorder successor | Intermediate |
| [Q12](#q12) | Validate BST — min/max bounds approach | Intermediate |
| [Q13](#q13) | Find the kth smallest element | Intermediate |
| [Q14](#q14) | Lowest common ancestor in a BST | Intermediate |
| [Q15](#q15) | Convert BST to sorted array | Intermediate |
| [Q16](#q16) | Range query — collect all values in [low, high] | Intermediate |
| [Q17](#q17) | Range sum — sum all values in [low, high] with pruning | Intermediate |
| [Q18](#q18) | Floor and ceiling in a BST | Intermediate |
| [Q19](#q19) | Inorder successor of a node | Intermediate |
| [Q20](#q20) | Convert sorted array to height-balanced BST | Intermediate |
| [Q21](#q21) | Find LCA using BST property vs general tree — complexity comparison | Advanced |
| [Q22](#q22) | Self-balancing trees — AVL vs Red-Black conceptual | Advanced |
| [Q23](#q23) | BST iterator — O(h) space, O(1) amortized next() | Advanced |
| [Q24](#q24) | Validate BST — inorder approach vs bounds approach | Advanced |
| [Q25](#q25) | Common mistake: treating BST like a general tree — prune don't search | Advanced |

---

## Basic (Q1–Q8)

---

<a id="q1"></a>
### Q1 — BST property: left < root < right

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


You have a BST with the following inorder values: `[2, 4, 6, 8, 10]`. The root is `6`. Draw the tree and verify the BST property holds. What must be true for every node — not just for the root?

<details>
<summary>Hint</summary>

The BST rule is not just "left child < parent". It applies to the entire subtree. Every node in the left subtree must be strictly less than the ancestor above it, all the way up.

</details>

<details>
<summary>Answer</summary>

One valid tree (from inserting in order 6, 4, 8, 2, 10):

```
        6
       / \
      4   8
     /     \
    2       10
```

**BST property (formal):** For every node X, ALL values in X's left subtree are strictly less than X, and ALL values in X's right subtree are strictly greater than X.

This is subtree-wide, not just parent-child. Node 2 must be less than both 4 and 6.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def verify_bst_property(root, min_val=float('-inf'), max_val=float('inf')):
    if not root:
        return True
    if not (min_val < root.val < max_val):
        return False
    return (verify_bst_property(root.left, min_val, root.val) and
            verify_bst_property(root.right, root.val, max_val))

root = TreeNode(6, TreeNode(4, TreeNode(2)), TreeNode(8, None, TreeNode(10)))
print(verify_bst_property(root))  # True
```

**Why:** The `min_val`/`max_val` range tightens at every level. Going left, the upper bound tightens to the parent's value. Going right, the lower bound tightens. This is the only correct way to enforce the full BST invariant.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q2"></a>
### Q2 — BST property is subtree-wide, not just direct children

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


The following tree passes a naive "check only parent-child" validation but is NOT a valid BST. Identify why and fix the validation.

```
      10
     /  \
    5    15
        /  \
       6    20
```

<details>
<summary>Hint</summary>

Node 6 has 6 > 5 and 6 < 15 locally. But what is 6's relationship to the root (10)?

</details>

<details>
<summary>Answer</summary>

Node 6 is in the **right subtree** of 10, so 6 must be **greater than 10**. But 6 < 10. Invalid BST.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# WRONG — only checks direct children
def is_valid_naive(root):
    if not root:
        return True
    if root.left and root.left.val >= root.val:
        return False
    if root.right and root.right.val <= root.val:
        return False
    return is_valid_naive(root.left) and is_valid_naive(root.right)

# CORRECT — passes bounds down
def is_valid_bst(root, lo=float('-inf'), hi=float('inf')):
    if not root:
        return True
    if not (lo < root.val < hi):
        return False
    return (is_valid_bst(root.left, lo, root.val) and
            is_valid_bst(root.right, root.val, hi))

root = TreeNode(10, TreeNode(5), TreeNode(15, TreeNode(6), TreeNode(20)))
print(is_valid_naive(root))   # True  — BUG
print(is_valid_bst(root))     # False — CORRECT
```

**Why:** The naive version says "is 6 < 15? yes, ok." But it misses the global constraint that 6 is in 10's right subtree and must therefore exceed 10. Bounds propagation carries the full ancestry constraint down to every node.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q3"></a>
### Q3 — Search in a BST: trace the path

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Given this BST, trace the path taken to search for the value `7`:

```
          8
         / \
        3   10
       / \    \
      1   6    14
         / \   /
        4   7 13
```

How many comparisons are made? What is the time complexity?

<details>
<summary>Hint</summary>

At each node, compare the target against the current value and decide left or right. You eliminate an entire subtree at each step.

</details>

<details>
<summary>Answer</summary>

Path: 8 → 3 → 6 → 7. Four comparisons.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def search_bst(root, target):
    steps = 0
    while root:
        steps += 1
        if target == root.val:
            print(f"Found {target} in {steps} steps")
            return root
        elif target < root.val:
            root = root.left
        else:
            root = root.right
    print(f"Not found after {steps} steps")
    return None
```

Trace:
- 8: 7 < 8 → go left
- 3: 7 > 3 → go right
- 6: 7 > 6 → go right
- 7: 7 == 7 → found

**Why:** BST search is binary search applied to a tree. At each node, one entire half is eliminated. For a balanced BST of n nodes, height h ≈ log n, so at most log n comparisons. Worst case (skewed tree): O(n).

**Time:** O(h) — O(log n) balanced, O(n) skewed. **Space:** O(1) iterative.

</details>

---

<a id="q4"></a>
### Q4 — Insert into a BST: step by step

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Insert the values `[5, 3, 7, 1, 4, 6, 8]` into an empty BST in that order. Draw the final tree. Then write the insert function.

<details>
<summary>Hint</summary>

The first value becomes the root. Each subsequent value navigates left when smaller, right when larger, and lands at the first empty spot.

</details>

<details>
<summary>Answer</summary>

```
          5
         / \
        3   7
       / \ / \
      1  4 6  8
```

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def insert_bst(root, val):
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = insert_bst(root.left, val)
    elif val > root.val:
        root.right = insert_bst(root.right, val)
    # equal: do nothing (no duplicates in standard BST)
    return root

root = None
for v in [5, 3, 7, 1, 4, 6, 8]:
    root = insert_bst(root, v)

def inorder(node):
    if not node: return []
    return inorder(node.left) + [node.val] + inorder(node.right)

print(inorder(root))  # [1, 3, 4, 5, 6, 7, 8]
```

**Why:** The critical pattern is `root.left = insert_bst(root.left, val)` — always assign the return value. The function returns the (possibly new) root at each level. Forgetting the assignment is the most common insert bug.

**Time:** O(h). **Space:** O(h) recursion stack.

</details>

---

<a id="q5"></a>
### Q5 — Find minimum and maximum

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Write functions to find the minimum and maximum values in a BST without traversing every node.

<details>
<summary>Hint</summary>

In a BST, smaller values are always to the left and larger values always to the right. What is the extreme case of "keep going left"?

</details>

<details>
<summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def find_min(root):
    if not root:
        return None
    while root.left:
        root = root.left
    return root.val   # leftmost node = minimum

def find_max(root):
    if not root:
        return None
    while root.right:
        root = root.right
    return root.val   # rightmost node = maximum
```

**Why:** The minimum is always the leftmost node — there is nothing smaller to its left. The maximum is always the rightmost node. This is O(h) — no need to visit every node. A hash map cannot do this in better than O(n); a BST does it in O(log n) for a balanced tree.

**Time:** O(h). **Space:** O(1).

</details>

---

<a id="q6"></a>
### Q6 — Inorder traversal gives sorted output

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Perform an inorder traversal of the BST below. Explain why the output is always sorted for any valid BST.

```
          5
         / \
        3   7
       / \ / \
      1  4 6  8
```

<details>
<summary>Hint</summary>

Inorder means: Left subtree first, then current node, then right subtree. What does the BST property guarantee about the left subtree's values relative to the root?

</details>

<details>
<summary>Answer</summary>

Inorder output: `[1, 3, 4, 5, 6, 7, 8]` — sorted ascending.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorder(root):
    if not root:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)

# Generator version — memory efficient for large trees
def inorder_gen(root):
    if root:
        yield from inorder_gen(root.left)
        yield root.val
        yield from inorder_gen(root.right)
```

**Why:** By the BST property, every value in the left subtree is smaller than the root, and every value in the right subtree is larger. Inorder processes Left → Root → Right, which visits nodes in strictly increasing order. This is the key insight that unlocks kth smallest, BST validation, conversion to sorted array, and more.

**Time:** O(n). **Space:** O(h) for the recursion stack.

</details>

---

<a id="q7"></a>
### Q7 — BST vs sorted array vs hash map

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Your team is designing a salary lookup system. Requirements: fast search, fast insert/delete, and support for "find all salaries between $60K and $90K". Which data structure do you choose and why?

<details>
<summary>Hint</summary>

A hash map gives O(1) lookup but cannot answer range queries. A sorted array supports binary search but inserts are O(n). What handles all three?

</details>

<details>
<summary>Answer</summary>

Choose a balanced BST (or Python's `sortedcontainers.SortedList`).

```
Operation           | Sorted Array  | Hash Map      | BST (balanced)
--------------------|---------------|---------------|----------------
Search              | O(log n)      | O(1) avg      | O(log n)
Insert              | O(n)          | O(1) avg      | O(log n)
Delete              | O(n)          | O(1) avg      | O(log n)
Range query [a, b]  | O(log n + k)  | O(n)          | O(log n + k)
Sorted iteration    | O(n)          | O(n log n)    | O(n)
```

```python
from sortedcontainers import SortedList

salaries = SortedList([75000, 55000, 90000, 62000, 80000])
salaries.add(70000)                     # O(log n)
in_range = list(salaries.irange(60000, 90000))
print(in_range)  # [62000, 70000, 75000, 80000, 90000]
```

**Why:** Hash maps excel at exact lookup but have zero concept of "order" — they cannot answer "give me everything between X and Y" without scanning all entries. Sorted arrays support range queries but insertions shift O(n) elements. A balanced BST handles all three requirements efficiently. This is the defining use case for BSTs over hash maps.

**Time:** Range query O(log n + k). **Space:** O(n).

</details>

---

<a id="q8"></a>
### Q8 — Worst-case O(n): when does a BST degrade?

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Insert the values `[1, 2, 3, 4, 5]` into an empty BST in that order. Draw the result. What is the search time? How do self-balancing trees fix this?

<details>
<summary>Hint</summary>

When values are inserted in sorted order, every new value is larger than the previous — it always goes to the right. What does the resulting shape look like?

</details>

<details>
<summary>Answer</summary>

```
1
 \
  2
   \
    3
     \
      4
       \
        5
```

This is a degenerate (skewed) BST — a linked list in disguise. Searching for 5 requires 5 comparisons. For n nodes: O(n).

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def insert_bst(root, val):
    if not root: return TreeNode(val)
    if val < root.val:
        root.left = insert_bst(root.left, val)
    elif val > root.val:
        root.right = insert_bst(root.right, val)
    return root

def height(root):
    if not root: return 0
    return 1 + max(height(root.left), height(root.right))

root = None
for v in [1, 2, 3, 4, 5]:
    root = insert_bst(root, v)

print(height(root))   # 5 — same as n, degenerate
```

**Fix:** AVL trees and Red-Black trees automatically rebalance after insert/delete. AVL maintains strict balance (height difference ≤ 1). Red-Black uses a looser color-based scheme with fewer rotations. Both guarantee O(log n) always. Python's `sortedcontainers` and Java's `TreeMap` use these internally.

**Time (skewed):** O(n) all operations. **Time (balanced):** O(log n).

</details>

---

## Intermediate (Q9–Q20)

---

<a id="q9"></a>
### Q9 — Delete a leaf node

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Delete the value `1` from this BST. Verify the BST property is preserved.

```
      5
     / \
    3   7
   /
  1
```

<details>
<summary>Hint</summary>

A leaf has no children. What is the only action needed?

</details>

<details>
<summary>Answer</summary>

Simply remove the node. No restructuring required.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def delete_bst(root, key):
    if not root:
        return None
    if key < root.val:
        root.left = delete_bst(root.left, key)
    elif key > root.val:
        root.right = delete_bst(root.right, key)
    else:
        # Found the node — handle deletion
        if not root.left:
            return root.right    # covers leaf (both None) and one-right-child
        if not root.right:
            return root.left
        # Two children — covered in Q11
        successor = root.right
        while successor.left:
            successor = successor.left
        root.val = successor.val
        root.right = delete_bst(root.right, successor.val)
    return root

def inorder(node):
    return [] if not node else inorder(node.left) + [node.val] + inorder(node.right)

root = TreeNode(5, TreeNode(3, TreeNode(1)), TreeNode(7))
root = delete_bst(root, 1)
print(inorder(root))  # [3, 5, 7]
```

**Why:** A leaf node has no children, so returning `None` from the recursive call effectively snips it from its parent. The pattern `root.left = delete(root.left, key)` propagates the change up. The leaf case falls naturally out of `if not root.left: return root.right` (both children are None).

**Time:** O(h). **Space:** O(h).

</details>

---

<a id="q10"></a>
### Q10 — Delete a node with one child

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Delete the value `3` from this BST (node 3 has only one child: node 2).

```
      5
     / \
    3   7
   /
  2
```

<details>
<summary>Hint</summary>

The node being deleted has exactly one child. The fix is like removing a link from a chain — connect the parent directly to the grandchild.

</details>

<details>
<summary>Answer</summary>

Replace node 3 with its only child (node 2). The parent (5) now points directly to 2.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def delete_bst(root, key):
    if not root:
        return None
    if key < root.val:
        root.left = delete_bst(root.left, key)
    elif key > root.val:
        root.right = delete_bst(root.right, key)
    else:
        if not root.left:
            return root.right   # no left child: replace with right (even if None)
        if not root.right:
            return root.left    # no right child: replace with left
        # two children handled in Q11
    return root

def inorder(node):
    return [] if not node else inorder(node.left) + [node.val] + inorder(node.right)

root = TreeNode(5, TreeNode(3, TreeNode(2)), TreeNode(7))
root = delete_bst(root, 3)
print(inorder(root))  # [2, 5, 7]
```

**Why:** When a node has one child, the node is simply bypassed. `return root.left` (or `root.right`) hands the single child directly to the caller, which assigns it to the deleted node's parent pointer. BST property holds because the child's values still satisfy the ordering relative to all ancestors.

**Time:** O(h). **Space:** O(h).

</details>

---

<a id="q11"></a>
### Q11 — Delete a node with two children

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Delete the value `5` (the root) from this BST. Explain the inorder successor strategy.

```
          5
         / \
        3   7
       / \ / \
      2  4 6  8
```

<details>
<summary>Hint</summary>

When a node has two children, you need a replacement that maintains BST order. What is the smallest value that is still larger than everything in the left subtree?

</details>

<details>
<summary>Answer</summary>

The inorder successor of 5 is 6 (smallest in the right subtree). Copy 6 into the root's position, then delete 6 from the right subtree (which is a leaf — Case 1).

```
Before: [2, 3, 4, 5, 6, 7, 8]   After: [2, 3, 4, 6, 7, 8]
```

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def delete_bst(root, key):
    if not root:
        return None
    if key < root.val:
        root.left = delete_bst(root.left, key)
    elif key > root.val:
        root.right = delete_bst(root.right, key)
    else:
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        # Two children: find inorder successor (min of right subtree)
        successor = root.right
        while successor.left:
            successor = successor.left
        root.val = successor.val                         # copy successor value
        root.right = delete_bst(root.right, successor.val)  # delete successor
    return root

def inorder(node):
    return [] if not node else inorder(node.left) + [node.val] + inorder(node.right)

root = TreeNode(5,
    TreeNode(3, TreeNode(2), TreeNode(4)),
    TreeNode(7, TreeNode(6), TreeNode(8)))
root = delete_bst(root, 5)
print(inorder(root))  # [2, 3, 4, 6, 7, 8]
```

**Why:** The inorder successor is the smallest value greater than the deleted node. It is always greater than everything in the left subtree (maintains the left-side ordering) and fits naturally into the deleted node's position. The critical step often forgotten: after copying the successor's value, you must delete the successor from the right subtree or it appears twice.

**Time:** O(h). **Space:** O(h).

</details>

---

<a id="q12"></a>
### Q12 — Validate BST using min/max bounds

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Write a function to validate whether a given binary tree is a valid BST. Use the min/max bounds approach. Show a case where checking only immediate children fails.

<details>
<summary>Hint</summary>

Every node needs to know not just its parent's value, but the full valid range inherited from all ancestors above it.

</details>

<details>
<summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def is_valid_bst(root, lo=float('-inf'), hi=float('inf')):
    if not root:
        return True
    if not (lo < root.val < hi):
        return False
    return (is_valid_bst(root.left, lo, root.val) and
            is_valid_bst(root.right, root.val, hi))

# Case where naive check fails:
#       10
#      /  \
#     5    15
#          /
#          6   ← 6 < 10 but in right subtree — INVALID
invalid = TreeNode(10, TreeNode(5), TreeNode(15, TreeNode(6)))
print(is_valid_bst(invalid))  # False — correct

# Valid BST
valid = TreeNode(4,
    TreeNode(2, TreeNode(1), TreeNode(3)),
    TreeNode(6, TreeNode(5), TreeNode(7)))
print(is_valid_bst(valid))    # True — correct
```

**Why:** When going left, the current node's value becomes the new upper bound. When going right, it becomes the new lower bound. Node 6 is in the right subtree of 10, so it inherits the lower bound of 10. Since 6 < 10, validation fails correctly.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q13"></a>
### Q13 — Find the kth smallest element

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Given a BST, find the kth smallest element. The BST has n nodes. Implement with O(h + k) time and O(h) space.

<details>
<summary>Hint</summary>

The key insight: inorder traversal of a BST visits nodes in sorted order. The kth node visited in inorder is the kth smallest.

</details>

<details>
<summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def kth_smallest(root, k):
    stack = []
    current = root
    count = 0

    while stack or current:
        while current:              # go as far left as possible
            stack.append(current)
            current = current.left

        current = stack.pop()
        count += 1

        if count == k:
            return current.val      # kth node in inorder = kth smallest

        current = current.right

    return -1   # k out of bounds

# BST:       5
#           / \
#          3   7
#         / \ / \
#        2  4 6  8
root = TreeNode(5,
    TreeNode(3, TreeNode(2), TreeNode(4)),
    TreeNode(7, TreeNode(6), TreeNode(8)))

print(kth_smallest(root, 1))  # 2
print(kth_smallest(root, 3))  # 4
print(kth_smallest(root, 5))  # 6
```

**Why:** The iterative inorder traversal visits nodes in ascending order and stops as soon as the kth node is reached — it does not traverse the entire tree. The stack simulates the call stack. Time is O(h + k): O(h) to reach the leftmost node, O(k) to count k nodes. Much better than converting to array (O(n) space).

**Time:** O(h + k). **Space:** O(h).

</details>

---

<a id="q14"></a>
### Q14 — Lowest common ancestor in a BST

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


Find the LCA of nodes 2 and 8 in this BST. Then find the LCA of 0 and 4. Implement using the BST property (not general tree LCA).

```
           6
          / \
         2   8
        / \ / \
       0  4 7  9
         / \
        3   5
```

<details>
<summary>Hint</summary>

At each node, if both targets are smaller, go left. If both are larger, go right. Otherwise, the current node is the split point — that is the LCA.

</details>

<details>
<summary>Answer</summary>

LCA(2, 8) = 6 (the root is the split point).
LCA(0, 4) = 2 (0 < 2 and 4 > 2, split at 2).

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def lca_bst(root, p, q):
    while root:
        if p < root.val and q < root.val:
            root = root.left    # both in left subtree
        elif p > root.val and q > root.val:
            root = root.right   # both in right subtree
        else:
            return root.val     # split point = LCA

root = TreeNode(6,
    TreeNode(2, TreeNode(0), TreeNode(4, TreeNode(3), TreeNode(5))),
    TreeNode(8, TreeNode(7), TreeNode(9)))

print(lca_bst(root, 2, 8))  # 6
print(lca_bst(root, 0, 4))  # 2
print(lca_bst(root, 3, 5))  # 4
print(lca_bst(root, 7, 9))  # 8
```

**Why:** The BST property tells us exactly which subtree contains each node — no exploration needed. If both p and q are less than the current node, they are both in the left subtree, so the LCA must also be there. The split point (where p and q go in different directions) is guaranteed to be the LCA. This is O(h) vs O(n) for general tree LCA.

**Time:** O(h). **Space:** O(1).

</details>

---

<a id="q15"></a>
### Q15 — Convert BST to sorted array

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


Convert a BST to a sorted array. What is the minimum possible time complexity, and why?

<details>
<summary>Hint</summary>

Inorder traversal of a BST yields values in sorted order. Since you must visit every node, the lower bound is O(n).

</details>

<details>
<summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def bst_to_sorted_array(root):
    result = []

    def inorder(node):
        if not node:
            return
        inorder(node.left)
        result.append(node.val)
        inorder(node.right)

    inorder(root)
    return result

# Using a generator for memory efficiency with large trees
def bst_to_sorted_gen(root):
    if root:
        yield from bst_to_sorted_gen(root.left)
        yield root.val
        yield from bst_to_sorted_gen(root.right)

root = TreeNode(5,
    TreeNode(3, TreeNode(2), TreeNode(4)),
    TreeNode(7, TreeNode(6), TreeNode(8)))

print(bst_to_sorted_array(root))          # [2, 3, 4, 5, 6, 7, 8]
print(list(bst_to_sorted_gen(root)))      # [2, 3, 4, 5, 6, 7, 8]
```

**Why:** The inorder traversal (Left → Root → Right) visits every node exactly once. By the BST property, it visits them in ascending order, so no sorting step is needed. Minimum time is O(n) — you must at least read every value. The generator version avoids building the full list in memory, streaming one value at a time.

**Time:** O(n). **Space:** O(h) for recursion stack, O(n) for the output array.

</details>

---

<a id="q16"></a>
### Q16 — Range query: collect all values in [low, high]

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Given a BST, collect all values in the range `[6, 10]`. Use BST-aware pruning — do not visit nodes that are guaranteed to be outside the range.

```
             10
            /  \
           5    15
          / \  /  \
         3   7 13  18
            / \
           6   8
```

<details>
<summary>Hint</summary>

If the current node's value is less than `low`, nothing in its left subtree can be in range — skip left. If the current value exceeds `high`, skip right.

</details>

<details>
<summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def range_query(root, low, high):
    result = []

    def dfs(node):
        if not node:
            return
        if node.val > low:      # left subtree might have values >= low
            dfs(node.left)
        if low <= node.val <= high:
            result.append(node.val)
        if node.val < high:     # right subtree might have values <= high
            dfs(node.right)

    dfs(root)
    return result   # already sorted (inorder pattern)

root = TreeNode(10,
    TreeNode(5, TreeNode(3), TreeNode(7, TreeNode(6), TreeNode(8))),
    TreeNode(15, TreeNode(13), TreeNode(18)))

print(range_query(root, 6, 10))   # [6, 7, 8, 10]
print(range_query(root, 1, 5))    # [3, 5]
print(range_query(root, 13, 18))  # [13, 15, 18]
```

**Why:** The naive approach (full inorder, then filter) visits all n nodes. The BST-aware version prunes: when `node.val <= low`, the entire left subtree is below `low` and can be skipped. When `node.val >= high`, the entire right subtree is above `high`. For sparse ranges, this can be close to O(log n + k) where k is the result count.

**Time:** O(log n + k) average. **Space:** O(h).

</details>

---

<a id="q17"></a>
### Q17 — Range sum with pruning

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


Find the sum of all values in a BST that fall within `[low, high]`. Implement with BST pruning and compare against a naive full traversal.

<details>
<summary>Hint</summary>

Same pruning logic as Q16, but accumulate the sum instead of collecting values.

</details>

<details>
<summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def range_sum_bst(root, low, high):
    if not root:
        return 0
    total = 0
    if low <= root.val <= high:
        total += root.val
    if root.val > low:
        total += range_sum_bst(root.left, low, high)
    if root.val < high:
        total += range_sum_bst(root.right, low, high)
    return total

# Naive for comparison
def range_sum_naive(root, low, high):
    if not root:
        return 0
    total = 0
    if low <= root.val <= high:
        total += root.val
    total += range_sum_naive(root.left, low, high)   # always recurses
    total += range_sum_naive(root.right, low, high)  # always recurses
    return total

root = TreeNode(10,
    TreeNode(5, TreeNode(3), TreeNode(7)),
    TreeNode(15, TreeNode(13), TreeNode(18)))

print(range_sum_bst(root, 7, 15))    # 7 + 10 + 13 + 15 = 45
print(range_sum_naive(root, 7, 15))  # same result, visits all nodes
```

**Why:** The pruned version skips the left subtree of node 5 (since 5 <= 7, values left of 5 are all < 7, below our range). It also skips the right subtree of 15 (since 15 >= 15, values right of 15 are all > 15). This is the LeetCode #938 "Range Sum of BST" problem — a classic pruning exercise.

**Time:** O(n) worst case (range covers all), O(log n + k) average. **Space:** O(h).

</details>

---

<a id="q18"></a>
### Q18 — Floor and ceiling in a BST

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Find the floor (largest value ≤ target) and ceiling (smallest value ≥ target) for target = 9 in this BST: `[8, 12, 3, 14, 5, 10]`.

<details>
<summary>Hint</summary>

For floor: when the current node is smaller than the target, it is a candidate. Keep going right to find a closer (larger) candidate. For ceiling: when the current node is larger, it is a candidate — go left to find a smaller one.

</details>

<details>
<summary>Answer</summary>

Floor of 9 = 8. Ceiling of 9 = 10.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def floor_bst(root, key):
    floor = None
    while root:
        if root.val == key:
            return root.val         # exact match is its own floor
        elif root.val < key:
            floor = root.val        # candidate — go right for a closer one
            root = root.right
        else:
            root = root.left        # too large — go left
    return floor

def ceiling_bst(root, key):
    ceil = None
    while root:
        if root.val == key:
            return root.val
        elif root.val > key:
            ceil = root.val         # candidate — go left for a smaller one
            root = root.left
        else:
            root = root.right       # too small — go right
    return ceil

def insert_bst(root, val):
    if not root: return TreeNode(val)
    if val < root.val: root.left = insert_bst(root.left, val)
    elif val > root.val: root.right = insert_bst(root.right, val)
    return root

root = None
for v in [8, 12, 3, 14, 5, 10]:
    root = insert_bst(root, v)

print(floor_bst(root, 9))    # 8
print(ceiling_bst(root, 9))  # 10
print(floor_bst(root, 3))    # 3 (exact match)
```

**Why:** Floor and ceiling are O(h) operations that exploit BST structure. When the current value is too small for floor, it's still a valid candidate (it's ≤ key) but something in the right subtree might be closer. This is used in database range scans (find first key ≥ X) and in interval scheduling.

**Time:** O(h). **Space:** O(1).

</details>

---

<a id="q19"></a>
### Q19 — Inorder successor of a node

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Find the inorder successor (next larger element in BST ordering) of node 4 in this BST:

```
          6
         / \
        2   8
       / \
      0   4
         / \
        3   5
```

<details>
<summary>Hint</summary>

Case 1: if the node has a right subtree, the successor is the minimum of that subtree. Case 2: if not, the successor is the lowest ancestor for which this node is in the left subtree.

</details>

<details>
<summary>Answer</summary>

Successor of 4 = 5 (minimum of 4's right subtree).

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorder_successor(root, target_val):
    successor = None
    node = root
    while node:
        if target_val < node.val:
            successor = node       # this node could be the successor
            node = node.left       # try to find a smaller one
        elif target_val > node.val:
            node = node.right
        else:
            # Found the target
            if node.right:
                # Case 1: right subtree exists — min of right subtree
                node = node.right
                while node.left:
                    node = node.left
                return node.val
            break                  # Case 2: tracked via successor variable
    return successor.val if successor else None

root = TreeNode(6,
    TreeNode(2, TreeNode(0), TreeNode(4, TreeNode(3), TreeNode(5))),
    TreeNode(8))

print(inorder_successor(root, 4))  # 5 (min of right subtree)
print(inorder_successor(root, 5))  # 6 (no right child, ancestor tracking)
print(inorder_successor(root, 8))  # None (8 is max)
```

**Why:** The successor is used in delete (to replace a two-child node) and in BST iterator implementations. The two-case logic — right subtree exists vs. ancestor tracking — covers all situations. The ancestor tracking case works because as you search for the target, every left turn sets a potential successor.

**Time:** O(h). **Space:** O(1).

</details>

---

<a id="q20"></a>
### Q20 — Convert sorted array to height-balanced BST

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


Convert `[-10, -3, 0, 5, 9]` to a height-balanced BST. Verify the result is balanced.

<details>
<summary>Hint</summary>

To get a balanced tree, always pick the midpoint of the current subarray as the root. The left half becomes the left subtree, the right half becomes the right subtree.

</details>

<details>
<summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def sorted_array_to_bst(nums):
    def build(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        root = TreeNode(nums[mid])
        root.left  = build(lo, mid - 1)
        root.right = build(mid + 1, hi)
        return root
    return build(0, len(nums) - 1)

def height(root):
    if not root: return 0
    return 1 + max(height(root.left), height(root.right))

def is_balanced(root):
    if not root: return True
    lh, rh = height(root.left), height(root.right)
    return abs(lh - rh) <= 1 and is_balanced(root.left) and is_balanced(root.right)

def inorder(root):
    return [] if not root else inorder(root.left) + [root.val] + inorder(root.right)

nums = [-10, -3, 0, 5, 9]
root = sorted_array_to_bst(nums)
print(inorder(root))       # [-10, -3, 0, 5, 9] — still sorted
print(is_balanced(root))   # True
print(f"height: {height(root)}")   # 3 (optimal for 5 nodes)
```

Result tree:
```
        0
       / \
     -3   9
     /   /
   -10   5
```

**Why:** Choosing the midpoint as the root ensures both halves have equal (or ±1) number of nodes, which gives minimum height. This is the divide-and-conquer pattern: each recursive call halves the problem. LeetCode #108. Height is ⌈log₂(n)⌉ — guaranteed balanced.

**Time:** O(n). **Space:** O(log n) recursion stack.

</details>

---

## Advanced (Q21–Q25)

---

<a id="q21"></a>
### Q21 — LCA: BST-specific O(h) vs general tree O(n)

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Explain why using the general binary tree LCA algorithm on a BST problem is a red flag in an interview. Implement both versions, compare the complexity, and show what the BST version exploits.

<details>
<summary>Hint</summary>

The general LCA must visit every node in the worst case because it has no information about where p and q live. The BST version can navigate directly using value comparisons.

</details>

<details>
<summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# General tree LCA — O(n): visits every node, works for any binary tree
def lca_general(root, p, q):
    if not root:
        return None
    if root.val == p or root.val == q:
        return root
    left = lca_general(root.left, p, q)
    right = lca_general(root.right, p, q)
    if left and right:
        return root         # p in left subtree, q in right subtree
    return left if left else right

# BST-specific LCA — O(h): exploits ordering property
def lca_bst(root, p, q):
    while root:
        if p < root.val and q < root.val:
            root = root.left        # both smaller → go left
        elif p > root.val and q > root.val:
            root = root.right       # both larger → go right
        else:
            return root.val         # split point = LCA

root = TreeNode(6,
    TreeNode(2, TreeNode(0), TreeNode(4, TreeNode(3), TreeNode(5))),
    TreeNode(8, TreeNode(7), TreeNode(9)))

print(lca_bst(root, 0, 5))     # 2
print(lca_bst(root, 0, 8))     # 6
print(lca_bst(root, 3, 5))     # 4

# Verify same results
assert lca_general(root, 0, 5).val == lca_bst(root, 0, 5)
assert lca_general(root, 3, 5).val == lca_bst(root, 3, 5)
```

```
Complexity comparison:
General tree LCA  → O(n) time, O(h) space  (must potentially visit every node)
BST LCA           → O(h) time, O(1) space  (follows one path from root)

For balanced BST: h = O(log n), so BST LCA is O(log n) vs O(n)
```

**Why:** Using general LCA on a BST signals you did not recognize or exploit the BST property. The BST version navigates like a search: at each step it knows which subtree contains the split. This is the difference between a candidate who understands trees generically vs. one who understands BSTs specifically.

**Time:** O(h). **Space:** O(1).

</details>

---

<a id="q22"></a>
### Q22 — Self-balancing trees: AVL vs Red-Black (conceptual)

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


You need to implement a production leaderboard that supports O(log n) insert, delete, and rank queries. You are told to use a self-balancing BST. Explain AVL vs Red-Black trade-offs conceptually. When would you choose one over the other?

<details>
<summary>Hint</summary>

Consider how strict each tree is about balance. Stricter balance means faster search, but more work on insert/delete. Looser balance means cheaper updates.

</details>

<details>
<summary>Answer</summary>

```
AVL Tree
  Balance rule: |height(left) - height(right)| ≤ 1 at every node
  Guarantee:    Height ≤ 1.44 * log₂(n) — very tight
  Rotations:    Up to O(log n) per insert/delete to rebalance
  Best for:     Read-heavy workloads (lookup >> insert/delete)
  Trade-off:    More rotations on writes → higher constant factor

Red-Black Tree
  Balance rule: Color-based (no path is 2x longer than any other)
  Guarantee:    Height ≤ 2 * log₂(n) — slightly looser
  Rotations:    At most 3 per insert, at most O(log n) per delete
  Best for:     Write-heavy or mixed workloads
  Used in:      Java TreeMap, C++ std::map, Linux process scheduler,
                Python sortedcontainers (internally uses a different structure)

Practical Python answer:
```

```python
# Python does not expose AVL or Red-Black trees directly.
# Use sortedcontainers.SortedList for BST-like behavior:
from sortedcontainers import SortedList

leaderboard = SortedList()
leaderboard.add(4200)   # O(log n) insert
leaderboard.add(3800)
leaderboard.add(5100)

# Rank: how many scores below 4200?
rank = leaderboard.bisect_left(4200)
print(f"rank (0-indexed from bottom): {rank}")  # 1

# Top 2
print(list(leaderboard)[-2:])  # [4200, 5100]
```

**Why:** For a leaderboard with frequent inserts and rank queries, Red-Black is typically preferred in production (used in databases). AVL is preferred in lookup-intensive systems like in-memory databases. The distinction matters at scale — at small n (< 10,000 nodes), the difference is negligible.

**Time (both):** O(log n) insert/delete/search. **Space:** O(n).

</details>

---

<a id="q23"></a>
### Q23 — BST iterator with O(h) space

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Implement a `BSTIterator` class that returns the next smallest element on each call to `next()`. Use O(h) space, not O(n). Each `next()` call must be O(1) amortized.

<details>
<summary>Hint</summary>

Do not flatten the BST to an array (that uses O(n) space). Instead, simulate the inorder traversal using an explicit stack. Only push the current node and its left-chain, not the entire tree.

</details>

<details>
<summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class BSTIterator:
    def __init__(self, root):
        self._stack = []
        self._push_left(root)   # push root's left chain

    def _push_left(self, node):
        while node:
            self._stack.append(node)
            node = node.left

    def next(self):
        node = self._stack.pop()
        if node.right:
            self._push_left(node.right)   # prepare next batch
        return node.val

    def has_next(self):
        return bool(self._stack)

root = TreeNode(7,
    TreeNode(3, TreeNode(1), TreeNode(5)),
    TreeNode(15, TreeNode(9), TreeNode(20)))

it = BSTIterator(root)
output = []
while it.has_next():
    output.append(it.next())
print(output)  # [1, 3, 5, 7, 9, 15, 20]
```

**Why:** The stack at any moment holds the "left spine" from the current position downward — at most h nodes. Each node is pushed and popped exactly once over the lifetime of the iterator, giving O(1) amortized per `next()`. This is used in LeetCode #173 and in actual database cursor implementations where you stream sorted rows without loading all of them.

**Time:** O(1) amortized per next(). **Space:** O(h).

</details>

---

<a id="q24"></a>
### Q24 — Two approaches to BST validation: which is better?

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


There are two correct approaches to validating a BST: (1) bounds propagation and (2) inorder traversal strictly increasing check. Implement both. When does each have an advantage?

<details>
<summary>Hint</summary>

The inorder approach can exit early as soon as it finds a violation — it does not need to traverse the full tree. The bounds approach is top-down; the inorder approach is left-to-right.

</details>

<details>
<summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Approach 1: Top-down bounds propagation
def validate_bounds(root, lo=float('-inf'), hi=float('inf')):
    if not root:
        return True
    if not (lo < root.val < hi):
        return False
    return (validate_bounds(root.left, lo, root.val) and
            validate_bounds(root.right, root.val, hi))

# Approach 2: Iterative inorder — must be strictly increasing
def validate_inorder(root):
    stack = []
    prev = float('-inf')
    current = root
    while stack or current:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        if current.val <= prev:
            return False            # not strictly increasing = invalid BST
        prev = current.val
        current = current.right
    return True

# Test both
valid = TreeNode(4,
    TreeNode(2, TreeNode(1), TreeNode(3)),
    TreeNode(6, TreeNode(5), TreeNode(7)))

invalid = TreeNode(5, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(6)))

assert validate_bounds(valid) == True
assert validate_inorder(valid) == True
assert validate_bounds(invalid) == False
assert validate_inorder(invalid) == False
print("Both approaches agree.")
```

```
When to prefer each:
  Bounds:   Easier to reason about; naturally top-down; can stop
            exploring a subtree as soon as a violation is found.
  Inorder:  Intuitive (BST inorder = sorted) and avoids passing
            extra parameters. Iterative version uses O(1) extra
            variables (not counting the stack). Slightly harder
            to short-circuit with recursion.

Both: O(n) time, O(h) space.
```

**Why:** The bounds approach directly encodes the BST invariant — each node carries its allowed range. The inorder approach leverages the "BST inorder = sorted" property. Both are accepted in interviews; bounds propagation is slightly more versatile (easier to extend for duplicate handling or different ordering rules).

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q25"></a>
### Q25 — Common mistake: treating BST like a general tree

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


A junior engineer writes a function to count nodes with values in `[low, high]`. Their solution always visits every node in the tree. Identify the mistake and rewrite it to exploit the BST property.

```python
# Junior's code
def count_in_range_wrong(root, low, high):
    if not root:
        return 0
    count = 1 if low <= root.val <= high else 0
    count += count_in_range_wrong(root.left, low, high)
    count += count_in_range_wrong(root.right, low, high)
    return count
```

<details>
<summary>Hint</summary>

The code is correct in output but ignores the BST ordering property. If `root.val < low`, every single value in the left subtree is also below `low`. Why visit any of them?

</details>

<details>
<summary>Answer</summary>

The mistake: unconditionally recurring left and right regardless of whether those subtrees can contain valid values. The BST property guarantees that if `node.val <= low`, the entire left subtree is also `<= low` and can be skipped.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Correct: prune branches that cannot contain values in [low, high]
def count_in_range_correct(root, low, high):
    if not root:
        return 0
    count = 1 if low <= root.val <= high else 0
    if root.val > low:      # left subtree MIGHT have values >= low
        count += count_in_range_correct(root.left, low, high)
    if root.val < high:     # right subtree MIGHT have values <= high
        count += count_in_range_correct(root.right, low, high)
    return count

def insert_bst(root, val):
    if not root: return TreeNode(val)
    if val < root.val: root.left = insert_bst(root.left, val)
    elif val > root.val: root.right = insert_bst(root.right, val)
    return root

# Build BST [1..15]
root = None
for v in [8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15]:
    root = insert_bst(root, v)

print(count_in_range_correct(root, 5, 10))   # 6 → values: 5,6,7,8,9,10

# Both give same answer, but wrong version visits all 15 nodes
# Correct version prunes subtrees below 5 and above 10
```

The general rule: **never recurse into a subtree when the BST property guarantees all values there are out of range.** This is the fundamental difference between using BSTs correctly and treating them as generic trees.

**Time (correct):** O(log n + k) average. **Time (wrong):** O(n) always. **Space:** O(h).

</details>

---

**[Back to README](../README.md)**

**Prev:** [← Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Heaps — Theory →](../16_heaps/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
