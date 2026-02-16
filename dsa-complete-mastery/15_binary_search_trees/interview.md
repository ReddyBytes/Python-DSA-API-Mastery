# 🎯 Binary Search Tree (BST) — Interview Preparation Guide

> BST questions test whether you truly understand:
> - Tree recursion
> - Ordered properties
> - Binary search logic
> - Height impact on performance
>
> Most candidates know traversal.
> Strong candidates understand ordering invariants.

---

# 🔎 How BST Questions Appear in Interviews

Rarely asked:
“Define BST.”

More commonly:

- Search in BST
- Insert into BST
- Delete node in BST
- Validate BST
- Kth smallest element
- Lowest common ancestor (BST version)
- Convert sorted array to BST
- Find floor/ceil
- Inorder successor
- Trim BST

If you see:
- Sorted property
- Ordered tree
- “Less than” / “Greater than”
- Efficient search in tree

Think: **BST**

---

# 🧠 How to Respond Before Coding

Instead of:

“I’ll solve using tree.”

Say:

> “Since the tree follows the binary search property, we can use ordered comparisons to eliminate half the search space at each step.”

That shows deep understanding.

---

# 🔹 Basic Level Questions (0–2 Years)

---

## 1️⃣ What is a Binary Search Tree?

Professional answer:

A Binary Search Tree is a binary tree where for every node, all values in its left subtree are smaller and all values in its right subtree are larger.

Mention “for every node.”

---

## 2️⃣ What is Time Complexity of Search?

Search time = O(h)

If balanced:
O(log n)

If skewed:
O(n)

Always mention both cases.

---

## 3️⃣ How to Insert in BST?

Logic:

If value < node:
Go left.

If value > node:
Go right.

Insert at null position.

Time:
O(h)

Explain traversal clearly.

---

## 4️⃣ How to Find Minimum and Maximum?

Minimum:
Keep going left.

Maximum:
Keep going right.

Because left subtree always smaller.

---

# 🔹 Intermediate Level Questions (2–5 Years)

---

## 5️⃣ Delete Node in BST

Most common tricky question.

Three cases:

### Case 1: Leaf
Remove directly.

### Case 2: One Child
Replace node with child.

### Case 3: Two Children
Replace with inorder successor (smallest in right subtree).

Then delete successor.

Explain why this preserves BST property.

---

## 6️⃣ Validate BST

Common mistake:
Only checking immediate children.

Correct approach:

Pass min/max constraints down recursion.

Example:

```python
def validate(node, min_val, max_val):
    if not node:
        return True
    if not (min_val < node.val < max_val):
        return False
    return validate(node.left, min_val, node.val) and \
           validate(node.right, node.val, max_val)
```

This checks entire subtree.

---

## 7️⃣ Kth Smallest Element

Important property:

Inorder traversal of BST gives sorted order.

So:
Traverse inorder.
Count nodes.
Return kth.

Optimized:
Stop traversal early.

Time:
O(h + k)

Strong candidates mention pruning.

---

## 8️⃣ Lowest Common Ancestor in BST

Use ordering:

If both nodes < root:
Go left.

If both > root:
Go right.

Else:
Current root is LCA.

Time:
O(h)

Much simpler than general tree LCA.

---

## 9️⃣ Convert Sorted Array to BST

Middle element becomes root.

Left half → left subtree.
Right half → right subtree.

Ensures balanced BST.

Time:
O(n)

Shows divide-and-conquer thinking.

---

# 🔹 Advanced Level Questions (5–10 Years)

---

## 🔟 Floor and Ceil in BST

Floor:
Largest value ≤ target.

Ceil:
Smallest value ≥ target.

Traverse while tracking candidate.

Used in range queries.

---

## 1️⃣1️⃣ Inorder Successor

If node has right subtree:
Successor = minimum of right subtree.

Else:
Move up until node is left child of parent.

Tests understanding of tree relationships.

---

## 1️⃣2️⃣ Why BST May Degrade to O(n)

If inserted in sorted order:

Tree becomes skewed.

Behaves like linked list.

Search becomes O(n).

Discuss need for self-balancing trees.

---

## 1️⃣3️⃣ Compare BST vs Hash Table

BST:
Ordered.
O(log n)
Supports range queries.

Hash:
Unordered.
O(1) average.
No range queries.

Choose based on use case.

Strong candidates compare trade-offs.

---

# 🔥 Scenario-Based Questions

---

## Scenario 1:
Search is slow in production.

Possible reason:
BST unbalanced.

Solution:
Use self-balancing BST (AVL, Red-Black).

---

## Scenario 2:
Validate BST failing for deep subtree.

Likely issue:
Only checking parent-child relation.

Must use min/max constraints.

---

## Scenario 3:
Need to retrieve sorted order frequently.

BST helpful.

Hash table not suitable.

---

## Scenario 4:
Memory constraint strict.

BST uses pointers (more memory than array).

Discuss trade-offs.

---

## Scenario 5:
Need fast insert and search with ordering.

BST or balanced BST appropriate.

---

# 🧠 How to Communicate Like a Strong Candidate

Weak candidate:

“I’ll search left or right.”

Strong candidate:

> “Since BST maintains strict ordering invariant, we can reduce search space at each comparison similarly to binary search, achieving logarithmic time in balanced cases.”

Structured. Confident.

---

# 🎯 Interview Cracking Strategy for BST

1. Confirm BST property.
2. Use ordering for elimination.
3. Mention height dependency.
4. Handle null cases.
5. Explain three deletion cases clearly.
6. Mention worst-case O(n).
7. Discuss balancing if needed.
8. Dry run example.

---

# ⚠️ Common Weak Candidate Mistakes

- Forgetting strict inequality
- Not handling duplicate values properly
- Incorrect deletion logic
- Not checking entire subtree in validation
- Assuming tree is balanced automatically
- Missing edge case: empty tree

BST requires precision.

---

# 🎯 Rapid-Fire Revision Points

- Left subtree < node < right subtree
- Search/insert/delete O(h)
- Balanced → O(log n)
- Skewed → O(n)
- Inorder traversal gives sorted order
- Deletion has 3 cases
- Use min/max for validation
- Compare BST vs hash for trade-offs

---

# 🏆 Final Interview Mindset

BST problems test:

- Logical ordering
- Recursive clarity
- Boundary control
- Case analysis skill
- Performance awareness

If you can:

- Explain ordering invariant confidently
- Handle deletion carefully
- Use inorder insight effectively
- Compare with hashing intelligently
- Discuss balancing clearly

You are strong in BST interviews.

BST mastery prepares you for:

- Self-balancing trees
- Ordered maps
- Tree-based data structures
- Advanced system design topics

---

# 🔁 Navigation

Previous:  
[15_binary_search_trees/theory.md](/dsa-complete-mastery/15_binary_search_trees/theory.md)

Next:  
[16_heaps/theory.md](/dsa-complete-mastery/16_heaps/theory.md)

