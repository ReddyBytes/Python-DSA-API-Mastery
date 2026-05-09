<a id="top"></a>
# 📘 14 – Trees in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is a Tree?](#1-what-is-a-tree)
  - [Visual: Family Tree with Vocabulary](#visual-family-tree)
  - [Why Trees?](#why-trees)
- [2. Tree Terminology](#2-terminology)
  - [Visual: Height vs Depth](#visual-height-depth)
- [3. Binary Tree](#3-binary-tree)
  - [Visual: Common Shapes](#visual-shapes)
- [4. How Trees Are Stored in Python](#4-python-storage)
- [5. Tree Traversal](#5-traversal)
  - [Visual: All 4 Traversals Step by Step](#visual-all-traversals)
  - [Level-Order Traversal (BFS)](#level-order)
- [6. Recursion and Trees](#6-recursion)
  - [Visual: Recursive Call Stack](#visual-call-stack)
- [7. Height of Tree](#7-height)
- [8. Balanced vs Skewed](#8-balanced-skewed)
- [9. Tree Serialization](#9-serialization)
- [10. Advanced Tree Patterns](#10-advanced)
  - [Top-Down vs Bottom-Up](#top-down-bottom-up)
  - [Path Problems](#path-problems)
  - [LCA — Lowest Common Ancestor](#lca)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
tree terminology · binary tree structure · inorder/preorder/postorder traversal · level-order traversal

**Should Learn** — Important for real projects, comes up regularly:
recursion pattern for trees · tree serialization · height and depth · balanced vs skewed

**Good to Know** — Useful in specific situations, not always tested:
path sum problems · tree reconstruction from traversals · LCA

**Reference** — Know it exists, look up syntax when needed:
Morris traversal · N-ary trees · threaded binary trees

Rowan is a botanist. He studies real trees — not the ones with leaves and bark, but the abstract structures that mirror how nature organizes information. A tree starts at one root, branches into children, and spreads outward until it reaches leaves. No cycles. No shortcuts. Just a clean hierarchy from top to bottom. Today Rowan will learn why this structure is the backbone of file systems, databases, compilers, and nearly every interview problem involving hierarchical data.

<a id="1-what-is-a-tree"></a>
# 1. What Is a Tree?

Rowan starts with the most natural tree he knows — his own family tree. Grandparents at the top (the root), parents in the middle (internal nodes), and himself and his siblings at the bottom (leaves). Each person has exactly one parent. No person is their own ancestor. That is a tree.

```
Rowan's Family Tree:

         Grandfather
         /          \
     Father        Uncle
     /    \          |
  Rowan  Sister   Cousin
```

<a id="visual-family-tree"></a>
## Visual: Family Tree with Full Vocabulary

```
           [A]  ← Root (no parent)
          /   \
        [B]   [C]  ← Children of A, Siblings of each other
       / | \    |
     [D][E][F] [G]  ← D,E,F are children of B; G is child of C
         |
        [H]  ← H is child of E, grandchild of B

Vocabulary:
  Root:     A (the topmost node, has no parent)
  Parent:   B is parent of D, E, F
  Child:    D, E, F are children of B
  Leaf:     D, F, G, H (nodes with no children)
  Subtree:  B and everything below it is a subtree
  Siblings: B and C share the same parent (A)
  Ancestor: A and B are ancestors of H
  Depth:    Distance from root (A=0, B=1, E=2, H=3)
  Height:   Distance from deepest leaf (H=0, E=1, B=2, A=3)
```

<a id="why-trees"></a>
## Why Trees?

Rowan asks: "Why not just use arrays or linked lists?" Because not everything is linear. Many real-world relationships are hierarchical:

- File systems (folders inside folders)
- Organization charts (managers → reports)
- HTML/XML documents (nested tags)
- Decision making (yes/no branches)
- Database indexes (B-trees for fast search)

Trees represent **one-to-many** relationships. Arrays can only represent sequences. Trees model hierarchy.

A tree is defined by these properties:
- One root node (no parent)
- Every other node has exactly one parent
- No cycles (you can never loop back to an ancestor)
- Connected (every node is reachable from the root)

> 📝 **Practice:** [Q1 · tree-node-definition](./practice.md#q1--tree-node-definition)

> [↑ Back to Top](#top)

<a id="2-terminology"></a>
# 2. Tree Terminology

Rowan memorizes the vocabulary that interviewers use constantly. Getting these wrong in an interview signals "has not studied trees."

| Term | Meaning |
|---|---|
| **Node** | A single element in the tree (holds data + references to children) |
| **Root** | The topmost node (has no parent) |
| **Parent** | The node directly above (every non-root node has exactly one) |
| **Child** | A node directly below |
| **Leaf** | A node with no children (terminal node) |
| **Subtree** | A node and all its descendants |
| **Height** | Distance from a node down to its deepest leaf |
| **Depth** | Distance from the root down to a node |
| **Level** | All nodes at the same depth |
| **Degree** | Number of children a node has |

<a id="visual-height-depth"></a>
## Visual: Height vs Depth

These are the most commonly confused terms. Height goes DOWN. Depth goes DOWN FROM ROOT.

```
            [A]        depth=0, height=3
           /   \
         [B]   [C]     depth=1, height=2 (B), height=1 (C)
        /   \    \
      [D]   [E]  [F]   depth=2, height=0 (D,F), height=1 (E)
             |
            [G]         depth=3, height=0

Height of a node = longest path DOWN to a leaf
Depth of a node = path from root DOWN to that node

Height of TREE = height of root = 3
Depth of TREE = maximum depth of any node = 3
```

```
CRITICAL: height is measured from the BOTTOM up.
          depth is measured from the TOP down.

Think of it like a building:
  - The HEIGHT of a building is measured from ground UP
  - The DEPTH of a basement is measured from ground DOWN
  - Root is the ground floor
```

> [↑ Back to Top](#top)

<a id="3-binary-tree"></a>
# 3. Binary Tree

Rowan learns that the most important type of tree in DSA is the **binary tree** — where each node has at most 2 children (left and right). This constraint makes traversal patterns elegant and enables powerful algorithms.

Binary Tree means: each node has at most 2 children.

```
Binary (max 2 children):       Not binary (3 children):

       [A]                          [A]
      /   \                       / | \
    [B]   [C]                   [B][C][D]
   /   \
 [D]   [E]
```

<a id="visual-shapes"></a>
## Visual: Common Binary Tree Shapes

```
Perfect Binary Tree — Every level is completely full:

           [1]
          /   \
        [2]   [3]
       / \   / \
     [4][5] [6][7]

Every non-leaf has exactly 2 children.
All leaves are at the same level.
n nodes in a perfect tree of height h: n = 2^(h+1) - 1


Complete Binary Tree — All levels full except possibly last (filled left to right):

           [1]
          /   \
        [2]   [3]
       / \   /
     [4][5] [6]

Used in: heaps (always a complete binary tree).


Full Binary Tree — Every node has either 0 or 2 children (never 1):

           [1]
          /   \
        [2]   [3]
             / \
           [4] [5]


Skewed Binary Tree — Every node has only one child:

    [1]
      \
      [2]
        \
        [3]
          \
          [4]

This is essentially a linked list — O(n) height.
```

> [↑ Back to Top](#top)

<a id="4-python-storage"></a>
# 4. How Trees Are Stored in Python

Rowan learns that Python does not have a built-in tree class. He builds one from scratch — each node is an object with a value and two pointers.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

Building a tree:

```python
#       1
#      / \
#     2   3
#    / \
#   4   5

root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)
```

Each node exists independently on the heap. They are connected only by `left` and `right` references — just like linked list nodes.

> [↑ Back to Top](#top)

<a id="5-traversal"></a>
# 5. Tree Traversal

Rowan needs to visit every node in his tree. But unlike a linear array where you just go left to right, a tree branches — you must choose a strategy. There are four fundamental orderings, and they determine the order in which nodes are visited.

**DFS (Depth-First Search)** — go deep before going wide:
- **Inorder:** Left → Root → Right (gives sorted order for BSTs)
- **Preorder:** Root → Left → Right (used for serialization)
- **Postorder:** Left → Right → Root (used for deletion/evaluation)

**BFS (Breadth-First Search)** — go wide before going deep:
- **Level-order:** Level by level, left to right

```python
# Inorder (Left → Root → Right)
def inorder(node):
    if not node: return
    inorder(node.left)
    print(node.val)
    inorder(node.right)

# Preorder (Root → Left → Right)
def preorder(node):
    if not node: return
    print(node.val)
    preorder(node.left)
    preorder(node.right)

# Postorder (Left → Right → Root)
def postorder(node):
    if not node: return
    postorder(node.left)
    postorder(node.right)
    print(node.val)
```

> 📝 **Practice:** [Q2–Q8 · all-traversals](./practice.md#q2--inorder-traversal-recursive)

<a id="visual-all-traversals"></a>
## Visual: All 4 Traversals Step by Step

```
            Tree used for all examples:

                    1
                   / \
                  2   3
                 / \   \
                4   5   6
```

## DFS — Preorder (Root → Left → Right)

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

## DFS — Inorder (Left → Root → Right)

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

## DFS — Postorder (Left → Right → Root)

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

## BFS — Level-order (Level by Level)

Use a queue. Visit all nodes at depth d before depth d+1.

```
Queue state:       Visited:
[1]            →   []
[2, 3]         →   [1]
[4, 5, 6]      →   [1, 2, 3]
[]             →   [1, 2, 3, 4, 5, 6]

Result:  1 → 2 → 3 → 4 → 5 → 6
```

## Side-by-Side Summary

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
  Go right from 2: visit 5 (leaf, backtrack)
  Go right from 1: visit 3
  Go right: visit 6

Output: [1, 2, 4, 5, 3, 6]
```

```
DFS — Inorder (Left → Root → Right):

Visit order: 4 → 2 → 5 → 1 → 3 → 6

Process:
  Go left from 1 → go left from 2 → hit 4 (leaf)
  Visit 4
  Back to 2: visit 2
  Go right from 2: visit 5
  Back to 1: visit 1
  Go right from 1 → visit 3
  Go right from 3: visit 6

Output: [4, 2, 5, 1, 3, 6]
```

```
DFS — Postorder (Left → Right → Root):

Visit order: 4 → 5 → 2 → 6 → 3 → 1

Process:
  Go all the way down-left: hit 4 → visit 4
  Go right from 2: visit 5
  Now visit 2 (both children done)
  Go right from 1: go right from 3: visit 6
  Visit 3 (children done)
  Visit 1 (root last!)

Output: [4, 5, 2, 6, 3, 1]
```

```
BFS — Level-order (Level by Level):

Level 0: [1]
Level 1: [2, 3]
Level 2: [4, 5, 6]

Output: [1, 2, 3, 4, 5, 6]

Uses a QUEUE:
  Queue: [1]      → dequeue 1, enqueue 2, 3
  Queue: [2, 3]   → dequeue 2, enqueue 4, 5
  Queue: [3, 4, 5]→ dequeue 3, enqueue 6
  Queue: [4, 5, 6]→ dequeue all (leaves)
```

```
Side-by-side summary:

Traversal    Order              Output          Use Case
──────────────────────────────────────────────────────────────
Preorder     Root, Left, Right  [1,2,4,5,3,6]  Copy/serialize tree
Inorder      Left, Root, Right  [4,2,5,1,3,6]  Sorted order (BST)
Postorder    Left, Right, Root  [4,5,2,6,3,1]  Delete tree, eval expr
Level-order  Level by level     [1,2,3,4,5,6]  BFS, shortest path
```

<a id="level-order"></a>
## Level-Order Traversal (BFS)

Rowan uses a queue to visit each level completely before moving to the next:

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result

# Tree:     1
#          / \
#         2   3
#        / \
#       4   5
# Output: [[1], [2, 3], [4, 5]]
```

## Common Level-Order Patterns

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

> 📝 **Practice:** [Q36 · bfs-level-order](../dsa_practice_questions_100.md#q36--normal--bfs-level-order)

> [↑ Back to Top](#top)

<a id="6-recursion"></a>
# 6. Recursion and Trees

Rowan discovers that trees and recursion are natural partners. Every subtree is itself a tree — the perfect self-similar structure for recursive thinking. The pattern: solve for the current node, then recursively solve for left and right children.

The recursive pattern for trees:
1. Base case: if node is None, return
2. Process current node (or recurse first, depending on order)
3. Recurse on left subtree
4. Recurse on right subtree

<a id="visual-call-stack"></a>
## Visual: Recursive Call Stack — Inorder Traversal

```
Tree:     1
         / \
        2   3

inorder(1):
  ├── inorder(2):
  │   ├── inorder(None) → return
  │   ├── VISIT 2 ✓
  │   └── inorder(None) → return
  ├── VISIT 1 ✓
  └── inorder(3):
      ├── inorder(None) → return
      ├── VISIT 3 ✓
      └── inorder(None) → return

Output: [2, 1, 3]
```

```
Call stack at deepest point (visiting node 2):

  ┌────────────────────┐
  │ inorder(None)      │ ← base case, returns
  ├────────────────────┤
  │ inorder(2)         │ ← about to visit 2
  ├────────────────────┤
  │ inorder(1)         │ ← waiting for left subtree
  └────────────────────┘

Space complexity: O(h) where h = height of tree
  Balanced tree: O(log n)
  Skewed tree:   O(n)
```

> 📝 **Practice:** [Q9 · tree-height](./practice.md#q9--tree-height)

> [↑ Back to Top](#top)

<a id="7-height"></a>
# 7. Height of Tree

Rowan learns that "height" is one of the most important tree properties — it determines the time complexity of most tree operations. But there is a subtle trap: two valid conventions exist, and mixing them causes bugs.

```python
# Convention 1: Counting NODES (null = 0, leaf = 1)
def height_nodes(node):
    if node is None:
        return 0
    return 1 + max(height_nodes(node.left), height_nodes(node.right))

# Convention 2: Counting EDGES (null = -1, leaf = 0)
def height_edges(node):
    if node is None:
        return -1
    return 1 + max(height_edges(node.left), height_edges(node.right))
```

**Common mistake — mixing conventions:** If you use `return 0` for None (convention 1) but expect leaf height to be 0, your results will be off by 1 everywhere. Pick one convention and use it consistently.

```
Tree:     1
         / \
        2   3
       /
      4

Convention 1 (nodes): height(1)=3, height(2)=2, height(4)=1
Convention 2 (edges): height(1)=2, height(2)=1, height(4)=0
```

> [↑ Back to Top](#top)

<a id="8-balanced-skewed"></a>
# 8. Balanced vs Skewed

Rowan learns that the shape of a tree determines its efficiency. A balanced tree gives O(log n) operations. A skewed tree degrades to O(n) — it is essentially a linked list.

```
Balanced (height = log n):          Skewed (height = n):

         [1]                          [1]
        /   \                           \
      [2]   [3]                         [2]
     / \   / \                            \
   [4][5] [6][7]                          [3]
                                            \
                                            [4]

Operations: O(log n)               Operations: O(n)
```

**Balanced** means: for every node, the height difference between left and right subtrees is at most 1. This is the AVL tree invariant.

```python
def is_balanced(root):
    def check(node):
        if not node:
            return 0
        left_h = check(node.left)
        if left_h == -1:
            return -1
        right_h = check(node.right)
        if right_h == -1:
            return -1
        if abs(left_h - right_h) > 1:
            return -1
        return 1 + max(left_h, right_h)

    return check(root) != -1
```

> [↑ Back to Top](#top)

<a id="9-serialization"></a>
# 9. Tree Serialization

Rowan needs to save a tree to a file and rebuild it later. He cannot just dump node values — the structure (which node is whose child) must be preserved. This is **serialization**: converting a tree to a string, and **deserialization**: rebuilding the tree from that string.

> 📝 **Practice:** [Q21 · serialize-tree](./practice.md#q21--serialize-a-binary-tree) · [Q22 · deserialize-tree](./practice.md#q22--deserialize-a-binary-tree)

## Preorder Serialization (with null markers)

```python
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
```

**Why null markers matter:**
```
Tree:     1        Preorder without nulls: "1,2,3" — AMBIGUOUS
         / \       Preorder with nulls:    "1,2,N,N,3,N,N" — UNIQUE ✓
        2   3

Without nulls, "1,2,3" could be:
    1           1         1
   / \           \       /
  2   3           2     2
                   \     \
                    3     3

With null markers, the structure is unambiguous.
```

## BFS Serialization (LeetCode format)

```python
from collections import deque

def serialize_bfs(root):
    if not root:
        return "[]"
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node:
            result.append(str(node.val))
            queue.append(node.left)    # ← append even if None
            queue.append(node.right)
        else:
            result.append("null")
    # Remove trailing nulls for cleaner output
    while result and result[-1] == "null":
        result.pop()
    return "[" + ",".join(result) + "]"

# Tree:     1
#          / \
#         2   3
#            / \
#           4   5
# BFS: "[1,2,3,null,null,4,5]"
```

**When this pattern appears:**
- LeetCode 297 (Serialize and Deserialize Binary Tree)
- Any problem requiring tree persistence or transmission
- Reconstruct binary tree from traversal output

> [↑ Back to Top](#top)

<a id="10-advanced"></a>
# 10. Advanced Tree Patterns

Rowan tackles the three patterns that appear in every medium/hard tree interview problem: choosing between top-down and bottom-up thinking, solving path problems, and finding the lowest common ancestor.

<a id="top-down-bottom-up"></a>
## Top-Down vs Bottom-Up

**Top-Down** — pass information DOWN to children (parameters carry state):

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

```python
def has_path_sum(root, target):
    def dfs(node, current_sum):
        if not node:
            return False
        current_sum += node.val
        if not node.left and not node.right:
            return current_sum == target
        return dfs(node.left, current_sum) or dfs(node.right, current_sum)
    return dfs(root, 0)
```

**Bottom-Up** — collect information UP from children (return values carry state):

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

```python
def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

```
  TOP-DOWN:  I know something → I tell my children
  BOTTOM-UP: My children know something → they tell me

  Top-Down use cases:  path sum, root-to-leaf paths, depth tracking
  Bottom-Up use cases: height, diameter, subtree count, balanced check
```

<a id="path-problems"></a>
## Path Problems

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

## Maximum Path Sum — The Classic Bottom-Up Problem

```
At each node:
  max_path_through_me = node.val + max(0, left_gain) + max(0, right_gain)
  max_path_as_extension = node.val + max(0, best_single_branch)

  Why max(0, ...)?  → We DROP a branch if it only makes the sum worse.

Tree:    -10
        /    \
       9      20
             /  \
            15   7

Best path: 15 → 20 → 7 = 42
```

**Common mistake — max path sum missing cases:** The path can use EITHER or BOTH subtrees at each node. Use `max(0, gain)` to exclude negative subtrees, and track the global maximum with a `nonlocal` variable or list — because the "bent" path through a node cannot be returned upward (parent can only extend one direction).

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

<a id="lca"></a>
## LCA — Lowest Common Ancestor

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

## The Recursive LCA Algorithm — Why It Works

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

**For BST (sorted):** use the property that LCA is where p and q split:

```python
def lca_bst(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left      # both in left subtree
        elif p.val > root.val and q.val > root.val:
            root = root.right     # both in right subtree
        else:
            return root           # split point = LCA
```

**Common mistake — using BST shortcut on a general tree:** The BST LCA shortcut (compare values to navigate left/right) only works when the tree is a valid BST. On a general binary tree, use the algorithm that checks both subtrees.

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

| Concept | Key Takeaway |
|---------|-------------|
| Tree | Hierarchical: one root, no cycles, one parent per node |
| Binary tree | Each node has at most 2 children |
| Height | Down to deepest leaf. Balanced=O(log n). Skewed=O(n) |
| Traversals | Inorder (sorted BST), Preorder (copy), Postorder (delete), Level (BFS) |
| Recursion | Trees are self-similar — subtree is itself a tree |
| Balanced vs Skewed | Balanced=efficient. Skewed=linked list |
| Serialization | Tree ↔ string for storage |
| Top-Down | Pass state down via parameters |
| Bottom-Up | Collect results up via return values |
| LCA | Where paths to p and q diverge |

**Why trees are powerful:**
- O(log n) search, insert, delete in balanced trees
- Hierarchical representation of real-world data
- Natural fit for recursive algorithms
- Foundation for BSTs, heaps, tries, segment trees
- Enable efficient range queries and ordered operations

**Trees enable things that flat structures cannot:**
- Fast search (balanced BST beats linear scan)
- Fast insert + delete (unlike sorted arrays which shift)
- Hierarchy modeling (file systems, org charts, DOM)
- Priority-based access (heaps)
- Prefix matching (tries)

**Real-world applications:**
- **File systems** — directory hierarchy (each folder is a subtree)
- **DOM** — HTML document structure (nested tags)
- **Database indexes** — B-trees, B+ trees (every SQL query you run)
- **Compilers** — abstract syntax trees (parsing `2 + 3 * 4`)
- **AI/ML** — decision trees, random forests
- **Networking** — routing hierarchies, DNS tree
- **Version control** — Git commit trees
- **Operating systems** — process trees (parent/child processes)

**Mental model:** A tree is an upside-down tree in nature. The root is at the top. Branches spread downward. Leaves are at the bottom. You can reach any node from the root by following exactly one path — no shortcuts, no cycles. Every algorithm on trees exploits this single-path property.

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [13_binary_search → theory.md](../13_binary_search/theory.md) |
| ➡ Next Module | [15_binary_search_trees → theory.md](../15_binary_search_trees/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[13 Binary Search →](../13_binary_search/theory.md) · [15 BST →](../15_binary_search_trees/theory.md) · [16 Heaps →](../16_heaps/theory.md) · [17 Trie →](../17_trie/theory.md)

**Jump to specific topics in other files:**
- BST operations → [15_binary_search_trees § theory.md](../15_binary_search_trees/theory.md)
- Heap (complete binary tree) → [16_heaps § theory.md](../16_heaps/theory.md)
- Trie (prefix tree) → [17_trie § theory.md](../17_trie/theory.md)
- DFS/BFS in graphs → [18_graphs § theory.md](../18_graphs/theory.md)
- Recursion patterns → [04_recursion § Common Patterns](../04_recursion/theory.md#7-common-patterns)

> [↑ Back to Top](#top)
