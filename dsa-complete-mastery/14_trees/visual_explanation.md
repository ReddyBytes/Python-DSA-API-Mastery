# Trees — Visual Explanation

---

## 1. WHAT IS A TREE?

**Analogy: Family Tree**

A tree is a hierarchy of nodes connected by edges, with exactly one root and no cycles.
Every node has exactly one parent (except the root).

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

---

## 2. ALL 4 TRAVERSALS ON THE SAME TREE

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

---

## 3. RECURSIVE CALL STACK — INORDER TRAVERSAL

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

---

## 4. HEIGHT vs DEPTH

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

---

## 5. COMMON TREE SHAPES

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

---

## 6. TOP-DOWN vs BOTTOM-UP THINKING

### Top-Down — Pass information DOWN to children (parameters carry state)

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

### Bottom-Up — Gather information FROM children (return values carry state)

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

---

## 7. PATH PROBLEMS — WHAT IS A PATH?

A path in a tree is a sequence of nodes where each consecutive pair is connected by an edge. **No node appears twice.**

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

### Maximum Path Sum — The classic bottom-up path problem

```
At each node:
  max_path_through_me = node.val + max(0, left_gain) + max(0, right_gain)
  max_path_as_root    = node.val + max(0, best_single_branch)

  Why max(0, ...)?  → We DROP a branch if it only makes the sum worse.
```

---

## 8. LCA — LOWEST COMMON ANCESTOR

The LCA of two nodes p and q is the deepest node that has BOTH p and q as descendants (a node is a descendant of itself).

**Analogy:** Two hikers walking toward the peak. The LCA is where their paths FIRST meet going up.

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

Case 4: LCA(7, 0)
  Path from 7: 7 → 2 → 5 → 3
  Path from 0: 0 → 1 → 3
  First common: 3
  LCA = 3  ✓

Case 5: LCA(2, 4)
  Path from 2: 2 → 5 → 3
  Path from 4: 4 → 2 → 5 → 3
  First common: 2
  LCA = 2  (2 contains 4 in its subtree!)  ✓
```

### The Recursive LCA Algorithm — Why it works

```
def lca(node, p, q):
    if not node:        return None     # fell off tree
    if node == p:       return node     # found p — stop here
    if node == q:       return node     # found q — stop here

    left  = lca(node.left,  p, q)
    right = lca(node.right, p, q)

    if left and right:  return node     # p on one side, q on other → THIS is LCA
    return left or right                # both on same side → bubble up the found one

Visual for LCA(6, 4):
            3           ← left=5, right=None → returns 5
           / \
          5   1         ← 5: left=6(found), right=None... wait
         / \ / \           actually: left=6, right=4 → returns 5  ✓
        6  2 0  8
          / \
         7   4
```

---

## MENTAL MODEL SUMMARY

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

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
