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

# 🔁 Navigation

Previous:  
[13_binary_search/interview.md](/dsa-complete-mastery/13_binary_search/interview.md)

Next:  
[14_trees/interview.md](/dsa-complete-mastery/14_trees/interview.md)  
[15_binary_search_trees/theory.md](/dsa-complete-mastery/15_binary_search_trees/theory.md)

