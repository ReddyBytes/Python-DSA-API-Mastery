<a id="top"></a>
# Binary Search Tree (BST) — The Organized Tree

> A normal tree is like a family.
> A Binary Search Tree is like a family with rules.
>
> Every node follows a strict ordering rule.
>
> That rule makes searching very fast.

BST is where trees become efficient.

## 📖 Table of Contents

1. [Real Life Story — Organized Library Shelves](#1-real-life-story)
2. [The BST Rule (Very Important)](#2-the-bst-rule)
3. [Building a BST: Insert Step by Step](#3-building-a-bst)
4. [Why BST Is Powerful](#4-why-bst-is-powerful)
5. [Searching in BST](#5-searching-in-bst)
6. [Insertion in BST](#6-insertion-in-bst)
7. [Deletion in BST (Most Important)](#7-deletion-in-bst)
8. [Height of BST](#8-height-of-bst)
9. [Balanced vs Unbalanced BST](#9-balanced-vs-unbalanced-bst)
10. [Inorder Traversal of BST](#10-inorder-traversal)
11. [Common BST Operations](#11-common-bst-operations)
12. [Validate BST](#12-validate-bst)
13. [BST vs Sorted Array vs Hash Map](#13-bst-vs-sorted-array-vs-hash-map)
14. [Real-World Usage](#14-real-world-usage)
15. [Mental Model](#15-mental-model)
16. [Final Understanding](#16-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
BST property · search · insert · delete (all three cases)

**Should Learn** — Important for real projects, comes up regularly:
inorder gives sorted order · successor and predecessor · BST validation

**Good to Know** — Useful in specific situations, not always tested:
height implications on performance · augmented BST

**Reference** — Know it exists, look up syntax when needed:
AVL trees · Red-Black trees · self-balancing tree overview

<a id="1-real-life-story"></a>
# 1. Real Life Story — Organized Library Shelves

Imagine you work at a very old-fashioned office. You have a massive filing cabinet with thousands of folders, each labeled with a number. Your job: find folder #47 as fast as possible.

**Option A: Unsorted cabinet.**
You open drawers randomly. Could be drawer 1, could be drawer 500. Pure luck.
Worst case: you check every single drawer. That's O(n). Painful.

**Option B: The Smart Filing Cabinet (BST).**
This cabinet has a rule baked into its very design:

```
        [ 50 ]          ← Start here
        /    \
    [ 30 ]  [ 70 ]      ← Left drawer = smaller, Right drawer = larger
    /   \    /   \
  [20] [40] [60] [80]
```

You're looking for 47.
- Open the top drawer: 50. Is 47 smaller? Yes. Go LEFT.
- Open left drawer: 30. Is 47 bigger? Yes. Go RIGHT.
- Open right drawer: 40. Is 47 bigger? Yes. Go RIGHT.
- Open right drawer: found 47 (or it's not there).

Every single decision **eliminates half the remaining cabinet.**
That's O(log n). For 1,000,000 folders, you need at most ~20 checks.

> [↑ Back to Top](#top)

<a id="2-the-bst-rule"></a>
# 2. The BST Rule (Very Important)

> 📝 **Practice:** [Q1 · BST property](./practice.md#q1----bst-property-left--root--right) · [Q2 · Subtree-wide rule](./practice.md#q2----bst-property-is-subtree-wide-not-just-direct-children)

For every node:

All values in left subtree < node value
All values in right subtree > node value

That's it. This simple rule creates power.

The rule isn't just about a node and its direct children. It applies to the **entire subtree**:

```
For ANY node X:
  - ALL values in the LEFT subtree  <  X
  - ALL values in the RIGHT subtree >  X
```

## Visual: Valid vs Invalid BST

### VALID BST

```
           [ 8 ]
          /     \
       [ 3 ]   [ 10 ]
       /   \       \
    [ 1 ] [ 6 ]   [ 14 ]
          /   \    /
        [ 4 ][ 7 ][ 13 ]
```

Check node 8: left subtree has {1,3,4,6,7} — all less than 8. Right has {10,13,14} — all greater. VALID.
Check node 3: left has {1} < 3. Right has {4,6,7} > 3. VALID.
Every node passes the test.

### INVALID BST — looks fine at first glance!

```
           [ 8 ]
          /     \
       [ 3 ]   [ 10 ]
       /   \
    [ 1 ] [ 12 ]    ← PROBLEM: 12 is in the LEFT subtree of 8!
```

Node 3's right child is 12. Locally, 12 > 3. Looks okay.
But 12 > 8 too — it's in the LEFT subtree of 8. That BREAKS the BST property.

The rule isn't just "left child < parent". It's "ALL descendants on the left < ancestor."

**Common mistake — checking only direct children:** Checking only `node.val > node.left.val` misses the case where a value in the right subtree is too small, or a value in the left subtree is too large relative to an ancestor. Always pass `(min_val, max_val)` bounds down the recursion.

> [↑ Back to Top](#top)

<a id="3-building-a-bst"></a>
# 3. Building a BST: Insert Step by Step

Insert numbers: **5, 3, 7, 1, 4, 6, 8**

## Visual: Step-by-Step Insertion

### Step 1: Insert 5 (root)
```
[ 5 ]
```

### Step 2: Insert 3
3 < 5, go left. Left is empty. Place here.
```
  [ 5 ]
  /
[ 3 ]
```

### Step 3: Insert 7
7 > 5, go right. Right is empty. Place here.
```
    [ 5 ]
    /   \
  [ 3 ] [ 7 ]
```

### Step 4: Insert 1
1 < 5, go left → 3. 1 < 3, go left. Empty. Place here.
```
      [ 5 ]
      /   \
    [ 3 ] [ 7 ]
    /
  [ 1 ]
```

### Step 5: Insert 4
4 < 5, go left → 3. 4 > 3, go right. Empty. Place here.
```
      [ 5 ]
      /   \
    [ 3 ] [ 7 ]
    /   \
  [ 1 ] [ 4 ]
```

### Step 6: Insert 6
6 > 5, go right → 7. 6 < 7, go left. Empty. Place here.
```
        [ 5 ]
        /   \
      [ 3 ] [ 7 ]
      /   \  /
    [1]  [4][6]
```

### Step 7: Insert 8
8 > 5, go right → 7. 8 > 7, go right. Empty. Place here.
```
          [ 5 ]
          /   \
        [ 3 ] [ 7 ]
        /   \  /  \
      [1]  [4][6] [8]
```

Our final tree. Notice it's nicely balanced because we inserted in a smart order.

**Common mistake — insert returns None or discards return value:** When writing recursive BST insert, the function must return the (possibly new) root at every recursive call. Local rebinding does not propagate back — the original tree is unchanged. Always `return root` at the end, and always assign `root.left = insert(root.left, val)`.

> [↑ Back to Top](#top)

<a id="4-why-bst-is-powerful"></a>
# 4. Why BST Is Powerful

Because it combines:

- Tree structure
- Binary search logic

Searching in BST:

Compare with root.
If smaller → go left.
If larger → go right.

Time: O(h)

If balanced: h ≈ log n

Fast.

> [↑ Back to Top](#top)

<a id="5-searching-in-bst"></a>
# 5. Searching in BST

> 📝 **Practice:** [Q3 · BST search trace](./practice.md#q3----search-in-a-bst-trace-the-path)

Using the tree we just built, let's find 4.

## Visual: Search Trace

```
          [ 5 ]          ← Start: Is 4 == 5? No. 4 < 5, go LEFT.
          /   \
        [ 3 ] [ 7 ]      ← Is 4 == 3? No. 4 > 3, go RIGHT.
        /   \  /  \
      [1]  [4][6] [8]    ← Is 4 == 4? YES! Found it.
```

**Decision log:**
```
Node 5:   4 < 5  →  go LEFT
Node 3:   4 > 3  →  go RIGHT
Node 4:   4 == 4 →  FOUND!
```

Only 3 comparisons for a 7-node tree. If the tree had 1 million nodes (balanced), you'd need at most ~20 comparisons. The binary elimination is powerful.

You didn't check every node. You eliminated half at each step. Binary search inside a tree.

> [↑ Back to Top](#top)

<a id="6-insertion-in-bst"></a>
# 6. Insertion in BST

> 📝 **Practice:** [Q4 · BST insert](./practice.md#q4----insert-into-a-bst-step-by-step) · [Q5 · Find min/max](./practice.md#q5----find-minimum-and-maximum)

Insert follows same rule.

Example: Insert 1 into a tree rooted at 5.

1 < 5 → go left.
1 < 3 → go left.
1 < 2 → go left.

Place as left child of 2.

Tree grows according to rule.

Time: O(h)

```python
class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

class BST:
    def insert(self, root, val):
        if not root:
            return Node(val)
        if val < root.val:
            root.left = self.insert(root.left, val)
        else:
            root.right = self.insert(root.right, val)
        return root
```

> [↑ Back to Top](#top)

<a id="7-deletion-in-bst"></a>
# 7. Deletion in BST (Most Important)

> 📝 **Practice:** [Q9 · Delete leaf](./practice.md#q9----delete-a-leaf-node) · [Q10 · Delete one child](./practice.md#q10----delete-a-node-with-one-child) · [Q11 · Delete two children](./practice.md#q11----delete-a-node-with-two-children)

Deletion has 3 cases, from easy to hard.

## Case 1: Leaf Node (no children)

Simply remove. No restructuring needed.

## Visual: Delete a Leaf

Delete **1** from our tree. It has no children. Just snip it off.

```
Before:                     After:
      [ 5 ]                       [ 5 ]
      /   \                       /   \
    [ 3 ] [ 7 ]                 [ 3 ] [ 7 ]
    /   \  /  \                     \  /  \
  [1]  [4][6] [8]                  [4][6] [8]
```

## Case 2: One Child

Replace node with its child. Like removing a link from a chain — reconnect the two neighbors.

## Visual: Delete a Node with One Child

Delete **7** from the tree (assume it only has child 8).

```
Before:                     After:
      [ 5 ]                       [ 5 ]
      /   \                       /   \
    [ 3 ] [ 7 ]                 [ 3 ] [ 8 ]
        \     \                     \
        [4]   [8]                   [4]
```

Just bypass 7. Connect its parent (5) directly to its child (8).

## Case 3: Two Children

Replace with:

- Inorder successor (smallest in right subtree)
OR
- Inorder predecessor (largest in left subtree)

Then delete that successor node.

This preserves BST rule.

## Visual: Delete a Node with Two Children

Delete **3** from our full tree. It has children 1 and 4.

```
          [ 5 ]
          /   \
        [ 3 ] [ 7 ]      ← Delete this one
        /   \  /  \
      [1]  [4][6] [8]
```

We can't just remove 3 — we'd break the structure. We need a replacement.

**Strategy: Find the inorder successor.**
The inorder successor is the smallest value in the RIGHT subtree.
For node 3, the right subtree is {4}. Smallest = 4.

**Steps:**
1. Find inorder successor of 3 → it's 4 (leftmost node in right subtree)
2. Copy 4's value into node 3's position
3. Delete 4 from its original position (which is a leaf — Case 1!)

```
Step 1 & 2: Replace 3 with 4
          [ 5 ]
          /   \
        [ 4 ] [ 7 ]      ← 3 replaced by 4
        /      /  \
      [1]    [6] [8]

Step 3: Delete 4 from original position (already done above)
```

**Why inorder successor?** Because it's the smallest value that's still larger than 3. It perfectly fills 3's role: larger than everything in 3's left subtree (1), smaller than 5.

**Common mistake — forgetting to remove the successor:** When deleting a node with two children, copying the successor's value without deleting the successor from the right subtree leaves it duplicated. After copying, always call `root.right = delete(root.right, successor.val)` to remove the original.

Deletion tests understanding deeply.

> [↑ Back to Top](#top)

<a id="8-height-of-bst"></a>
# 8. Height of BST

> 📝 **Practice:** [Q8 · Worst-case O(n)](./practice.md#q8----worst-case-on-when-does-a-bst-degrade)

Performance depends on height.

Balanced BST:

```
Height ≈ log n
```

Worst case (skewed):

```
Height ≈ n
```

Example skewed tree — insert 1,2,3,4,5 in order:

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

Behaves like linked list. Search becomes O(n).

```
Balanced BST (7 nodes):   Height = 3   → O(log 7) ≈ 3 comparisons
Degenerate BST (7 nodes): Height = 7   → O(7) comparisons in worst case
```

> [↑ Back to Top](#top)

<a id="9-balanced-vs-unbalanced-bst"></a>
# 9. Balanced vs Unbalanced BST

> 📝 **Practice:** [Q22 · AVL vs Red-Black](./practice.md#q22----self-balancing-trees-avl-vs-red-black-conceptual)

Balanced: Fast operations.

Unbalanced: Slow operations.

That's why balanced BSTs exist:

- **AVL Trees**: Automatically rotate nodes to keep the tree balanced after every insert/delete.
- **Red-Black Trees**: A more relaxed balancing scheme (used in Java's `TreeMap`, C++'s `std::map`).

They maintain height ≈ log n.

The concept: after an insert or delete, check if the tree is "too lopsided" and rotate nodes to fix it.
Python's `sortedcontainers.SortedList` and Java's `TreeMap` give you BST behavior without worrying about this.

**Common mistake — assuming BST is always O(log n):** BST is only O(log n) for balanced trees. Inserting values in sorted order produces a skewed tree with O(n) search. Always account for worst-case height, or use a self-balancing variant in production.

> [↑ Back to Top](#top)

<a id="10-inorder-traversal"></a>
# 10. Inorder Traversal of BST

> 📝 **Practice:** [Q6 · Inorder sorted output](./practice.md#q6----inorder-traversal-gives-sorted-output) · [Q15 · BST to sorted array](./practice.md#q15----convert-bst-to-sorted-array)

Important property:

Inorder traversal (Left → Node → Right) of BST gives sorted order automatically.

## Visual: Inorder Traversal Trace

```
          [ 5 ]
          /   \
        [ 3 ] [ 7 ]
        /   \  /  \
      [1]  [4][6] [8]
```

```
Go left as far as possible → reach [1]
Visit [1]    → output: 1
Back to [3], visit [3]    → output: 3
Go right to [4], visit [4] → output: 4
Back to [5], visit [5]    → output: 5
Go left to [6], visit [6] → output: 6
Back to [7], visit [7]    → output: 7
Go right to [8], visit [8] → output: 8
```

**Result: [1, 3, 4, 5, 6, 7, 8]**

Sorted! For free! This is why BSTs are great for problems that need ordered data.

```python
class BST:
    def inorder(self, root):
        if not root:
            return []
        return self.inorder(root.left) + [root.val] + self.inorder(root.right)
        # Returns sorted list!
```

> [↑ Back to Top](#top)

<a id="11-common-bst-operations"></a>
# 11. Common BST Operations

- Search
- Insert
- Delete
- Find minimum
- Find maximum
- Find successor
- Find predecessor
- Validate BST

All rely on ordering rule.

> [↑ Back to Top](#top)

<a id="12-validate-bst"></a>
# 12. Validate BST

> 📝 **Practice:** [Q12 · Bounds approach](./practice.md#q12----validate-bst-using-minmax-bounds) · [Q24 · Inorder vs bounds](./practice.md#q24----two-approaches-to-bst-validation)

Check:

Left subtree max < node value
Right subtree min > node value

Can be done using:

- Inorder traversal
- Min/max range recursion

The min/max bounds approach passes the valid range down the recursion:

```python
import math

def is_valid_bst(root, min_val=float('-inf'), max_val=float('inf')):
    if root is None:
        return True
    if not (min_val < root.val < max_val):
        return False
    return (is_valid_bst(root.left,  min_val, root.val) and
            is_valid_bst(root.right, root.val, max_val))
```

**Common mistake — checking only parent-child relationship:** `is_valid_bst_wrong` that checks only `node.val > node.left.val` will approve this invalid tree: root=5, right child=4, right.left=3, right.right=6 — because 4's children look locally valid, but 4 itself violates the constraint that everything in 5's right subtree must exceed 5. Always use the bounds approach.

> 📝 **Practice:** [Q37 · bst-properties](../dsa_practice_questions_100.md#q37--critical--bst-properties)

Important interview question.

> [↑ Back to Top](#top)

<a id="13-bst-vs-sorted-array-vs-hash-map"></a>
# 13. BST vs Sorted Array vs Hash Map

> 📝 **Practice:** [Q7 · BST vs hash map tradeoffs](./practice.md#q7----bst-vs-sorted-array-vs-hash-map)

Which data structure should you use? Here's the honest comparison.

```
Operation          | Sorted Array  | Hash Map      | BST (balanced)
-------------------|---------------|---------------|---------------
Search             | O(log n)      | O(1) avg      | O(log n)
Insert             | O(n)          | O(1) avg      | O(log n)
Delete             | O(n)          | O(1) avg      | O(log n)
Find min/max       | O(1)          | O(n)          | O(log n)
Range query [a,b]  | O(log n + k)  | O(n)          | O(log n + k)
In-order output    | O(n) *free*   | O(n log n)    | O(n) *free*
```

- **Sorted Array:** Search is fast, but inserting a new element means shifting everything. Painful for frequent updates.
- **Hash Map:** Blazing fast for exact lookups, but has no concept of "order". Can't answer "give me all values between 10 and 20."
- **BST:** The balanced compromise. Fast search AND fast insert AND supports ordering AND range queries.

**When to choose BST:**
- You need both fast search AND fast insert
- You need to find elements in a range (e.g., "all employees with salary between 50k and 80k")
- You need sorted output frequently

**Common mistake — range query visits entire tree:** Doing a full inorder traversal then filtering is O(n). BST property lets you prune: if a node's value is less than `low`, its entire left subtree is also below range — skip it. Skip left if `node.val <= low`; skip right if `node.val >= high`. This gives O(k + h) where k is the number of results.

**Common mistake — using general O(n) LCA on a BST:** Lowest Common Ancestor on a BST can be solved in O(h) by exploiting BST ordering: if both target values are less than the current node, go left; if both are greater, go right; otherwise the current node is the LCA. Using the general tree algorithm (which visits every node) signals you missed the BST structure.

> [↑ Back to Top](#top)

<a id="14-real-world-usage"></a>
# 14. Real-World Usage

BST used in:

- Database indexing
- Symbol tables
- Ordered maps
- File systems
- Scheduling systems
- C++ STL set/map (Red-Black Tree)

Ordered structures rely on BST logic.

> [↑ Back to Top](#top)

<a id="15-mental-model"></a>
# 15. Mental Model

Think of BST as a decision tree.

At each node you decide: Left or right?

You eliminate half possibilities.

BST is the tree version of binary search.

A BST is a filing cabinet where every drawer tells you "go left if smaller, go right if bigger," so you eliminate half the remaining work at every single step — as long as you keep it balanced.

> [↑ Back to Top](#top)

<a id="16-final-understanding"></a>
# 16. Final Understanding

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

> 📝 **Practice:** [Q38 · bst-search-insert](../dsa_practice_questions_100.md#q38--normal--bst-search-insert)

> [↑ Back to Top](#top)

## 📂 Navigation

**[🏠 Back to README](../README.md)**

**Prev:** [← Trees — Interview Q&A](../14_trees/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
