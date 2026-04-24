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

**Q1: What is a Binary Search Tree?**

<details>
<summary>💡 Show Answer</summary>

Professional answer:

A Binary Search Tree is a binary tree where for every node, all values in its left subtree are smaller and all values in its right subtree are larger.

Mention “for every node.”

</details>

<br>

**Q2: What is Time Complexity of Search?**

<details>
<summary>💡 Show Answer</summary>

Search time = O(h)

If balanced:
O(log n)

If skewed:
O(n)

Always mention both cases.

</details>

<br>

**Q3: How to Insert in BST?**

<details>
<summary>💡 Show Answer</summary>

Logic:

If value < node:
Go left.

If value > node:
Go right.

Insert at null position.

Time:
O(h)

Explain traversal clearly.

</details>

<br>

**Q4: How to Find Minimum and Maximum?**

<details>
<summary>💡 Show Answer</summary>

Minimum:
Keep going left.

Maximum:
Keep going right.

Because left subtree always smaller.

</details>


# 🔹 Intermediate Level Questions (2–5 Years)

---

**Q5: Delete Node in BST**

<details>
<summary>💡 Show Answer</summary>

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

</details>

<br>

**Q6: Validate BST**

<details>
<summary>💡 Show Answer</summary>

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

</details>

<br>

**Q7: Kth Smallest Element**

<details>
<summary>💡 Show Answer</summary>

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

</details>

<br>

**Q8: Lowest Common Ancestor in BST**

<details>
<summary>💡 Show Answer</summary>

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

</details>

<br>

**Q9: Convert Sorted Array to BST**

<details>
<summary>💡 Show Answer</summary>

Middle element becomes root.

Left half → left subtree.
Right half → right subtree.

Ensures balanced BST.

Time:
O(n)

Shows divide-and-conquer thinking.

</details>


# 🔹 Advanced Level Questions (5–10 Years)

---

**Q10: Floor and Ceil in BST**

<details>
<summary>💡 Show Answer</summary>

Floor:
Largest value ≤ target.

Ceil:
Smallest value ≥ target.

Traverse while tracking candidate.

Used in range queries.

</details>

<br>

**Q11: Inorder Successor**

<details>
<summary>💡 Show Answer</summary>

If node has right subtree:
Successor = minimum of right subtree.

Else:
Move up until node is left child of parent.

Tests understanding of tree relationships.

</details>

<br>

**Q12: Why BST May Degrade to O(n)**

<details>
<summary>💡 Show Answer</summary>

If inserted in sorted order:

Tree becomes skewed.

Behaves like linked list.

Search becomes O(n).

Discuss need for self-balancing trees.

</details>

<br>

**Q13: Compare BST vs Hash Table**

<details>
<summary>💡 Show Answer</summary>

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

</details>


# 🔥 Scenario-Based Questions

---

## Scenario 1:

Search is slow in production.

<details>
<summary>💡 Show Answer</summary>

Possible reason:
BST unbalanced.

Solution:
Use self-balancing BST (AVL, Red-Black).

</details>
---

## Scenario 2:

Validate BST failing for deep subtree.

<details>
<summary>💡 Show Answer</summary>

Likely issue:
Only checking parent-child relation.

Must use min/max constraints.

</details>
---

## Scenario 3:

Need to retrieve sorted order frequently.

<details>
<summary>💡 Show Answer</summary>

BST helpful.

Hash table not suitable.

</details>
---

## Scenario 4:

Memory constraint strict.

<details>
<summary>💡 Show Answer</summary>

BST uses pointers (more memory than array).

Discuss trade-offs.

</details>
---

## Scenario 5:

Need fast insert and search with ordering.

<details>
<summary>💡 Show Answer</summary>

BST or balanced BST appropriate.

</details>
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

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Common Mistakes](./common_mistakes.md) &nbsp;|&nbsp; **Next:** [Heaps — Theory →](../16_heaps/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md)
