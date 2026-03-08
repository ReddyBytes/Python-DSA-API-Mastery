# Binary Search Trees — Common Mistakes & Error Prevention

A focused guide on the bugs that appear most often in BST problems during interviews. Each mistake includes a broken implementation, an explanation of why it fails, and a corrected version with test cases that expose the bug.

---

## Mistake 1: BST Validation — Checking Only the Parent-Child Relationship

### The Confusion

A node is valid in a BST only if its value respects the **entire ancestry chain**, not just its immediate parent:
- Every node in a node's **left subtree** must be **strictly less than** the node
- Every node in a node's **right subtree** must be **strictly greater than** the node

Checking only `node.val > node.left.val` misses the case where a value in the right subtree is too small, or a value in the left subtree is too large relative to an ancestor.

### Wrong Code

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# WRONG: checks only direct parent-child relationship
def is_valid_bst_wrong(root):
    if root is None:
        return True
    # Check left child
    if root.left and root.left.val >= root.val:
        return False
    # Check right child
    if root.right and root.right.val <= root.val:
        return False
    return is_valid_bst_wrong(root.left) and is_valid_bst_wrong(root.right)

# --- Test that exposes the bug ---
# Tree that LOOKS locally valid but violates BST property:
#       5
#      / \
#     1   4
#        / \
#       3   6
#
# At node 4: left child 3 < 4 (ok), right child 6 > 4 (ok)
# But 4 is in the RIGHT subtree of 5, so 4 > 5 must hold — it doesn't! Invalid BST.
# Also: 3 is in the right subtree of 5 but 3 < 5 — doubly invalid.

root = TreeNode(5)
root.left = TreeNode(1)
root.right = TreeNode(4)
root.right.left = TreeNode(3)
root.right.right = TreeNode(6)

print(is_valid_bst_wrong(root))   # True  <-- BUG: should be False

# Another classic case:
#       10
#      /  \
#     5    15
#          / \
#         6   20
#
# 6 is in the right subtree of 10, but 6 < 10 — invalid.
root2 = TreeNode(10)
root2.left = TreeNode(5)
root2.right = TreeNode(15)
root2.right.left = TreeNode(6)    # BUG: 6 < 10 but in right subtree
root2.right.right = TreeNode(20)

print(is_valid_bst_wrong(root2))  # True  <-- BUG: should be False
```

### Correct Code

```python
import math

def is_valid_bst_correct(root, min_val=float('-inf'), max_val=float('inf')):
    """Pass the valid range down the recursion."""
    if root is None:
        return True

    # Current node must lie strictly within (min_val, max_val)
    if not (min_val < root.val < max_val):
        return False

    # Left subtree: all values must be < root.val (tighten upper bound)
    # Right subtree: all values must be > root.val (tighten lower bound)
    return (is_valid_bst_correct(root.left,  min_val, root.val) and
            is_valid_bst_correct(root.right, root.val, max_val))

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# --- Tests ---
# Valid BST:   4
#            / \
#           2   6
#          / \ / \
#         1  3 5  7
root_valid = TreeNode(4,
    TreeNode(2, TreeNode(1), TreeNode(3)),
    TreeNode(6, TreeNode(5), TreeNode(7)))
assert is_valid_bst_correct(root_valid) == True

# Invalid: right subtree contains value less than root
#       5
#      / \
#     1   4
#        / \
#       3   6
root_inv1 = TreeNode(5, TreeNode(1),
                     TreeNode(4, TreeNode(3), TreeNode(6)))
assert is_valid_bst_correct(root_inv1) == False   # was True with wrong code

# Invalid: 6 is in right subtree of 10 but 6 < 10
root_inv2 = TreeNode(10, TreeNode(5),
                     TreeNode(15, TreeNode(6), TreeNode(20)))
assert is_valid_bst_correct(root_inv2) == False   # was True with wrong code

# Single node
assert is_valid_bst_correct(TreeNode(1)) == True

# Duplicate: BST requires STRICT inequalities
root_dup = TreeNode(2, TreeNode(2))   # equal val in left subtree — invalid
assert is_valid_bst_correct(root_dup) == False

