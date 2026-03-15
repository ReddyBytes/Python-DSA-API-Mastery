# Trees — Common Mistakes & Error Prevention

> **How to use this file**: Each mistake shows WRONG code (with the bug annotated),
> CORRECT code (with the fix annotated), and a test case that distinguishes them.
> Study the wrong code first — recognize the pattern in your own writing.

---

## Mistake 1 — Null Check Order: Accessing Before Checking

### The Bug

You access a node's attribute (`.val`, `.left`, `.right`) BEFORE checking if the node
is `None`. This crashes with `AttributeError: 'NoneType' object has no attribute 'val'`.

### Wrong Code

```python
def search(node, target):
    # WRONG: accessing node.val BEFORE checking if node is None
    if node.val == target:        # CRASH when node is None
        return True
    if node.val > target:
        return search(node.left, target)
    return search(node.right, target)

# Also wrong:
def has_value(node, val):
    if node.left.val == val:      # CRASH if node.left is None
        return True
    ...
```

### Correct Code

```python
def search(node, target):
    # CORRECT: check None FIRST, before accessing any attribute
    if node is None:
        return False              # base case: fell off the tree

    if node.val == target:
        return True
    if node.val > target:
        return search(node.left, target)
    return search(node.right, target)

def has_value(node, val):
    if node is None:
        return False
    if node.left is not None and node.left.val == val:
        return True
    ...
```

### Test Case That Catches This

```python
# Test: search an empty tree or a single-node tree
root = TreeNode(5)
root.right = TreeNode(7)

# Bug triggers when searching for value less than 5:
# search(root, 3) → node.val=5 > 3 → calls search(root.left, 3)
# root.left is None → next call: node.val crashes
print(search(root, 3))    # WRONG: AttributeError
                           # CORRECT: False

# Always test:
# 1. Empty tree (root=None)
# 2. Single node
# 3. Search for value in empty subtree
```

---

## Mistake 2 — Forgetting `return` in Recursive Calls

### The Bug

The function implicitly returns `None` because you forgot `return` before the recursive
call. The result of the recursion is computed and immediately discarded.

### Wrong Code

```python
def find_node(node, target):
    if node is None:
        return None
    if node.val == target:
        return node

    # WRONG: result of recursion is discarded! Function returns None implicitly.
    if node.val > target:
        find_node(node.left, target)   # missing return
    else:
        find_node(node.right, target)  # missing return
    # Falls off the end → returns None even if node was found below

# Also common in path-finding:
def has_path_sum(node, target):
    if node is None:
        return False
    if not node.left and not node.right:
        return node.val == target

    # WRONG: both branches missing return
    has_path_sum(node.left, target - node.val)
    has_path_sum(node.right, target - node.val)
```

### Correct Code

```python
def find_node(node, target):
    if node is None:
        return None
    if node.val == target:
        return node

    # CORRECT: always return the result of recursive calls
    if node.val > target:
        return find_node(node.left, target)    # return the result
    else:
        return find_node(node.right, target)   # return the result

def has_path_sum(node, target):
    if node is None:
        return False
    if not node.left and not node.right:
        return node.val == target

    # CORRECT: return OR of both subtrees
    return (has_path_sum(node.left, target - node.val) or
            has_path_sum(node.right, target - node.val))
```

### Test Case That Catches This

```python
# Tree:   5
#        / \
#       3   7

root = TreeNode(5)
root.left = TreeNode(3)
root.right = TreeNode(7)

# Without return, both of these return None instead of the node/True:
result = find_node(root, 3)
print(result)           # WRONG: None (should be TreeNode(3))
                        # CORRECT: TreeNode with val=3

print(has_path_sum(root, 8))   # WRONG: None (falsy, but wrong type)
                                # CORRECT: True (5+3=8)

# Rule: EVERY code path in a function that returns a value must have
# an explicit return statement. No "falling off the end."
```

---

## Mistake 3 — Diameter vs Height Confusion

### The Bug

Tree diameter = the longest path between any two nodes (may not pass through root).
At a given node, the diameter through it = left_height + right_height.
But your recursive function can only RETURN one value — you can't return both
the diameter AND the height from the same call.

### Wrong Code

