# 🎯 Trees — Interview Preparation Guide (Hierarchy Mastery)

> Tree problems test how well you think recursively.
>
> They test:
> - Structural understanding
> - Divide-and-conquer reasoning
> - Base case handling
> - Traversal mastery
> - Edge case awareness
>
> Most candidates fear trees.
> Strong candidates break them into subtrees.

Trees are not hard.
They require correct thinking style.

---

# 🔎 How Tree Questions Appear in Interviews

Rarely asked:
“Define a tree.”

More commonly:

- Inorder / preorder / postorder traversal
- Level order traversal
- Height of tree
- Check if tree is balanced
- Diameter of tree
- Lowest common ancestor (LCA)
- Validate binary tree
- Symmetric tree
- Path sum problems
- Maximum path sum
- Serialize and deserialize tree

If you see:
- Parent-child relationship
- Hierarchical data
- Recursive structure
- Subtree
- Path from root to leaf

Think: **Tree + Recursion**

---

# 🧠 How to Respond Before Coding

Instead of jumping into code, say:

> “Since each node can be treated as a root of its own subtree, I will solve this using recursion by defining the result for left and right subtree and combining them.”

That sentence shows maturity.

---

# 🔹 Basic Level Questions (0–2 Years)

---

## 1️⃣ What is a Tree?

Professional answer:

A tree is a hierarchical data structure consisting of nodes connected by edges, with one root node and no cycles.

Keep answer structured.

---

## 2️⃣ What is a Binary Tree?

A binary tree is a tree where each node has at most two children: left and right.

Important:
“At most” two children.

---

## 3️⃣ Explain Tree Traversals

Inorder:
Left → Root → Right

Preorder:
Root → Left → Right

Postorder:
Left → Right → Root

Interview tip:
Always draw small example when explaining.

---

## 4️⃣ What is Height of Tree?

Height = number of edges on longest path from root to leaf.

Implementation idea:

Height = 1 + max(height(left), height(right))

Recursive definition.

---

# 🔹 Intermediate Level Questions (2–5 Years)

---

## 5️⃣ Level Order Traversal

Use queue (BFS).

Steps:

1. Enqueue root.
2. While queue not empty:
   - Dequeue node.
   - Enqueue children.

Time: O(n)  
Space: O(n)

Before coding, say:

> “Since we need level-by-level traversal, BFS using queue is appropriate.”

---

## 6️⃣ Check if Tree is Balanced

Balanced means:

For every node,
|height(left) - height(right)| ≤ 1

Naive solution:
Compute height repeatedly → O(n²)

Optimized solution:
Return height while checking balance → O(n)

Strong candidates mention optimization.

---

## 7️⃣ Diameter of Tree

Diameter = longest path between two nodes.

Key insight:

Diameter at node = height(left) + height(right)

Global maximum required.

Time: O(n)

Tests subtree combination logic.

---

## 8️⃣ Lowest Common Ancestor (LCA)

If both nodes exist in different subtrees,
current node is LCA.

Recursive logic:

If root == p or root == q:
Return root.

Check left and right.

If both non-null:
Current is LCA.

This tests recursion reasoning.

---

## 9️⃣ Symmetric Tree

Check if left subtree is mirror of right subtree.

Recursive comparison:

left.left vs right.right  
left.right vs right.left

Tests structural comparison.

---

# 🔹 Advanced Level Questions (5–10 Years)

---

## 🔟 Maximum Path Sum

Path can start and end anywhere.

Key idea:

At each node:

max_gain = max(node.val, node.val + max(left, right))

Global maximum updated.

This is advanced tree DP.

---

## 1️⃣1️⃣ Serialize and Deserialize Tree

Convert tree to string and back.

Use:

- Preorder traversal
- Null markers

Shows system-level thinking.

---

## 1️⃣2️⃣ Construct Tree from Traversals

Given preorder + inorder:

Root = first element of preorder.

Split inorder into left/right.

Recursively build subtrees.

Tests understanding of traversal relationships.

---

## 1️⃣3️⃣ When Recursion May Fail

If tree is skewed:

Recursion depth = n.

May cause stack overflow.

Alternative:
Iterative solution.

Senior candidates mention this.

---

# 🔥 Scenario-Based Questions

---

## Scenario 1:
Tree problem running in O(n²).

Likely issue:
Recomputing height repeatedly.

Optimize by combining computations.

---

## Scenario 2:
Infinite recursion or crash.

Cause:
Missing base case.

Always check if node is None.

---

## Scenario 3:
Need to check if path exists from root to leaf with sum = target.

Use recursion.

Pass cumulative sum.

---

## Scenario 4:
Given extremely large tree.

Concern:
Recursion depth.

Use iterative approach.

---

## Scenario 5:
Need to print nodes level by level in zigzag order.

Use queue + reverse alternate levels.

Tests BFS modification.

---

# 🧠 How to Communicate Like a Strong Candidate

Weak candidate:

“I’ll solve using recursion.”

Strong candidate:

> “Since each node can be considered as a root of its own subtree, I’ll define the recursive relationship based on results from left and right subtree and combine them appropriately.”

Communication clarity matters.

---

# 🎯 Interview Cracking Strategy for Tree Problems

1. Identify if traversal or computation problem.
2. Decide DFS (recursion) or BFS (queue).
3. Define base case clearly.
4. Define recursive return value clearly.
5. Combine left and right results carefully.
6. Consider global variable if needed.
7. Mention time complexity O(n).
8. Mention space complexity (recursion stack O(h)).

Never code before defining recursion clearly.

---

# ⚠️ Common Weak Candidate Mistakes

- Forgetting base case
- Confusing height and depth
- Using global variables incorrectly
- Recomputing subtree values
- Not considering null nodes
- Ignoring skewed tree case
- Mixing inorder/preorder logic

Trees demand clarity.

---

# 🎯 Rapid-Fire Revision Points

- Trees are recursive structures
- Each node can be root of subtree
- DFS uses recursion or stack
- BFS uses queue
- Height calculation is common pattern
- Combine left/right results carefully
- Global variables often required
- Watch recursion depth
- Time complexity usually O(n)

---

# 🏆 Final Interview Mindset

Tree problems are about:

- Breaking problem into subtrees
- Defining recursive structure clearly
- Combining results logically
- Handling edge cases precisely

If you can:

- Visualize tree structure mentally
- Write clean recursive logic
- Explain base case confidently
- Optimize subtree computations
- Control recursion depth

You are strong in tree-based interviews.

Tree mastery unlocks:

- BST
- Heap
- Trie
- Graph
- Advanced dynamic programming

---

# 🔁 Navigation

Previous:  
[14_trees/theory.md](/dsa-complete-mastery/14_trees/theory.md)

Next:  
[15_binary_search_trees/theory.md](/dsa-complete-mastery/15_binary_search_trees/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Common Mistakes](./common_mistakes.md) &nbsp;|&nbsp; **Next:** [Binary Search Trees — Theory →](../15_binary_search_trees/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md)