print("BST validation tests passed.")
```

---

## Mistake 2: Deleting a Node with Two Children — Forgetting to Remove the Successor

### The Confusion

When deleting a node that has **two children**, the standard algorithm:
1. Find the **in-order successor** (smallest value in the right subtree)
2. Copy the successor's value into the node being deleted
3. **Recursively delete the successor from the right subtree**

Step 3 is the one that gets forgotten. Without it, the successor's value now appears **twice** in the tree — once in the "deleted" node's position, and again in the successor's original position.

### Wrong Code

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def find_min(node):
    while node.left:
        node = node.left
    return node

# WRONG: copies successor value but does not delete the successor node
def delete_bst_wrong(root, key):
    if root is None:
        return None

    if key < root.val:
        root.left = delete_bst_wrong(root.left, key)
    elif key > root.val:
        root.right = delete_bst_wrong(root.right, key)
    else:
        # Found the node to delete
        if root.left is None:
            return root.right
        elif root.right is None:
            return root.left
        else:
            # Two children: find in-order successor (min of right subtree)
            successor = find_min(root.right)
            root.val = successor.val   # copy value
            # BUG: forgot to delete the successor from the right subtree
            # successor still exists in right subtree with the same value!

    return root

# --- Test that exposes the bug ---
def inorder(root):
    if not root:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)

#       5
#      / \
#     3   7
#    / \ / \
#   2  4 6  8
root = TreeNode(5,
    TreeNode(3, TreeNode(2), TreeNode(4)),
    TreeNode(7, TreeNode(6), TreeNode(8)))

print("Before deletion:", inorder(root))   # [2, 3, 4, 5, 6, 7, 8]
delete_bst_wrong(root, 5)
print("After deleting 5 (wrong):", inorder(root))
# Expected: [2, 3, 4, 6, 7, 8]
# Actual:   [2, 3, 4, 6, 6, 8]  <-- BUG: 6 appears twice (copied up but not removed)
```

### Correct Code

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def find_min(node):
    while node.left:
        node = node.left
    return node

def delete_bst_correct(root, key):
    if root is None:
        return None

    if key < root.val:
        root.left = delete_bst_correct(root.left, key)
    elif key > root.val:
        root.right = delete_bst_correct(root.right, key)
    else:
        # Case 1: no left child
        if root.left is None:
            return root.right
        # Case 2: no right child
        elif root.right is None:
            return root.left
        # Case 3: two children
        else:
            successor = find_min(root.right)
            root.val = successor.val
            # CRITICAL: delete the successor from the right subtree
            root.right = delete_bst_correct(root.right, successor.val)

    return root

def inorder(root):
    if not root:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)

def build_bst():
    #       5
    #      / \
    #     3   7
    #    / \ / \
    #   2  4 6  8
    return TreeNode(5,
        TreeNode(3, TreeNode(2), TreeNode(4)),
        TreeNode(7, TreeNode(6), TreeNode(8)))

# --- Tests ---
root = build_bst()
root = delete_bst_correct(root, 5)   # delete root (two children)
assert inorder(root) == [2, 3, 4, 6, 7, 8]   # 5 gone, 6 appears once

root = build_bst()
root = delete_bst_correct(root, 3)   # delete node with two children
assert inorder(root) == [2, 4, 5, 6, 7, 8]

root = build_bst()
root = delete_bst_correct(root, 2)   # delete leaf
assert inorder(root) == [3, 4, 5, 6, 7, 8]

root = build_bst()
root = delete_bst_correct(root, 7)   # delete node with two children
assert inorder(root) == [2, 3, 4, 5, 6, 8]

root = build_bst()
root = delete_bst_correct(root, 99)  # delete non-existent key
assert inorder(root) == [2, 3, 4, 5, 6, 7, 8]

print("BST deletion tests passed.")
```

---

## Mistake 3: BST Insert — Forgetting to Return the Root

### The Confusion

When writing a recursive BST insert, the function must **return the (possibly new) root** at every recursive call. A common mistake: assigning to the local `root` variable when `root is None` and returning nothing. The local rebinding does not propagate back — the original tree is unchanged.

### Wrong Code

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# WRONG: rebinds a local variable; return value is None in base case
def insert_wrong(root, val):
    if root is None:
        root = TreeNode(val)   # rebinds local name only — caller sees nothing
        return               # returns None implicitly

    if val < root.val:
        insert_wrong(root.left, val)    # BUG: return value discarded
    elif val > root.val:
        insert_wrong(root.right, val)   # BUG: return value discarded

# --- Test that exposes the bug ---
def inorder(root):
    if not root:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)

root = TreeNode(5)
insert_wrong(root, 3)
insert_wrong(root, 7)
insert_wrong(root, 1)
print(inorder(root))   # Expected: [1, 3, 5, 7] — Actual: [5]  BUG: nothing inserted!

# Another variant of the bug: correctly returns in base case, but
# does not propagate the return value in recursive case
def insert_wrong_v2(root, val):
    if root is None:
        return TreeNode(val)   # correct base case...
    if val < root.val:
        insert_wrong_v2(root.left, val)    # BUG: return value not assigned
    elif val > root.val:
        insert_wrong_v2(root.right, val)   # BUG: return value not assigned
    return root

root2 = TreeNode(5)
root2 = insert_wrong_v2(root2, 3)
root2 = insert_wrong_v2(root2, 7)
print(inorder(root2))   # [5] — still empty because root.left/right never set
```