```python
def diameter_wrong(node):
    # WRONG: this computes the depth (longest path DOWN from node),
    # not the diameter (longest path THROUGH node using both sides).
    if node is None:
        return 0

    left = diameter_wrong(node.left)
    right = diameter_wrong(node.right)

    # This is max DEPTH, not DIAMETER.
    # Diameter would require left + right, but we're returning max(left, right) + 1
    return max(left, right) + 1

# Consequence: calling diameter_wrong(root) gives the tree's HEIGHT,
# not its diameter. You'd never catch this without a non-trivial test.
```

### Correct Code

```python
def diameter_of_binary_tree(root):
    """
    CORRECT: use a nonlocal variable to track diameter separately.
    The recursive function RETURNS HEIGHT (needed by the parent).
    But ALSO updates the diameter (left + right) at each node.

    Two roles, two return channels:
      - return value: height (used by parent node)
      - nonlocal variable: diameter (the answer we actually want)
    """
    max_diameter = [0]   # use list so nested function can modify it

    def height(node):
        if node is None:
            return 0   # or -1 if counting edges (see Mistake 6)

        left_h = height(node.left)
        right_h = height(node.right)

        # Diameter THROUGH this node = left height + right height
        # (the path goes down left subtree, through this node, down right subtree)
        max_diameter[0] = max(max_diameter[0], left_h + right_h)

        # Return HEIGHT to parent (not diameter)
        return max(left_h, right_h) + 1

    height(root)
    return max_diameter[0]

# Alternative: use class attribute or nonlocal
def diameter_v2(root):
    result = 0

    def height(node):
        nonlocal result
        if node is None:
            return 0
        left_h = height(node.left)
        right_h = height(node.right)
        result = max(result, left_h + right_h)
        return max(left_h, right_h) + 1

    height(root)
    return result
```

### Test Case That Catches This

```python
# Tree:    1
#         / \
#        2   3
#       / \
#      4   5
#
# Diameter = 3 (path: 4→2→1→3 or 5→2→1→3, length 3 edges)
# Height   = 3 (path: root→2→4 or root→2→5, length 3 nodes = 2 edges... wait)

root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)

print(diameter_wrong(root))          # returns 3 (height with node count)
print(diameter_of_binary_tree(root)) # returns 3 (diameter in edges)
# Both happen to return 3 HERE but for different reasons!

# A better distinguishing tree:
#      1
#     /
#    2
#   /
#  3
#
# Height = 3 (nodes) = 2 (edges)
# Diameter = 2 (edges, path: 3→2→1)
# Wrong function returns 3 (height as node count)
# Correct returns 2 (diameter in edges)
```

---

## Mistake 4 — Using BST Shortcut on a General Tree

### The Bug

BST has a special property: all values in the left subtree are smaller, all in the right
are larger. LCA (Lowest Common Ancestor) on a BST can use this property for an O(log n)
shortcut. On a GENERAL binary tree, this shortcut is WRONG — you must check both subtrees.

### Wrong Code

```python
def lca_wrong(root, p, q):
    # WRONG: assumes BST property. DO NOT use on general binary tree.
    if root is None:
        return None

    # These comparisons only make sense for a BST
    if p.val < root.val and q.val < root.val:
        return lca_wrong(root.left, p, q)    # both in left subtree
    if p.val > root.val and q.val > root.val:
        return lca_wrong(root.right, p, q)   # both in right subtree
    return root    # root is the LCA

# This silently gives wrong answers on a general tree where
# node positions don't correlate with values.
```

### Correct Code

```python
# For GENERAL binary tree LCA:
def lca_general(root, p, q):
    """
    If root is p or q, root IS the LCA (or the other is below it).
    If p is in left and q is in right (or vice versa), root is LCA.
    Otherwise, LCA is in whichever subtree contains both p and q.
    """
    if root is None:
        return None
    if root == p or root == q:
        return root    # found one of them — stop searching this branch

    left = lca_general(root.left, p, q)    # search left subtree
    right = lca_general(root.right, p, q)  # search right subtree

    if left and right:
        return root    # p and q are in DIFFERENT subtrees → root is LCA
    return left or right   # both are in one subtree → return whichever found them

# For BST (only use when you KNOW it's a BST):
def lca_bst(root, p, q):
    if root is None:
        return None
    if p.val < root.val and q.val < root.val:
        return lca_bst(root.left, p, q)
    if p.val > root.val and q.val > root.val:
        return lca_bst(root.right, p, q)
    return root
```

### Test Case That Catches This

