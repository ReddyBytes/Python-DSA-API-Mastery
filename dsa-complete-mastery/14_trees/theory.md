# 📘 Trees — The Structure of Hierarchy

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

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
tree terminology · binary tree structure · inorder/preorder/postorder traversal · level-order traversal

**Should Learn** — Important for real projects, comes up regularly:
recursion pattern for trees · tree serialization · height and depth · balanced vs skewed

**Good to Know** — Useful in specific situations, not always tested:
path sum problems · tree reconstruction from traversals

**Reference** — Know it exists, look up syntax when needed:
Morris traversal · N-ary trees

---

# 🌳 1️⃣ Real Life Story — Family Tree

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

---

# 🌍 2️⃣ Why Do We Need Trees?

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

---

# 🌱 3️⃣ What Is a Tree (Definition)

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

---

# 🧩 4️⃣ Basic Terminology (Very Important)

Let’s understand deeply.

---

## 🔹 Node

Each element in tree.

Example:

```
A
```

A is node.

---

## 🔹 Root

Topmost node.

Only one root.

---

## 🔹 Parent

Node that has children.

---

## 🔹 Child

Node connected below parent.

---

## 🔹 Leaf

Node with no children.

---

## 🔹 Subtree

Tree inside tree.

---

## 🔹 Height

Number of edges from root to deepest leaf.

---

## 🔹 Depth

Distance from root to a node.

---

# 🌳 5️⃣ Binary Tree — Most Important Type

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

---

# 📦 6️⃣ How Is Tree Stored in Python?

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

---

# 🔍 7️⃣ Tree Traversal — Exploring the Tree

Traversal means:
Visiting all nodes.

Three main types:

---

## 🔹 Inorder (Left → Root → Right)

```
Visit left
Visit node
Visit right
```

Used in BST to get sorted order.

---

## 🔹 Preorder (Root → Left → Right)

Used for copying tree.

---

## 🔹 Postorder (Left → Right → Root)

Used for deletion.

---

# 📊 8️⃣ Visual Traversal Example

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

---

# 🔁 9️⃣ Recursion and Trees

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

---

# 📏 1️⃣0️⃣ Height of Tree

Height determines performance.

If tree is balanced:

Height ≈ log n

If tree is skewed:

Height ≈ n

Performance depends on height.

---

# ⚖️ 1️⃣1️⃣ Balanced vs Skewed Tree

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

---

# 🧠 1️⃣2️⃣ Why Trees Are Powerful

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

---

# 🔥 1️⃣3️⃣ Real-World Applications

- File system
- HTML DOM
- Database indexing
- Routing tables
- Game AI decision trees
- Expression parsing

Trees are everywhere.

---

# ⚠️ 1️⃣4️⃣ Common Mistakes

- Forgetting base case in recursion
- Not checking null
- Confusing depth vs height
- Assuming balanced tree
- Stack overflow in deep recursion

Tree recursion requires careful thinking.

---

# 🏆 1️⃣5️⃣ Mental Model to Remember

Imagine a tree upside down.

Root at top.
Branches downward.

Each node controls subtrees below it.

When solving tree problems:

Think:

“If I know answer for left subtree and right subtree,
how do I combine them?”

That is tree thinking.

---

# 📌 Final Understanding

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

---

## 🌊 Level-Order Traversal — BFS on Trees

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

---

## 📦 Tree Serialization — Store and Rebuild Any Tree

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

---

# 🔁 Navigation

Previous:
[13_binary_search/interview.md](/dsa-complete-mastery/13_binary_search/interview.md)

Next:  
[14_trees/interview.md](/dsa-complete-mastery/14_trees/interview.md)  
[15_binary_search_trees/theory.md](/dsa-complete-mastery/15_binary_search_trees/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Binary Search — Interview Q&A](../13_binary_search/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
