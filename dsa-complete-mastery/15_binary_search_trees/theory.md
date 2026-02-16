# 📘 Binary Search Tree (BST) — The Organized Tree

> A normal tree is like a family.
> A Binary Search Tree is like a family with rules.
>
> Every node follows a strict ordering rule.
>
> That rule makes searching very fast.

BST is where trees become efficient.

---

# 🌳 1️⃣ Real Life Story — Organized Library Shelves

Imagine a library where books are randomly placed.

Searching takes time.

Now imagine a library where:

- All smaller-numbered books go to left shelf
- All larger-numbered books go to right shelf

Every shelf follows same rule.

Now searching becomes fast.

That is BST.

---

# 📜 2️⃣ The BST Rule (Very Important)

For every node:

All values in left subtree < node value  
All values in right subtree > node value

That’s it.

This simple rule creates power.

---

# 🌲 3️⃣ Visual Example

Insert numbers:

```
5, 3, 7, 2, 4, 6, 8
```

Tree becomes:

```
        5
       / \
      3   7
     / \ / \
    2  4 6  8
```

Observe:

Left side always smaller.
Right side always larger.

Ordered tree.

---

# 🔍 4️⃣ Why BST Is Powerful

Because it combines:

- Tree structure
- Binary search logic

Searching in BST:

Compare with root.
If smaller → go left.
If larger → go right.

Time:
O(h)

If balanced:
h ≈ log n

Fast.

---

# 🧠 5️⃣ Searching in BST (Step by Step)

Example:
Search 6.

Start at root (5).

6 > 5 → go right.

Now at 7.

6 < 7 → go left.

Found 6.

You didn’t check every node.

You eliminated half at each step.

Binary search inside tree.

---

# ➕ 6️⃣ Insertion in BST

Insert follows same rule.

Example:
Insert 1.

1 < 5 → go left.
1 < 3 → go left.
1 < 2 → go left.

Place as left child of 2.

Tree grows according to rule.

Time:
O(h)

---

# ❌ 7️⃣ Deletion in BST (Most Important)

Deletion has 3 cases:

---

## 🔹 Case 1: Leaf Node

Simply remove.

---

## 🔹 Case 2: One Child

Replace node with its child.

---

## 🔹 Case 3: Two Children

Replace with:

- Inorder successor (smallest in right subtree)
OR
- Inorder predecessor (largest in left subtree)

Then delete that successor node.

This preserves BST rule.

Deletion tests understanding deeply.

---

# 📏 8️⃣ Height of BST

Performance depends on height.

Balanced BST:

```
Height ≈ log n
```

Worst case (skewed):

```
Height ≈ n
```

Example skewed tree:

Insert 1,2,3,4,5 in order.

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

Behaves like linked list.

Search becomes O(n).

---

# ⚖️ 9️⃣ Balanced vs Unbalanced BST

Balanced:
Fast operations.

Unbalanced:
Slow operations.

That’s why balanced BSTs exist:

- AVL Tree
- Red-Black Tree

They maintain height ≈ log n.

---

# 🔄 1️⃣0️⃣ Inorder Traversal of BST

Important property:

Inorder traversal of BST gives sorted order.

Example:

```
2 3 4 5 6 7 8
```

This is key property.

Used in many problems.

---

# 🧩 1️⃣1️⃣ Common BST Operations

- Search
- Insert
- Delete
- Find minimum
- Find maximum
- Find successor
- Find predecessor
- Validate BST

All rely on ordering rule.

---

# 🧠 1️⃣2️⃣ Validate BST

Check:

Left subtree max < node value  
Right subtree min > node value

Can be done using:

- Inorder traversal
- Min/max range recursion

Important interview question.

---

# 🌍 1️⃣3️⃣ Real-World Usage

BST used in:

- Database indexing
- Symbol tables
- Ordered maps
- File systems
- Scheduling systems
- C++ STL set/map (Red-Black Tree)

Ordered structures rely on BST logic.

---

# ⚠️ 1️⃣4️⃣ Common Mistakes

- Confusing BST with binary tree
- Not handling deletion correctly
- Forgetting strict inequality
- Not checking entire subtree in validation
- Assuming balanced automatically

BST requires strict rule checking.

---

# 🧠 1️⃣5️⃣ Mental Model

Think of BST as:

A decision tree.

At each node:

You decide:
Left or right?

You eliminate half possibilities.

BST is tree version of binary search.

---

# 📌 Final Understanding

Binary Search Tree is:

- Ordered tree
- Efficient search structure
- Logarithmic if balanced
- Foundation for advanced trees
- Base for self-balancing trees

Understanding BST unlocks:

- AVL Tree
- Red-Black Tree
- Segment Tree
- TreeMap / OrderedSet
- Many interview problems

BST is where trees become practical.

---

# 🔁 Navigation

Previous:  
[14_trees/interview.md](/dsa-complete-mastery/14_trees/interview.md)

Next:  
[15_binary_search_trees/interview.md](/dsa-complete-mastery/15_binary_search_trees/interview.md)  
[16_heaps/theory.md](/dsa-complete-mastery/16_heaps/theory.md)

