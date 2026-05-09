<a id="top"></a>
# Trees — The Structure of Hierarchy

> If arrays are straight roads,
> trees are branching paths.
>
> Trees represent relationships.
> Parent → Child.
> Root → Branch → Leaf.
>
> Trees help us organize information in a structured way.

Trees are everywhere.
Not just in DSA.
In life.

## 📖 Table of Contents

1. [Real Life Story — Family Tree](#1-real-life-story)
2. [Why Do We Need Trees?](#2-why-trees)
3. [What Is a Tree (Definition)](#3-definition)
4. [Basic Terminology](#4-terminology)
5. [Binary Tree — Most Important Type](#5-binary-tree)
6. [How Is Tree Stored in Python?](#6-python-storage)
7. [Tree Traversal — Exploring the Tree](#7-traversal)
8. [Visual Traversal Example](#8-visual-traversal)
9. [Recursion and Trees](#9-recursion)
10. [Height of Tree](#10-height)
11. [Balanced vs Skewed Tree](#11-balanced-vs-skewed)
12. [Why Trees Are Powerful](#12-why-powerful)
13. [Real-World Applications](#13-real-world)
14. [Mental Model to Remember](#14-mental-model)
15. [Final Understanding](#15-final-understanding)
16. [Level-Order Traversal — BFS on Trees](#16-level-order)
17. [Tree Serialization — Store and Rebuild Any Tree](#17-serialization)
18. [Top-Down vs Bottom-Up Thinking](#18-top-down-bottom-up)
19. [Path Problems](#19-path-problems)
20. [LCA — Lowest Common Ancestor](#20-lca)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
tree terminology · binary tree structure · inorder/preorder/postorder traversal · level-order traversal

**Should Learn** — Important for real projects, comes up regularly:
recursion pattern for trees · tree serialization · height and depth · balanced vs skewed

**Good to Know** — Useful in specific situations, not always tested:
path sum problems · tree reconstruction from traversals

**Reference** — Know it exists, look up syntax when needed:
Morris traversal · N-ary trees

<a id="1-real-life-story"></a>
# 1. Real Life Story — Family Tree

Imagine your family.

You have:

- Grandfather
- His children
- Their children
- And so on

It looks like:

```
        Grandfather
        /        \
    Father       Uncle
    /    \           \
 You   Sister      Cousin
```

This is a tree.

It has:

- One root (Grandfather)
- Branches (children)
- Leaves (last generation)

This is hierarchical structure.

## Visual: Family Tree with Full Vocabulary

```
                    [Grandparent]          ← ROOT (depth 0, level 1)
                    /           \
            [Parent A]        [Parent B]   ← depth 1
            /       \              \
        [Child1] [Child2]       [Child3]   ← depth 2 (LEAVES)
```

**Vocabulary mapped to family tree:**
```
  ROOT        = Grandparent (no parent)
  LEAF        = Child with no children
  PARENT      = Any node with children below it
  CHILD       = Any node with a parent above it
  SIBLING     = Nodes sharing the same parent
  SUBTREE     = A node + all its descendants
  ANCESTOR    = Any node on path from node → root
  DESCENDANT  = Any node reachable going downward
```

> [↑ Back to Top](#top)

<a id="2-why-trees"></a>
# 2. Why Do We Need Trees?

Not everything is linear.

Examples:

- Company structure
- File system
- Organization chart
- Website DOM
- Decision trees
- Game states

Linear structures cannot model branching relationships.

Trees can.

> [↑ Back to Top](#top)

<a id="3-definition"></a>
# 3. What Is a Tree (Definition)

> 📝 **Practice:** [Q1 · tree-node-definition](./practice.md#q1--tree-node-definition)

A tree is a hierarchical data structure consisting of:

- Nodes
- Edges
- Root node
- Parent-child relationships

Properties:

- One root
- No cycles
- Exactly one path between two nodes

If there is a cycle → it becomes a graph.

> [↑ Back to Top](#top)

<a id="4-terminology"></a>
# 4. Basic Terminology (Very Important)

Let's understand deeply.

## Node

Each element in tree.

Example:

```
A
```

A is node.

## Root

Topmost node.

Only one root.

## Parent

Node that has children.

## Child

Node connected below parent.

## Leaf

Node with no children.

## Subtree

Tree inside tree.

## Height

Number of edges from root to deepest leaf.

## Depth

Distance from root to a node.

## Visual: Height vs Depth

```
                    A           ← depth 0
                   / \
                  B   C         ← depth 1
                 / \
                D   E           ← depth 2

  DEPTH of a node   = distance from ROOT to that node
  HEIGHT of a node  = distance from that node to the DEEPEST LEAF below it

  Node   Depth   Height
  ────   ─────   ──────
  A        0       2      ← height of tree = height of root
  B        1       1
  C        1       0      ← C is a leaf, height = 0
  D        2       0      ← leaf
  E        2       0      ← leaf

  Mental model:
  DEPTH  = how far DOWN from the top am I?   (counting from root)
  HEIGHT = how far DOWN can I still go?      (counting to deepest leaf)
```

**Common mistake — depth vs height confusion:** Depth counts distance FROM the root DOWN to a node; height counts distance FROM a node DOWN to its deepest leaf. They run in opposite directions — depth increases going down, height decreases going down.

> [↑ Back to Top](#top)

<a id="5-binary-tree"></a>
# 5. Binary Tree — Most Important Type

Binary Tree means:

Each node has at most 2 children.

Left child.
Right child.

Example:

```
       1
      / \
     2   3
    / \
   4   5
```

## Visual: Common Binary Tree Shapes

### Perfect Binary Tree — Every level is completely full

```
            1
           / \
          2   3
         / \ / \
        4  5 6  7

  All leaves at same depth.
  Nodes = 2^(h+1) - 1  where h = height
```

### Complete Binary Tree — All levels full except last; last level filled left-to-right

```
            1
           / \
          2   3
         / \ /
        4  5 6          ← last level filled LEFT to RIGHT

  Used in heaps (can be stored as array efficiently).
  NOT complete:       1
                     / \
                    2   3
                   / \   \
                  4   5   7   ← gap on left before filling right
```

### Degenerate (Skewed) Tree — Every node has at most 1 child

```
  Left-skewed:        Right-skewed:
  1                         1
   \                        \
    2                        2
     \                        \
      3                        3
       \                        \
        4                        4

  Behaves like a linked list.
  All operations degrade from O(log n) → O(n).
  This is why balanced BSTs (AVL, Red-Black) exist.
```

> [↑ Back to Top](#top)

<a id="6-python-storage"></a>
# 6. How Is Tree Stored in Python?

Node structure:

```python
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
```

Each node stores:
- Value
- Left pointer
- Right pointer

Tree is connected through references.

**Common mistake — null check order:** Always check `if node is None` before accessing `node.val`, `node.left`, or `node.right`. Accessing any attribute on `None` crashes with `AttributeError: 'NoneType' object has no attribute 'val'`.

```python
# WRONG: accessing node.val BEFORE checking if node is None
def search(node, target):
    if node.val == target:        # CRASH when node is None
        return True

# CORRECT: check None FIRST, before accessing any attribute
def search(node, target):
    if node is None:
        return False              # base case: fell off the tree
    if node.val == target:
        return True
    if node.val > target:
        return search(node.left, target)
    return search(node.right, target)
```

> [↑ Back to Top](#top)

<a id="7-traversal"></a>
# 7. Tree Traversal — Exploring the Tree

> 📝 **Practice:** [Q2–Q8 · all-traversals](./practice.md#q2--inorder-traversal-recursive) | [Q16 · dfs-vs-bfs](./practice.md#q16--dfs-vs-bfs-on-trees-when-to-use-each) | [Q17 · inorder-and-sorted](./practice.md#q17--when-does-inorder-give-sorted-output)

Traversal means:
Visiting all nodes.

Three main types:

> 📝 **Practice:** [Q35 · binary-tree-traversal](../dsa_practice_questions_100.md#q35--logical--binary-tree-traversal)

## Inorder (Left → Root → Right)

```
Visit left
Visit node
Visit right
```

Used in BST to get sorted order.

## Preorder (Root → Left → Right)

Used for copying tree.

## Postorder (Left → Right → Root)

Used for deletion.

## Visual: All 4 Traversals Step by Step

```
            Tree used for all examples:

                    1
                   / \
                  2   3
                 / \   \
                4   5   6
```

### DFS — Preorder (Root → Left → Right)

Visit the node BEFORE visiting children. "Check in first, explore later."

```
Step 1: visit 1   →  [1]
Step 2: go left, visit 2  →  [1, 2]
Step 3: go left, visit 4  →  [1, 2, 4]
Step 4: 4 has no children, backtrack to 2
Step 5: go right, visit 5  →  [1, 2, 4, 5]
Step 6: 5 has no children, backtrack to 1
Step 7: go right, visit 3  →  [1, 2, 4, 5, 3]
Step 8: 3 has no left child, go right, visit 6  →  [1, 2, 4, 5, 3, 6]

Result:  1 → 2 → 4 → 5 → 3 → 6
```

### DFS — Inorder (Left → Root → Right)

Visit left subtree, THEN node, THEN right. "Explore left, check in, explore right."
**In a BST, inorder gives SORTED order!**

```
Step 1: go left as far as possible → reach 4
Step 2: 4 has no left child, visit 4  →  [4]
Step 3: backtrack to 2, visit 2  →  [4, 2]
Step 4: go to 2's right, visit 5  →  [4, 2, 5]
Step 5: backtrack to 1, visit 1  →  [4, 2, 5, 1]
Step 6: go to 3, 3 has no left, visit 3  →  [4, 2, 5, 1, 3]
Step 7: go to 3's right, visit 6  →  [4, 2, 5, 1, 3, 6]

Result:  4 → 2 → 5 → 1 → 3 → 6
```

### DFS — Postorder (Left → Right → Root)

Visit children BEFORE the node itself. "Explore everything before checking in."
**Used for: deleting trees, evaluating expression trees.**

```
Step 1: go left as far as possible → reach 4
Step 2: 4 is a leaf, visit 4  →  [4]
Step 3: backtrack to 2, go right to 5
Step 4: 5 is a leaf, visit 5  →  [4, 5]
Step 5: both children of 2 done, visit 2  →  [4, 5, 2]
Step 6: go to 3, 3 has no left, go right to 6
Step 7: 6 is a leaf, visit 6  →  [4, 5, 2, 6]
Step 8: right child of 3 done, visit 3  →  [4, 5, 2, 6, 3]
Step 9: both children of 1 done, visit 1  →  [4, 5, 2, 6, 3, 1]

Result:  4 → 5 → 2 → 6 → 3 → 1
```

### BFS — Level-order (Level by Level)

Use a queue. Visit all nodes at depth d before depth d+1.

```
Queue state:       Visited:
[1]            →   []
[2, 3]         →   [1]
[4, 5, 6]      →   [1, 2, 3]
[]             →   [1, 2, 3, 4, 5, 6]

Result:  1 → 2 → 3 → 4 → 5 → 6
```

### Side-by-Side Summary

```
           Tree:        1
                       / \
                      2   3
                     / \   \
                    4   5   6

Preorder:   [1,  2,  4,  5,  3,  6]   ← root first
Inorder:    [4,  2,  5,  1,  3,  6]   ← left first
Postorder:  [4,  5,  2,  6,  3,  1]   ← root last
Level-order:[1,  2,  3,  4,  5,  6]   ← breadth first
```

> [↑ Back to Top](#top)

<a id="8-visual-traversal"></a>
# 8. Visual Traversal Example

```
       1
      / \
     2   3
    / \
   4   5
```

Inorder:
4 2 5 1 3

Preorder:
1 2 4 5 3

Postorder:
4 5 2 3 1

Traversal order changes meaning.

> [↑ Back to Top](#top)

<a id="9-recursion"></a>
# 9. Recursion and Trees

> 📝 **Practice:** [Q9 · tree-height](./practice.md#q9--tree-height) · [Q10 · count-nodes](./practice.md#q10--count-nodes) · [Q11 · symmetric](./practice.md#q11--check-symmetric-tree) · [Q12 · balanced](./practice.md#q12--check-balanced-tree)

Trees are naturally recursive.

Why?

Each subtree is itself a tree.

Recursive thinking fits perfectly.

Example:

```python
def inorder(root):
    if not root:
        return
    inorder(root.left)
    print(root.val)
    inorder(root.right)
```

Recursion mirrors structure.

## Visual: Recursive Call Stack — Inorder Traversal

Each function call either processes a node or returns immediately on None.

```
inorder(1)
├── inorder(2)
│   ├── inorder(4)
│   │   ├── inorder(None) → return   ← left of 4
│   │   ├── VISIT 4  →  output: 4
│   │   └── inorder(None) → return   ← right of 4
│   ├── VISIT 2  →  output: 2
│   └── inorder(5)
│       ├── inorder(None) → return   ← left of 5
│       ├── VISIT 5  →  output: 5
│       └── inorder(None) → return   ← right of 5
├── VISIT 1  →  output: 1
└── inorder(3)
    ├── inorder(None) → return        ← left of 3
    ├── VISIT 3  →  output: 3
    └── inorder(6)
        ├── inorder(None) → return    ← left of 6
        ├── VISIT 6  →  output: 6
        └── inorder(None) → return    ← right of 6

Call stack at deepest point:
┌─────────────┐
│ inorder(None)│  ← top (returns immediately)
├─────────────┤
│ inorder(4)  │
├─────────────┤
│ inorder(2)  │
├─────────────┤
│ inorder(1)  │  ← bottom (first call)
└─────────────┘
```

**Common mistake — missing `return` in recursive calls:** If you forget `return` before a recursive call, the result is computed and immediately discarded — the function returns `None` implicitly. Every code path that produces a value must have an explicit `return` statement.

```python
# WRONG: result of recursion is discarded
def find_node(node, target):
    if node is None:
        return None
    if node.val == target:
        return node
    if node.val > target:
        find_node(node.left, target)   # missing return — returns None
    else:
        find_node(node.right, target)  # missing return — returns None

# CORRECT: always return the result of recursive calls
def find_node(node, target):
    if node is None:
        return None
    if node.val == target:
        return node
    if node.val > target:
        return find_node(node.left, target)
    else:
        return find_node(node.right, target)
```

> [↑ Back to Top](#top)

<a id="10-height"></a>
# 10. Height of Tree

> 📝 **Practice:** [Q9 · tree-height](./practice.md#q9--tree-height) · [Q19 · min-depth](./practice.md#q19--minimum-depth)

Height determines performance.

If tree is balanced:

Height ≈ log n

If tree is skewed:

Height ≈ n

Performance depends on height.

**Common mistake — off-by-one in height convention:** Two valid conventions exist and mixing them causes off-by-one errors. Pick one and stay consistent throughout the entire solution.

```
CONVENTION 1 — Count NODES (height = number of nodes on longest path):
  Height of null node = 0
  Height of leaf node = 1

CONVENTION 2 — Count EDGES (height = number of edges on longest path):
  Height of null node = -1
  Height of leaf node = 0

LeetCode problems typically use Convention 1 (null = 0).
```

```python
# Convention 1: Counting NODES (null = 0)
def height_by_nodes(node):
    if node is None:
        return 0
    return max(height_by_nodes(node.left),
               height_by_nodes(node.right)) + 1

# Convention 2: Counting EDGES (null = -1)
def height_by_edges(node):
    if node is None:
        return -1                         # null: -1 so that leaf = (-1+1) = 0
    return max(height_by_edges(node.left),
               height_by_edges(node.right)) + 1
```

**Common mistake — minimum depth counting non-leaf nodes:** Minimum depth is the distance to the nearest LEAF. A leaf has BOTH children as None. If a node has only one child, it is not a leaf — the minimum depth must go through that child.

```python
# WRONG: treats any node with a None child as a "leaf"
def min_depth_wrong(root):
    if root is None:
        return 0
    left = min_depth_wrong(root.left)
    right = min_depth_wrong(root.right)
    return min(left, right) + 1   # BUG: picks 0+1=1 for a node with no left child

# CORRECT: skip the missing-child direction
def min_depth(root):
    if root is None:
        return 0
    if root.left is None:
        return min_depth(root.right) + 1
    if root.right is None:
        return min_depth(root.left) + 1
    return min(min_depth(root.left), min_depth(root.right)) + 1
```

> [↑ Back to Top](#top)

<a id="11-balanced-vs-skewed"></a>
# 11. Balanced vs Skewed Tree

Balanced:

```
       4
      / \
     2   6
    / \ / \
   1  3 5  7
```

Height = 2

Skewed:

```
1
 \
  2
   \
    3
     \
      4
```

Height = 3

Skewed behaves like linked list.

> 📝 **Practice:** [Q39 · tree-height-balance](../dsa_practice_questions_100.md#q39--thinking--tree-height-balance)

**Common mistake — diameter vs height confusion:** Tree diameter (the longest path between any two nodes) is NOT the same as height. At each node, diameter through it equals left_height + right_height — but you can only return one value from a recursive function. Use a `nonlocal` variable to track the diameter separately while returning height.

```python
# WRONG: this computes height, not diameter
def diameter_wrong(node):
    if node is None:
        return 0
    left = diameter_wrong(node.left)
    right = diameter_wrong(node.right)
    return max(left, right) + 1   # this is height

# CORRECT: return height, but update diameter via nonlocal
def diameter_of_binary_tree(root):
    result = 0

    def height(node):
        nonlocal result
        if node is None:
            return 0
        left_h = height(node.left)
        right_h = height(node.right)
        result = max(result, left_h + right_h)   # diameter through this node
        return max(left_h, right_h) + 1          # height for parent

    height(root)
    return result
```

> [↑ Back to Top](#top)

<a id="12-why-powerful"></a>
# 12. Why Trees Are Powerful

Trees enable:

- Fast searching
- Hierarchical modeling
- Divide-and-conquer algorithms
- Efficient storage
- Decision making

Trees form foundation for:

- BST
- Heap
- Trie
- Segment Tree
- Graph algorithms

> [↑ Back to Top](#top)

<a id="13-real-world"></a>
# 13. Real-World Applications

- File system
- HTML DOM
- Database indexing
- Routing tables
- Game AI decision trees
- Expression parsing

Trees are everywhere.

> [↑ Back to Top](#top)

<a id="14-mental-model"></a>
# 14. Mental Model to Remember

Imagine a tree upside down.

Root at top.
Branches downward.

Each node controls subtrees below it.

When solving tree problems:

Think:

"If I know answer for left subtree and right subtree,
how do I combine them?"

That is tree thinking.

## Visual: Mental Model Summary

```
┌────────────────────────────────────────────────────────────┐
│  TREES — MENTAL MODELS                                     │
├────────────────────────────────────────────────────────────┤
│  Traversal    │ Think of it as...                          │
│  ─────────── │ ────────────────────────────────────────── │
│  Preorder     │ "Print the map BEFORE exploring"           │
│  Inorder      │ "Read a BST like a sorted list"            │
│  Postorder    │ "Bottom-up: children before parents"       │
│  Level-order  │ "Flood fill, ripple outward"               │
├────────────────────────────────────────────────────────────┤
│  Problem Type  │ Use...                                    │
│  ──────────── │ ──────────────────────────────────────── │
│  Path sums     │ Bottom-up, pass max gain upward           │
│  Max depth     │ Top-down or bottom-up both work           │
│  Diameter      │ Bottom-up ONLY (need both subtree heights)│
│  LCA           │ Bottom-up: bubble up found node           │
│  Serialize     │ Preorder (root first = easy to rebuild)   │
│  Validate BST  │ Inorder (should be sorted) OR top-down    │
│                │ with min/max bounds                       │
└────────────────────────────────────────────────────────────┘
```

> [↑ Back to Top](#top)

<a id="15-final-understanding"></a>
# 15. Final Understanding

Tree is:

- Hierarchical
- Recursive
- Branching
- Powerful
- Foundational

Understanding trees deeply unlocks:

- Binary Search Tree
- Heap
- Trie
- Graph
- Dynamic Programming on Trees

Trees are not just another topic.
They are a gateway to advanced DSA.

> [↑ Back to Top](#top)

<a id="16-level-order"></a>
# 16. Level-Order Traversal — BFS on Trees

> 📝 **Practice:** [Q8 · level-order-bfs](./practice.md#q8--level-order-traversal-bfs)

> Imagine photographing a tree from above, capturing one row at a time — roots first, then their children, then grandchildren. That's level-order traversal.

**Level-order traversal** visits nodes level by level using a queue (BFS). It is the go-to technique for any problem involving tree levels, width, or top-down relationships.

```python
from collections import deque

def level_order(root):
    if not root:
        return []

    result = []
    queue = deque([root])          # ← start with root

    while queue:
        level_size = len(queue)    # ← snapshot: how many nodes at this level
        level = []

        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)

        result.append(level)       # ← one sublist per level

    return result


# Tree:     1
#          / \
#         2   3
#        / \
#       4   5
# Output: [[1], [2, 3], [4, 5]]
```

> 📝 **Practice:** [Q36 · bfs-level-order](../dsa_practice_questions_100.md#q36--normal--bfs-level-order)


**Common level-order patterns:**
```python
# Right side view — last node at each level:
def right_side_view(root):
    result = []
    queue = deque([root]) if root else deque()
    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:    # ← last node at this level
                result.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
    return result

# Maximum width of tree — max nodes at any level:
def max_width(root):
    if not root: return 0
    max_w = 0
    queue = deque([root])
    while queue:
        max_w = max(max_w, len(queue))
        for _ in range(len(queue)):
            node = queue.popleft()
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
    return max_w
```

**Complexity:** O(n) time, O(n) space (queue holds up to n/2 nodes at widest level)

> [↑ Back to Top](#top)

<a id="17-serialization"></a>
# 17. Tree Serialization — Store and Rebuild Any Tree

> 📝 **Practice:** [Q21 · serialize-tree](./practice.md#q21--serialize-a-binary-tree) · [Q22 · deserialize-tree](./practice.md#q22--deserialize-a-binary-tree)

> Like saving a game — serialization encodes the entire tree into a string you can store, transmit, or reconstruct exactly.

**Serialization** converts a tree to a string. **Deserialization** rebuilds the exact tree from that string. The standard approach uses BFS (level-order) or preorder with null markers.

```python
# Preorder serialization — encodes structure via null markers
class Codec:
    def serialize(self, root):
        """Preorder DFS — mark None as 'N'."""
        vals = []

        def dfs(node):
            if not node:
                vals.append('N')    # ← null marker preserves structure
                return
            vals.append(str(node.val))
            dfs(node.left)
            dfs(node.right)

        dfs(root)
        return ','.join(vals)       # "1,2,N,N,3,N,N"

    def deserialize(self, data):
        """Rebuild using same preorder order."""
        vals = iter(data.split(','))

        def build():
            val = next(vals)
            if val == 'N':
                return None         # ← null → no node here
            node = TreeNode(int(val))
            node.left  = build()   # ← recurse same order
            node.right = build()
            return node

        return build()

# BFS serialization (LeetCode format):
def serialize_bfs(root):
    if not root: return ''
    queue = deque([root])
    vals = []
    while queue:
        node = queue.popleft()
        if node:
            vals.append(str(node.val))
            queue.append(node.left)    # ← append even if None
            queue.append(node.right)
        else:
            vals.append('N')
    return ','.join(vals)
```

**Why null markers matter:**
```
Tree:     1        Preorder without nulls: "1,2,3" — AMBIGUOUS
         / \       Preorder with nulls:    "1,2,N,N,3,N,N" — UNIQUE ✓
        2   3
```

**When this pattern appears:**
- LeetCode 297 (Serialize and Deserialize Binary Tree)
- Any problem requiring tree persistence or transmission
- Reconstruct binary tree from traversal output

> [↑ Back to Top](#top)

<a id="18-top-down-bottom-up"></a>
# 18. Top-Down vs Bottom-Up Thinking

## Visual: Top-Down — Pass information DOWN to children (parameters carry state)

**Example: Max Depth**

```
maxDepth(node, current_depth):
  if node is None: return current_depth
  return max(
      maxDepth(node.left,  current_depth + 1),
      maxDepth(node.right, current_depth + 1)
  )

Information flows DOWNWARD:
  maxDepth(1, 0)
       |
  passes depth=1 to children
       |
  maxDepth(2, 1)    maxDepth(3, 1)
       |
  passes depth=2 to children
       |
  maxDepth(4, 2)    maxDepth(5, 2)
  returns 2         returns 2
```

## Visual: Bottom-Up — Gather information FROM children (return values carry state)

**Example: Diameter of Tree**
The diameter is the longest path between any two nodes. It may or may not pass through the root.

```
At each node, ask: "what is the longest path through ME?"
Answer = left_height + right_height

            1
           / \
          2   3
         / \
        4   5

  At node 4: returns height 0 (leaf)
  At node 5: returns height 0 (leaf)
  At node 2: diameter candidate = 0 + 0 + 2 = 2 (path: 4→2→5)
             returns height = 1
  At node 3: returns height 0 (leaf)
  At node 1: diameter candidate = 1 + 0 + 2 = 3 (path: 4→2→1→3)
             ↑ this is the answer

  Information flows UPWARD (children return their heights).
  Parent uses return values to compute its own answer.
```

```
  TOP-DOWN:  I know something → I tell my children
  BOTTOM-UP: My children know something → they tell me
```

> [↑ Back to Top](#top)

<a id="19-path-problems"></a>
# 19. Path Problems

A path in a tree is a sequence of nodes where each consecutive pair is connected by an edge. **No node appears twice.**

## Visual: What Is a Valid Path?

```
            1
           / \
          2   3
         / \
        4   5

  VALID paths:
  4 → 2 → 5          (goes through node 2, left to right)
  4 → 2 → 1 → 3      (goes up to root then down)
  4 → 2              (just two nodes)
  1 → 3              (root to leaf)

  INVALID paths:
  4 → 2 → 1 → 2      (visits node 2 TWICE)
  4 → 5              (4 and 5 are not directly connected;
                       you would need to go through 2)
  3 → 1 → 2 → 1      (visits 1 twice)

Key insight: In a tree, there is EXACTLY ONE path between any two nodes.
```

## Visual: Maximum Path Sum — The classic bottom-up path problem

```
At each node:
  max_path_through_me = node.val + max(0, left_gain) + max(0, right_gain)
  max_path_as_root    = node.val + max(0, best_single_branch)

  Why max(0, ...)?  → We DROP a branch if it only makes the sum worse.
```

**Common mistake — max path sum missing cases:** The path can go through any node using EITHER or BOTH subtrees. Use `max(0, gain)` to exclude negative subtrees, and track the global maximum with a `nonlocal` variable or list — because the "bent" path through a node cannot be returned upward.

```python
def max_path_sum(root):
    max_sum = [float('-inf')]

    def gain(node):
        if node is None:
            return 0
        left_gain  = max(0, gain(node.left))    # exclude if negative
        right_gain = max(0, gain(node.right))   # exclude if negative

        # "Bent" path through this node — update global max
        max_sum[0] = max(max_sum[0], node.val + left_gain + right_gain)

        # Return straight path for the parent to extend
        return node.val + max(left_gain, right_gain)

    gain(root)
    return max_sum[0]
```

> [↑ Back to Top](#top)

<a id="20-lca"></a>
# 20. LCA — Lowest Common Ancestor

The LCA of two nodes p and q is the deepest node that has BOTH p and q as descendants (a node is a descendant of itself).

**Analogy:** Two hikers walking toward the peak. The LCA is where their paths FIRST meet going up.

## Visual: LCA Examples

```
Example tree:
            3
           / \
          5   1
         / \ / \
        6  2 0  8
          / \
         7   4

Case 1: LCA(6, 4)
  Path from 6 to root: 6 → 5 → 3
  Path from 4 to root: 4 → 2 → 5 → 3
  First common node:   5
  LCA = 5  ✓

Case 2: LCA(5, 4)
  Path from 5 to root: 5 → 3
  Path from 4 to root: 4 → 2 → 5 → 3
  First common:        5
  LCA = 5  (5 is its own ancestor!)  ✓

Case 3: LCA(6, 8)
  Path from 6: 6 → 5 → 3
  Path from 8: 8 → 1 → 3
  First common: 3
  LCA = 3  ✓
```

## Visual: The Recursive LCA Algorithm — Why it works

```python
def lca(node, p, q):
    if not node:        return None     # fell off tree
    if node == p:       return node     # found p — stop here
    if node == q:       return node     # found q — stop here

    left  = lca(node.left,  p, q)
    right = lca(node.right, p, q)

    if left and right:  return node     # p on one side, q on other → THIS is LCA
    return left or right                # both on same side → bubble up the found one
```

**Common mistake — using BST shortcut on a general tree:** The BST LCA shortcut (compare values to navigate left/right) only works when you KNOW the tree is a valid BST. On a general binary tree where node positions don't correlate with values, use the general algorithm that checks both subtrees.

```python
# WRONG for general trees: assumes BST property
def lca_wrong(root, p, q):
    if p.val < root.val and q.val < root.val:
        return lca_wrong(root.left, p, q)
    if p.val > root.val and q.val > root.val:
        return lca_wrong(root.right, p, q)
    return root

# CORRECT for general binary trees: check both subtrees
def lca_general(root, p, q):
    if root is None:
        return None
    if root == p or root == q:
        return root
    left  = lca_general(root.left,  p, q)
    right = lca_general(root.right, p, q)
    if left and right:
        return root           # p and q in different subtrees
    return left or right      # both in same subtree
```

> [↑ Back to Top](#top)

# Navigation

Previous:
[13_binary_search/interview.md](/02_DSA_Mastery/13_binary_search/interview.md)

Next:
[14_trees/interview.md](/02_DSA_Mastery/14_trees/interview.md)
[15_binary_search_trees/theory.md](/02_DSA_Mastery/15_binary_search_trees/theory.md)

**[🏠 Back to README](../README.md)**

**Prev:** [← Binary Search — Interview Q&A](../13_binary_search/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