### Correct Code

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def insert_correct(root, val):
    """Returns the root of the modified tree."""
    if root is None:
        return TreeNode(val)        # return the new node

    if val < root.val:
        root.left = insert_correct(root.left, val)    # assign the return value
    elif val > root.val:
        root.right = insert_correct(root.right, val)  # assign the return value
    # if val == root.val: do nothing (no duplicates in standard BST)

    return root   # always return root

def inorder(root):
    if not root:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)

# --- Tests ---
root = None
for val in [5, 3, 7, 1, 4, 6, 8]:
    root = insert_correct(root, val)

assert inorder(root) == [1, 3, 4, 5, 6, 7, 8]

# Insert into empty tree
root2 = insert_correct(None, 42)
assert inorder(root2) == [42]

# Insert duplicate — should not change tree
root3 = insert_correct(None, 5)
root3 = insert_correct(root3, 5)
assert inorder(root3) == [5]   # duplicate ignored

# Insert in sorted order (creates a skewed tree — still correct)
root4 = None
for val in [1, 2, 3, 4, 5]:
    root4 = insert_correct(root4, val)
assert inorder(root4) == [1, 2, 3, 4, 5]

print("BST insert tests passed.")
```

---

## Mistake 4: Range Query — Collecting All Nodes Then Filtering

### The Confusion

"Find all values in a BST between `low` and `high`" can be solved two ways:
1. **Wrong**: in-order traversal of the entire tree, then filter → O(n) time, visits every node
2. **Correct**: BST-aware DFS that prunes branches outside the range → O(k + h) where k is the number of results and h is the height

BST property lets you skip entire subtrees: if a node's value is less than `low`, its entire left subtree is also less than `low` — skip it.

### Wrong Code

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# WRONG: visits every node even when subtrees are guaranteed out of range
def range_query_wrong(root, low, high):
    result = []

    def inorder(node):
        if not node:
            return
        inorder(node.left)    # visits ALL left children even if node.val < low
        if low <= node.val <= high:
            result.append(node.val)
        inorder(node.right)   # visits ALL right children even if node.val > high

    inorder(root)
    return result

# This is CORRECT in output but INEFFICIENT.
# On a BST with 10^6 nodes where range is [999990, 999999],
# the wrong version visits all 10^6 nodes.
# The correct version visits only ~20 nodes (log n path + k results).

# Demonstrating the extra visits:
visit_count = {"wrong": 0}

def range_query_wrong_instrumented(root, low, high):
    result = []
    def inorder(node):
        if not node:
            return
        visit_count["wrong"] += 1
        inorder(node.left)
        if low <= node.val <= high:
            result.append(node.val)
        inorder(node.right)
    inorder(root)
    return result
```

### Correct Code

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def range_query_correct(root, low, high):
    """Prune branches outside [low, high] using BST property."""
    result = []

    def dfs(node):
        if not node:
            return
        # Only go left if there could be values >= low in left subtree
        if node.val > low:
            dfs(node.left)
        # Collect if in range
        if low <= node.val <= high:
            result.append(node.val)
        # Only go right if there could be values <= high in right subtree
        if node.val < high:
            dfs(node.right)

    dfs(root)
    return sorted(result)  # DFS returns in-order, but sort for clarity

def build_bst(values):
    root = None
    def insert(root, val):
        if root is None:
            return TreeNode(val)
        if val < root.val:
            root.left = insert(root.left, val)
        elif val > root.val:
            root.right = insert(root.right, val)
        return root
    for v in values:
        root = insert(root, v)
    return root

# --- Tests ---
root = build_bst([10, 5, 15, 3, 7, 13, 18, 1, 6])

assert range_query_correct(root, 6, 10)  == [6, 7, 10]
assert range_query_correct(root, 1, 3)   == [1, 3]
assert range_query_correct(root, 13, 18) == [13, 15, 18]
assert range_query_correct(root, 0, 20)  == [1, 3, 5, 6, 7, 10, 13, 15, 18]
assert range_query_correct(root, 8, 9)   == []    # no nodes in range
assert range_query_correct(root, 7, 7)   == [7]   # exact match

# Verify same results as brute-force (wrong) version
assert range_query_correct(root, 6, 10) == sorted(range_query_wrong(root, 6, 10))

print("BST range query tests passed.")

def range_query_wrong(root, low, high):
    result = []
    def inorder(node):
        if not node: return
        inorder(node.left)
        if low <= node.val <= high: result.append(node.val)
        inorder(node.right)
    inorder(root)
    return result