```python
# General tree where BST property does NOT hold:
#       10
#      /  \
#     5    15
#    / \
#   3   8
#      /
#     6
#
# Find LCA of nodes 6 and 15.
# BST approach: 6 < 10 and 15 > 10? Not both < and not both > → returns root(10). CORRECT.
# But try LCA of 6 and 3:
# BST approach: both < 10 → go left. Both < 5? 3 < 5 but 6 > 5 → root(5). CORRECT here too.
# BST approach works only BECAUSE this tree happens to also be a valid BST.

# Non-BST tree where BST approach fails:
#       1
#      / \
#     2   3     (values: 2 > 1 but in left subtree — NOT a BST)
#    / \
#   4   5
# LCA of 4 and 5:
# BST approach: 4 > 1 and 5 > 1 → go right → returns node(3). WRONG.
# General approach: left returns node(2) (contains 4 and 5). CORRECT.
```

---

## Mistake 5 — Minimum Depth: DFS That Miscounts Nodes with One Child

### The Bug

Minimum depth = depth of the NEAREST LEAF. A LEAF has NO children (both left and right
are None). If a node has only one child, it is NOT a leaf — its minimum depth goes through
that one child.

### Wrong Code

```python
def min_depth_wrong(root):
    # WRONG: treats any node with a None child as a "leaf"
    if root is None:
        return 0

    left = min_depth_wrong(root.left)
    right = min_depth_wrong(root.right)

    # BUG: if left is None (returns 0), this picks 0+1=1 as the minimum.
    # But that means we stopped at a non-leaf node (one that has a right child).
    return min(left, right) + 1

# Example where this fails:
#    1
#     \
#      2        (root has no left child, only right)
#
# Wrong: min(0, 1) + 1 = 1. Says depth is 1. But node 1 is NOT a leaf!
# Correct: minimum depth = 2 (the only leaf is node 2).
```

### Correct Code

```python
def min_depth(root):
    """
    Minimum depth = distance to nearest LEAF.
    A LEAF has NO children (both left AND right are None).
    If a node has only one child, minimum depth must go through that child.
    """
    if root is None:
        return 0

    # If only right child exists, can't go left (no leaf there)
    # Must go right — so min depth = right depth + 1
    if root.left is None:
        return min_depth(root.right) + 1

    # If only left child exists, can't go right (no leaf there)
    # Must go left — so min depth = left depth + 1
    if root.right is None:
        return min_depth(root.left) + 1

    # BOTH children exist: take minimum of the two paths
    return min(min_depth(root.left), min_depth(root.right)) + 1

# Alternatively, use BFS (most natural for "minimum depth"):
from collections import deque

def min_depth_bfs(root):
    """
    BFS is actually the cleaner approach for minimum depth.
    The FIRST leaf we encounter in BFS is guaranteed to be the nearest.
    No need to handle one-child edge cases explicitly.
    """
    if root is None:
        return 0

    queue = deque([(root, 1)])  # (node, depth)

    while queue:
        node, depth = queue.popleft()

        # First leaf found = minimum depth (BFS explores level by level)
        if not node.left and not node.right:
            return depth

        if node.left:
            queue.append((node.left, depth + 1))
        if node.right:
            queue.append((node.right, depth + 1))

    return 0
```

### Test Case That Catches This

```python
# Tree:    1
#           \
#            2
#
# Expected minimum depth: 2 (only leaf is node 2)
root = TreeNode(1)
root.right = TreeNode(2)

print(min_depth_wrong(root))   # returns 1. WRONG.
print(min_depth(root))         # returns 2. CORRECT.

# Also test:
#    1
#   / \
#  2   3
# Expected: 2 (both children are leaves at depth 2)
root2 = TreeNode(1)
root2.left = TreeNode(2)
root2.right = TreeNode(3)

print(min_depth_wrong(root2))  # returns 2. Happens to be correct here.
print(min_depth(root2))        # returns 2. CORRECT.
# This is why the first tree is the critical test case — the simpler tree
# masks the bug.
```

---

## Mistake 6 — Off-by-One in Height vs Depth Convention

### The Bug

"Height of a tree" and "depth of a node" have two common conventions, and mixing them
causes off-by-one errors. You must pick ONE convention and use it consistently.

### Two Valid Conventions

