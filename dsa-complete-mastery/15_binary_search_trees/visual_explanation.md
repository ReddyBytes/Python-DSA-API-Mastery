# Binary Search Trees — The Organized Filing Cabinet

---

## The Filing Cabinet That Thinks

Imagine you work at a very old-fashioned office. You have a massive filing cabinet with thousands of folders,
each labeled with a number. Your job: find folder #47 as fast as possible.

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

---

## The Golden Rule of BSTs

Here's the rule that makes everything work. It's not just about a node and its direct children.
It applies to the **entire subtree**:

```
For ANY node X:
  - ALL values in the LEFT subtree  <  X
  - ALL values in the RIGHT subtree >  X
```

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

---

## Building a BST: Insert Step by Step

Let's insert these numbers in order: **5, 3, 7, 1, 4, 6, 8**

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

Our final tree! Notice it's nicely balanced. That's because we inserted in a smart order.

---

## Searching: Find the Number 4

Using the tree we just built, let's find 4.

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

Only 3 comparisons for a 7-node tree. If the tree had 1 million nodes (balanced),
you'd need at most ~20 comparisons. The binary elimination is powerful.

---

## Inorder Traversal = Free Sorted Output

Here's a beautiful property of BSTs: if you do an **inorder traversal** (Left → Node → Right),
you get all the values in sorted order automatically.

```
          [ 5 ]
          /   \
        [ 3 ] [ 7 ]
        /   \  /  \
      [1]  [4][6] [8]
```

Inorder traversal trace:
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

---

## Deletion: The Tricky Part

Deletion has three cases, from easy to hard.

### Case 1: Delete a Leaf Node (no children)

Delete **1** from our tree. It has no children. Just snip it off.

```
Before:                     After:
      [ 5 ]                       [ 5 ]
      /   \                       /   \
    [ 3 ] [ 7 ]                 [ 3 ] [ 7 ]
    /   \  /  \                     \  /  \
  [1]  [4][6] [8]                  [4][6] [8]
```

Easy. No restructuring needed.

### Case 2: Delete a Node with One Child

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
Like removing a link from a chain — reconnect the two neighbors.

### Case 3: Delete a Node with Two Children (the interesting one)

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

**Why inorder successor?** Because it's the smallest value that's still larger than 3.
It perfectly fills 3's role: larger than everything in 3's left subtree (1), smaller than 5.

---

## BST vs Sorted Array vs Hash Map

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

---

## The Danger of Imbalance

Here's the dark secret. Remember we said BSTs are O(log n)? That's only true for **balanced** trees.

What happens if you insert values in sorted order: **1, 2, 3, 4, 5**?

```
Insert 1: [1]
Insert 2: [1] → [2]         (2 > 1, go right)
Insert 3: [1] → [2] → [3]   (3 > 2, go right again)
Insert 4: ...
Insert 5: ...

Final "tree":
  [1]
    \
    [2]
      \
      [3]
        \
        [4]
          \
          [5]
```

That's just a linked list wearing a tree costume. O(n) search. O(n) insert. All the downsides, none of the benefits.

```
Balanced BST (7 nodes):   Height = 3   → O(log 7) ≈ 3 comparisons
Degenerate BST (7 nodes): Height = 7   → O(7) comparisons in worst case
```

**What to do about it:**
This is why self-balancing trees exist:
- **AVL Trees**: Automatically rotate nodes to keep the tree balanced after every insert/delete
- **Red-Black Trees**: A more relaxed balancing scheme (used in Java's TreeMap, C++'s std::map)

The concept: after an insert or delete, check if the tree is "too lopsided" and rotate nodes to fix it.
Python's `sortedcontainers.SortedList` and Java's `TreeMap` give you BST behavior without worrying about this.

---

## Quick Code Reference

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

    def search(self, root, val):
        if not root or root.val == val:
            return root
        if val < root.val:
            return self.search(root.left, val)
        return self.search(root.right, val)

    def inorder(self, root):
        if not root:
            return []
        return self.inorder(root.left) + [root.val] + self.inorder(root.right)
        # Returns sorted list!
```

---

## The One-Sentence Summary

A BST is a filing cabinet where every drawer tells you "go left if smaller, go right if bigger,"
so you eliminate half the remaining work at every single step — as long as you keep it balanced.