```

---

## Mistake 5: LCA in a BST — Using General Tree LCA Instead of BST-Specific O(h)

### The Confusion

**General tree LCA** (Lowest Common Ancestor) requires O(n) time — you must visit every node to find where `p` and `q` appear.

**BST LCA** uses the BST property directly:
- If both `p` and `q` are **less than** the current node → LCA is in the **left** subtree
- If both `p` and `q` are **greater than** the current node → LCA is in the **right** subtree
- Otherwise → the current node **is** the LCA (the paths to `p` and `q` diverge here)

This gives O(h) time — O(log n) on a balanced BST, not O(n).

### Wrong Code (General Tree LCA Applied to BST)

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# WRONG: general tree LCA — works correctly but ignores BST property, O(n)
def lca_general_wrong(root, p, q):
    """
    Correct output, but O(n) — misses the O(h) BST optimisation.
    In an interview this signals you did not recognise the BST structure.
    """
    if root is None:
        return None
    if root.val == p or root.val == q:
        return root

    left = lca_general_wrong(root.left, p, q)
    right = lca_general_wrong(root.right, p, q)

    if left and right:
        return root   # p and q found in different subtrees
    return left if left else right
    # This is O(n): visits every node regardless of BST structure
```

### Correct Code (BST-Specific LCA)

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def lca_bst_correct(root, p, q):
    """
    O(h) LCA using BST property.
    p and q are guaranteed to exist in the tree.
    """
    node = root
    while node:
        if p < node.val and q < node.val:
            node = node.left    # both nodes are in left subtree
        elif p > node.val and q > node.val:
            node = node.right   # both nodes are in right subtree
        else:
            return node.val     # divergence point — this IS the LCA

    return -1   # should never reach here if p and q are guaranteed in tree

# Recursive version — equally correct and O(h)
def lca_bst_recursive(root, p, q):
    if root is None:
        return -1
    if p < root.val and q < root.val:
        return lca_bst_recursive(root.left, p, q)
    elif p > root.val and q > root.val:
        return lca_bst_recursive(root.right, p, q)
    else:
        return root.val   # current node is the LCA

def build_bst_manual():
    #           6
    #          / \
    #         2   8
    #        / \ / \
    #       0  4 7  9
    #         / \
    #        3   5
    root = TreeNode(6)
    root.left = TreeNode(2)
    root.right = TreeNode(8)
    root.left.left = TreeNode(0)
    root.left.right = TreeNode(4)
    root.left.right.left = TreeNode(3)
    root.left.right.right = TreeNode(5)
    root.right.left = TreeNode(7)
    root.right.right = TreeNode(9)
    return root

# --- Tests ---
root = build_bst_manual()

assert lca_bst_correct(root, 2, 8)  == 6   # LCA is root
assert lca_bst_correct(root, 2, 4)  == 2   # p is ancestor of q
assert lca_bst_correct(root, 3, 5)  == 4   # diverge at 4
assert lca_bst_correct(root, 7, 9)  == 8   # diverge at 8
assert lca_bst_correct(root, 0, 5)  == 2   # diverge at 2
assert lca_bst_correct(root, 6, 4)  == 6   # one node is root

assert lca_bst_recursive(root, 2, 8)  == 6
assert lca_bst_recursive(root, 3, 5)  == 4
assert lca_bst_recursive(root, 7, 9)  == 8

# Both versions should agree with general LCA on all cases
for p, q in [(2, 8), (2, 4), (3, 5), (7, 9), (0, 5)]:
    assert lca_bst_correct(root, p, q) == lca_general_wrong(root, p, q).val

print("BST LCA tests passed.")
```

### Complexity Comparison

```
Algorithm            Time      Space   Notes
-----------          ----      -----   -----
General tree LCA     O(n)      O(h)    Must visit every node
BST LCA (iterative)  O(h)      O(1)    Follows one path from root to LCA
BST LCA (recursive)  O(h)      O(h)    Call stack depth = tree height

For a balanced BST with n nodes: h = O(log n)
For a skewed BST: h = O(n) — BST LCA still beats general LCA by constant

Interview signal: using general LCA on a BST problem suggests you
did not recognise or leverage the BST ordering property.
```

---

## Summary Table

| # | Mistake                                              | Root Cause                                     | Fix                                                          |
|---|------------------------------------------------------|------------------------------------------------|--------------------------------------------------------------|
| 1 | BST validation checks only parent-child              | Ignores the full ancestry range constraint     | Pass `(min_val, max_val)` bounds down the recursion          |
| 2 | Delete with two children: copy value, skip deleting successor | Successor duplicated in tree          | After copying, `root.right = delete(root.right, successor.val)` |
| 3 | Insert returns `None` or discards return value        | Local rebinding does not affect caller         | Always `return root`; always assign `root.left = insert(...)` |
| 4 | Range query visits entire tree                       | Misses BST pruning on out-of-range branches    | Skip left if `node.val <= low`; skip right if `node.val >= high` |
| 5 | LCA uses general O(n) algorithm on a BST             | Does not exploit BST ordering property         | Use BST LCA: both < root → go left; both > root → go right; else → root is LCA |