```
CONVENTION 1 — Count NODES (height = number of nodes on longest path):
  Height of null node = 0
  Height of leaf node = 1
  Height of tree with 2 levels = 2

CONVENTION 2 — Count EDGES (height = number of edges on longest path):
  Height of null node = -1  ← common choice to make leaf = 0
  Height of leaf node = 0
  Height of tree with 2 levels = 1

LeetCode problems typically use CONVENTION 1 (node counting, null = 0).
Diameter problems often use CONVENTION 2 (edge counting, null = -1 or 0).
```

### Showing Both Conventions

```python
# Convention 1: Counting NODES (null = 0)
def height_by_nodes(node):
    if node is None:
        return 0                          # null contributes 0 nodes
    return max(height_by_nodes(node.left),
               height_by_nodes(node.right)) + 1   # +1 for current node

# Convention 2: Counting EDGES (null = -1)
def height_by_edges(node):
    if node is None:
        return -1                         # null: -1 so that leaf = (-1+1) = 0
    return max(height_by_edges(node.left),
               height_by_edges(node.right)) + 1   # +1 for the edge to this node

# Verification:
#   Tree:   1
#          / \
#         2   3
#        /
#       4
#
# By nodes:   height_by_nodes(root) = 3 (nodes: 1→2→4)
# By edges:   height_by_edges(root) = 2 (edges: 1-2, 2-4)
```

### Wrong Code — Mixed Conventions

```python
def is_balanced_wrong(node):
    # WRONG: mixes conventions mid-way
    if node is None:
        return True

    left_h = height_by_nodes(node.left)    # node counting (null=0)
    right_h = height_by_edges(node.right)  # edge counting (null=-1)

    # Now comparing apples to oranges — always off by 1+
    if abs(left_h - right_h) > 1:
        return False
    return is_balanced_wrong(node.left) and is_balanced_wrong(node.right)
```

### Correct Code — Consistent Convention

```python
def is_balanced(root):
    """Returns True if tree is height-balanced (all nodes' subtrees differ by ≤ 1)."""

    def height(node):
        """Returns height in nodes (null = 0), or -1 if subtree is unbalanced."""
        if node is None:
            return 0   # Convention 1: counting nodes

        left_h = height(node.left)
        right_h = height(node.right)

        # Propagate imbalance upward with -1 sentinel
        if left_h == -1 or right_h == -1:
            return -1
        if abs(left_h - right_h) > 1:
            return -1

        return max(left_h, right_h) + 1   # consistent: same +1 convention

    return height(root) != -1

# RULE: Pick ONE convention at the start of the problem and document it.
# A common comment: "# height = number of nodes, null → 0"
```

### Test Case That Catches This

```python
# Single node: height should be 1 (nodes) or 0 (edges)
root = TreeNode(1)
print(height_by_nodes(root))   # 1
print(height_by_edges(root))   # 0

# Two levels:
root.left = TreeNode(2)
print(height_by_nodes(root))   # 2
print(height_by_edges(root))   # 1

# Null:
print(height_by_nodes(None))   # 0
print(height_by_edges(None))   # -1    ← DIFFERENT for null case

# If your function returns 0 for null, you're using node-counting.
# If it returns -1 for null, you're using edge-counting.
# NEVER mix these in the same calculation.
```

---

## Mistake 7 — Max Path Sum: Forgetting the "Any to Any Path" Cases

### The Bug

In "Binary Tree Maximum Path Sum" (LeetCode 124), the path can go through any node and
can use EITHER or BOTH subtrees. A common mistake is to only consider paths that go
DOWN from the root, or to forget that a negative-gain subtree should be excluded.

### Wrong Code

```python
def max_path_sum_wrong(root):
    # WRONG: only considers paths that start at root and go down one side.
    # Misses paths that go up through a node using both left and right.
    if root is None:
        return 0

    left = max_path_sum_wrong(root.left)
    right = max_path_sum_wrong(root.right)

    # BUG 1: doesn't allow "use both left and right" to update the answer
    # BUG 2: doesn't prevent negative paths from being included
    # BUG 3: returns max of the two paths, but doesn't track a global max
    return max(left, right) + root.val   # wrong return value
```

### Correct Code

