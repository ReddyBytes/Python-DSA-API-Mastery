<a id="top"></a>
# 📘 15 – Binary Search Trees (BST) in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is a BST?](#1-what-is-a-bst)
  - [The BST Rule](#bst-rule)
  - [Visual: VALID vs INVALID BST](#visual-valid-invalid)
- [2. Building and Inserting](#2-building-inserting)
  - [Visual: Step-by-Step Insertion](#visual-insertion)
- [3. Searching in BST](#3-searching)
  - [Visual: Search Trace](#visual-search)
- [4. Deletion in BST](#4-deletion)
  - [Case 1: Leaf Node](#delete-leaf)
  - [Case 2: One Child](#delete-one-child)
  - [Case 3: Two Children](#delete-two-children)
- [5. Height and Balance](#5-height-balance)
- [6. Inorder Traversal — Sorted Output](#6-inorder)
  - [Visual: Inorder Trace](#visual-inorder)
- [7. Common BST Operations](#7-operations)
- [8. Validate BST](#8-validate)
- [9. BST vs Sorted Array vs Hash Map](#9-comparison)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
BST property · search · insert · delete (all three cases)

**Should Learn** — Important for real projects, comes up regularly:
inorder gives sorted order · successor and predecessor · BST validation

**Good to Know** — Useful in specific situations, not always tested:
height implications on performance · augmented BST

**Reference** — Know it exists, look up syntax when needed:
AVL trees · Red-Black trees · self-balancing tree overview

Vera is an archivist. She manages a massive filing cabinet with thousands of folders, each labeled with a number. Her cabinet has a strict rule built into its very design: every drawer tells you "go left if your number is smaller, go right if it is bigger." This single rule lets Vera find any folder in at most 20 steps — even among a million folders. That ordering rule is what makes a Binary Search Tree special.

<a id="1-what-is-a-bst"></a>
# 1. What Is a BST?

Vera's filing cabinet is not just any tree — it is a tree with a rule. Every drawer (node) guarantees: everything on the left is smaller, everything on the right is larger. This single constraint turns a regular tree into a search machine.

```
Vera's Filing Cabinet:

        [ 50 ]          ← Start here
        /    \
    [ 30 ]  [ 70 ]      ← Left = smaller, Right = larger
    /   \    /   \
  [20] [40] [60] [80]
```

Looking for folder 47:
- Open top drawer: 50. Is 47 smaller? Yes. Go LEFT.
- Open left drawer: 30. Is 47 bigger? Yes. Go RIGHT.
- Open right drawer: 40. Is 47 bigger? Yes. Go RIGHT.
- Found 47 (or it is not there).

Every decision eliminates half the remaining cabinet. That is O(log n).

<a id="bst-rule"></a>
## The BST Rule

For every node X:
- ALL values in the LEFT subtree < X
- ALL values in the RIGHT subtree > X

The rule is not just about direct children. It applies to the **entire subtree**.

> 📝 **Practice:** [Q1 · BST property](./practice.md#q1----bst-property-left--root--right) · [Q2 · Subtree-wide rule](./practice.md#q2----bst-property-is-subtree-wide-not-just-direct-children)

<a id="visual-valid-invalid"></a>
## Visual: VALID vs INVALID BST

```
VALID BST:

           [ 8 ]
          /     \
       [ 3 ]   [ 10 ]
       /   \       \
    [ 1 ] [ 6 ]   [ 14 ]
          /   \    /
        [ 4 ][ 7 ][ 13 ]

Check node 8: left subtree {1,3,4,6,7} — all < 8. Right {10,13,14} — all > 8. ✓


INVALID BST — looks fine at first glance!

           [ 8 ]
          /     \
       [ 3 ]   [ 10 ]
       /   \
    [ 1 ] [ 12 ]    ← PROBLEM: 12 is in LEFT subtree of 8!

Node 3's right child is 12. Locally 12 > 3 looks OK.
But 12 > 8 — it breaks the rule that ALL left descendants < ancestor.
```

**Common mistake — checking only direct children:** Checking `node.val > node.left.val` misses violations relative to ancestors. Always pass `(min_val, max_val)` bounds down the recursion.

> [↑ Back to Top](#top)

<a id="2-building-inserting"></a>
# 2. Building and Inserting

Vera receives folders one at a time and files them following the BST rule. Each new folder travels down from the root until it finds an empty slot. The path it takes is determined entirely by comparisons.

<a id="visual-insertion"></a>
## Visual: Step-by-Step Insertion

Insert numbers: **5, 3, 7, 1, 4, 6, 8**

```
Step 1: Insert 5 (becomes root)
[ 5 ]

Step 2: Insert 3 (3 < 5, go left)
  [ 5 ]
  /
[ 3 ]

Step 3: Insert 7 (7 > 5, go right)
    [ 5 ]
    /   \
  [ 3 ] [ 7 ]

Step 4: Insert 1 (1 < 5, left → 3. 1 < 3, left)
      [ 5 ]
      /   \
    [ 3 ] [ 7 ]
    /
  [ 1 ]

Step 5: Insert 4 (4 < 5, left → 3. 4 > 3, right)
      [ 5 ]
      /   \
    [ 3 ] [ 7 ]
    /   \
  [ 1 ] [ 4 ]

Step 6: Insert 6 (6 > 5, right → 7. 6 < 7, left)
        [ 5 ]
        /   \
      [ 3 ] [ 7 ]
      /   \  /
    [1]  [4][6]

Step 7: Insert 8 (8 > 5, right → 7. 8 > 7, right)
          [ 5 ]
          /   \
        [ 3 ] [ 7 ]
        /   \  /  \
      [1]  [4][6] [8]
```

```python
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def insert(root, val):
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    return root
```

Time: O(h) where h = height of tree.

**Common mistake — insert returns None or discards return value:** The function must return the (possibly new) root at every recursive call. Always assign `root.left = insert(root.left, val)`.

> 📝 **Practice:** [Q4 · BST insert](./practice.md#q4----insert-into-a-bst-step-by-step) · [Q5 · Find min/max](./practice.md#q5----find-minimum-and-maximum)

> [↑ Back to Top](#top)

<a id="3-searching"></a>
# 3. Searching in BST

Vera needs to find folder 4 in her cabinet. She starts at the root and makes left/right decisions at each node — exactly like binary search, but on a tree instead of an array.

<a id="visual-search"></a>
## Visual: Search Trace

```
          [ 5 ]          ← Is 4 == 5? No. 4 < 5, go LEFT.
          /   \
        [ 3 ] [ 7 ]      ← Is 4 == 3? No. 4 > 3, go RIGHT.
        /   \  /  \
      [1]  [4][6] [8]    ← Is 4 == 4? YES! Found it.

Decision log:
  Node 5:   4 < 5  →  go LEFT
  Node 3:   4 > 3  →  go RIGHT
  Node 4:   4 == 4 →  FOUND!
```

Only 3 comparisons for a 7-node tree. For 1 million balanced nodes: ~20 comparisons.

> 📝 **Practice:** [Q3 · BST search trace](./practice.md#q3----search-in-a-bst-trace-the-path)

> [↑ Back to Top](#top)

<a id="4-deletion"></a>
# 4. Deletion in BST

Vera must remove a folder from the cabinet. This is the hardest BST operation — there are three cases depending on how many children the target node has. Each case requires a different strategy to maintain the BST rule.

> 📝 **Practice:** [Q9 · Delete leaf](./practice.md#q9----delete-a-leaf-node) · [Q10 · Delete one child](./practice.md#q10----delete-a-node-with-one-child) · [Q11 · Delete two children](./practice.md#q11----delete-a-node-with-two-children)

<a id="delete-leaf"></a>
## Case 1: Leaf Node (no children)

Simply remove. No restructuring needed.

```
Delete 1 (leaf):

Before:                     After:
      [ 5 ]                       [ 5 ]
      /   \                       /   \
    [ 3 ] [ 7 ]                 [ 3 ] [ 7 ]
    /   \  /  \                     \  /  \
  [1]  [4][6] [8]                  [4][6] [8]
```

<a id="delete-one-child"></a>
## Case 2: One Child

Replace node with its child. Like removing a link from a chain — reconnect neighbors.

```
Delete 7 (one child: 8):

Before:                     After:
      [ 5 ]                       [ 5 ]
      /   \                       /   \
    [ 3 ] [ 7 ]                 [ 3 ] [ 8 ]
        \     \                     \
        [4]   [8]                   [4]
```

<a id="delete-two-children"></a>
## Case 3: Two Children

The hardest case. Replace with the **inorder successor** (smallest in right subtree), then delete that successor.

```
Delete 3 (two children: 1 and 4):

          [ 5 ]
          /   \
        [ 3 ] [ 7 ]      ← Delete this
        /   \  /  \
      [1]  [4][6] [8]

Step 1: Find inorder successor of 3 → it's 4 (leftmost in right subtree)
Step 2: Copy 4's value into node 3's position
Step 3: Delete 4 from original position (leaf — Case 1!)

Result:
          [ 5 ]
          /   \
        [ 4 ] [ 7 ]
        /      /  \
      [1]    [6] [8]
```

**Why inorder successor?** It is the smallest value still larger than 3 — perfectly fills the role.

**Common mistake — forgetting to remove the successor:** Copying the successor's value without deleting it from the right subtree leaves a duplicate. Always call `root.right = delete(root.right, successor.val)`.

> [↑ Back to Top](#top)

<a id="5-height-balance"></a>
# 5. Height and Balance

Vera discovers that her cabinet's performance depends entirely on its shape. A balanced cabinet (equal depth on both sides) gives O(log n) search. A skewed cabinet (all folders on one side) degrades to O(n) — essentially a linked list.

```
Balanced BST (7 nodes):   Height = 3   → O(log 7) ≈ 3 comparisons

          [ 5 ]
          /   \
        [ 3 ] [ 7 ]
        /   \  /  \
      [1]  [4][6] [8]


Skewed BST (insert 1,2,3,4,5 in order):   Height = 5 → O(5)

    1
     \
      2
       \
        3
         \
          4
           \
            5

Behaves like a linked list!
```

Self-balancing trees fix this:
- **AVL Trees:** rotate after every insert/delete to maintain balance
- **Red-Black Trees:** relaxed balancing (Java `TreeMap`, C++ `std::map`)

**Common mistake — assuming BST is always O(log n):** Only balanced trees are O(log n). Inserting sorted values produces O(n) search. Use self-balancing variants in production.

> 📝 **Practice:** [Q8 · Worst-case O(n)](./practice.md#q8----worst-case-on-when-does-a-bst-degrade) · [Q22 · AVL vs Red-Black](./practice.md#q22----self-balancing-trees-avl-vs-red-black-conceptual)

> [↑ Back to Top](#top)

<a id="6-inorder"></a>
# 6. Inorder Traversal — Sorted Output

Vera discovers a magical property: if she visits her cabinet in Left → Node → Right order (inorder traversal), the folders come out perfectly sorted. No sorting algorithm needed — the BST rule guarantees it.

<a id="visual-inorder"></a>
## Visual: Inorder Trace

```
          [ 5 ]
          /   \
        [ 3 ] [ 7 ]
        /   \  /  \
      [1]  [4][6] [8]

Go left as far as possible → reach [1]
Visit [1]    → output: 1
Back to [3], visit [3]    → output: 3
Go right to [4], visit [4] → output: 4
Back to [5], visit [5]    → output: 5
Go left to [6], visit [6] → output: 6
Back to [7], visit [7]    → output: 7
Go right to [8], visit [8] → output: 8

Result: [1, 3, 4, 5, 6, 7, 8] — sorted!
```

```python
def inorder(root):
    if not root:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)
```

> 📝 **Practice:** [Q6 · Inorder sorted output](./practice.md#q6----inorder-traversal-gives-sorted-output) · [Q15 · BST to sorted array](./practice.md#q15----convert-bst-to-sorted-array)

> [↑ Back to Top](#top)

<a id="7-operations"></a>
# 7. Common BST Operations

Vera's complete toolkit — every operation she needs for her filing cabinet:

- **Search:** O(h) — follow left/right based on comparisons
- **Insert:** O(h) — find empty slot following BST rule
- **Delete:** O(h) — three cases based on children count
- **Find minimum:** O(h) — go all the way left
- **Find maximum:** O(h) — go all the way right
- **Find successor:** O(h) — leftmost in right subtree (or first right ancestor)
- **Find predecessor:** O(h) — rightmost in left subtree
- **Validate BST:** O(n) — check every node against bounds

All operations depend on height h. Balanced: h = log n. Skewed: h = n.

> [↑ Back to Top](#top)

<a id="8-validate"></a>
# 8. Validate BST

Vera needs to verify that someone else's cabinet actually follows the BST rule. She passes valid bounds down the recursion — each node must be within its allowed range.

```python
def is_valid_bst(root, min_val=float('-inf'), max_val=float('inf')):
    if root is None:
        return True
    if not (min_val < root.val < max_val):
        return False
    return (is_valid_bst(root.left,  min_val, root.val) and
            is_valid_bst(root.right, root.val, max_val))
```

**Common mistake — checking only parent-child:** Verifying only `node.val > node.left.val` approves invalid trees where a deep node violates an ancestor's constraint. Always use bounds.

> 📝 **Practice:** [Q12 · Bounds approach](./practice.md#q12----validate-bst-using-minmax-bounds) · [Q24 · Inorder vs bounds](./practice.md#q24----two-approaches-to-bst-validation)
> 📝 **Practice:** [Q37 · bst-properties](../dsa_practice_questions_100.md#q37--critical--bst-properties)

> [↑ Back to Top](#top)

<a id="9-comparison"></a>
# 9. BST vs Sorted Array vs Hash Map

Vera asks: "When should I use my filing cabinet (BST) instead of a sorted shelf (array) or a hash table?" The answer depends on which operations matter most.

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

- **Sorted Array:** Fast search but inserting shifts everything. Best for read-heavy, rarely-updated data.
- **Hash Map:** Blazing fast for exact lookups but no concept of "order." Cannot answer range queries.
- **BST:** The balanced compromise — fast search AND fast insert AND supports ordering AND range queries.

**When to choose BST:** need both fast search + fast insert, need range queries, need sorted output frequently.

**Common mistake — range query visits entire tree:** Use BST property to prune: skip left subtree if `node.val <= low`; skip right if `node.val >= high`. Gives O(k + h) instead of O(n).

**Common mistake — using general O(n) LCA on a BST:** BST's ordering lets you solve LCA in O(h): if both targets < node, go left; both > node, go right; otherwise current node is the LCA.

> 📝 **Practice:** [Q7 · BST vs hash map tradeoffs](./practice.md#q7----bst-vs-sorted-array-vs-hash-map)

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

| Concept | Key Takeaway |
|---------|-------------|
| BST Rule | All left < node < all right (entire subtree, not just children) |
| Search | O(h) — follow left/right like binary search |
| Insert | O(h) — find empty slot following rule |
| Delete | 3 cases: leaf (snip), one child (bypass), two children (inorder successor) |
| Height | Balanced = O(log n). Skewed = O(n) |
| Inorder | Left → Node → Right gives sorted output for free |
| Validate | Pass (min, max) bounds down recursion |
| vs Hash Map | BST wins when you need order, range queries, or sorted output |

**Real-world usage:** database indexing, symbol tables (compilers), ordered maps (`TreeMap`, `std::map`), file systems, scheduling systems.

**Mental model:** A BST is a filing cabinet where every drawer says "go left if smaller, go right if bigger." You eliminate half at every step — as long as you keep it balanced.

Understanding BST unlocks: AVL Trees, Red-Black Trees, Segment Trees, `TreeMap`/`OrderedSet`, and many interview problems.

> 📝 **Practice:** [Q38 · bst-search-insert](../dsa_practice_questions_100.md#q38--normal--bst-search-insert)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [14_trees → theory.md](../14_trees/theory.md) |
| ➡ Next Module | [16_heaps → theory.md](../16_heaps/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[14 Trees →](../14_trees/theory.md) · [16 Heaps →](../16_heaps/theory.md) · [06 Searching →](../06_searching/theory.md) · [13 Binary Search →](../13_binary_search/theory.md)

**Jump to specific topics in other files:**
- Tree basics → [14_trees § theory.md](../14_trees/theory.md)
- Binary search (array version) → [13_binary_search § theory.md](../13_binary_search/theory.md)
- Heap (another tree structure) → [16_heaps § theory.md](../16_heaps/theory.md)
- Self-balancing trees → mentioned here conceptually; detailed in advanced modules

> [↑ Back to Top](#top)