```python
def max_path_sum(root):
    """
    A "path" is any sequence of nodes where each pair is parent-child (no revisiting).
    The path can start and end at any node.

    At each node, four candidate paths exist:
      1. Just this node:                         root.val
      2. This node + best left subtree path:     root.val + left_gain
      3. This node + best right subtree path:    root.val + right_gain
      4. Left + this node + right (bent path):   left_gain + root.val + right_gain

    But the function can only RETURN a "straight" path (down one side),
    because the parent will extend it further. We update the global max
    with the "bent" path (case 4) inside the recursion.
    """
    max_sum = [float('-inf')]   # global maximum (use list for mutability)

    def gain(node):
        """
        Returns the maximum gain from a path starting at node and going DOWN
        into one subtree only (straight path — can be extended by parent).

        Also updates max_sum with the best "bent" path through this node.
        """
        if node is None:
            return 0

        # max(0, ...) ensures we only include a subtree if it adds value.
        # If a subtree path has negative total, it's better to exclude it.
        left_gain = max(0, gain(node.left))    # ← KEY: exclude if negative
        right_gain = max(0, gain(node.right))  # ← KEY: exclude if negative

        # "Bent" path through this node: left + node + right
        # This cannot be returned upward (parent can't extend a bent path),
        # but it IS a valid candidate for the answer.
        path_through_node = node.val + left_gain + right_gain
        max_sum[0] = max(max_sum[0], path_through_node)

        # Return the best "straight" path for the parent to extend
        return node.val + max(left_gain, right_gain)

    gain(root)
    return max_sum[0]

# Four cases at each node, visualized:
#
#        5
#       / \
#      4   8
#     / \ / \
#    11 13  4  ← (simplified)
#   /  \   \
#  7    2   1
#
# The maximum path is 7→11→4→5→8→4→1? No.
# Actually: 7→11→4→5→8→13 = 48? Let's check with the function.
# The key insight: max(0, gain) means we don't enter negative territory.
```

### Test Cases That Catch This

```python
# Test 1: All positive — must use entire tree path
#    1
#   / \
#  2   3
# Expected: 6 (path: 2→1→3)
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
print(max_path_sum(root))         # CORRECT: 6
print(max_path_sum_wrong(root))   # WRONG: 4 (only goes down best side: 1→3=4)

# Test 2: Negative values — should exclude bad subtree
#   -3
# Expected: -3 (single node; can't do better)
root2 = TreeNode(-3)
print(max_path_sum(root2))        # CORRECT: -3
# Wrong function returns 0 (never handles the all-negative case correctly)

# Test 3: Mixed, best path doesn't go through root
#     -10
#     /  \
#    9   20
#       /  \
#      15   7
# Expected: 42 (path: 15→20→7)
root3 = TreeNode(-10)
root3.left = TreeNode(9)
root3.right = TreeNode(20)
root3.right.left = TreeNode(15)
root3.right.right = TreeNode(7)
print(max_path_sum(root3))        # CORRECT: 42
print(max_path_sum_wrong(root3))  # WRONG: misses the 15→20→7 bent path
```

---

## Summary Table — Bugs and Their Fixes

| Mistake | Root Cause | Fix |
|---------|-----------|-----|
| Access `node.val` before null check | Wrong order | Always check `if node is None` first |
| Missing `return` in recursive call | Forgetting to propagate result | Every path must `return` the recursive call |
| Diameter vs height confusion | One return value, two jobs | Use `nonlocal` or list to track diameter; return height |
| BST shortcut on general tree | Wrong assumption | Use general LCA algorithm (check both subtrees) |
| Min depth counting non-leaf | Wrong leaf definition | A leaf must have BOTH children as None |
| Off-by-one height | Mixed conventions | Pick one convention (node-counting or edge-counting), document it |
| Max path sum missing cases | Forgot bent path or negatives | Use `max(0, gain)` to skip negatives; update global max with bent path |

---

## The Universal Tree Debugging Template

When your tree function returns a wrong answer, run through this checklist:

```
1. BASE CASE: Does if node is None return the CORRECT neutral value?
              (0 for height, False for search, None for find, [] for paths)

2. NULL FIRST: Is every node.val/node.left/node.right access
               PRECEDED by a null check?

3. RETURN:     Does EVERY code path (including else-branches) have
               an explicit return statement?

4. TWO JOBS:   Does the function need to both COMPUTE something AND
               RETURN something different? If so, use nonlocal/list.

5. CONVENTION: Is the height convention consistent? (null = 0 or null = -1?)

6. NEGATIVES:  For max/min path problems, should you use max(0, value)
               to exclude paths that reduce the answer?

7. BOTH SIDES: Does the problem ask about paths through a node using
               BOTH subtrees? If so, you need a global max variable.
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real World Usage](./real_world_usage.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
