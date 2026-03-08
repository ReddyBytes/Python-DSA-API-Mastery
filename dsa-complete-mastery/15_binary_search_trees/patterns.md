# BST Problem Patterns — Recognition and Templates

> "A BST is a sorted array wearing a tree costume. Every BST trick is a trick you already know about sorted data."

---

## The Big Idea Before Everything Else

A binary search tree has one superpower: **its inorder traversal is sorted**. That's it. That's the whole secret. Every single BST pattern flows from this one fact.

When you're stuck on a BST problem, ask yourself: "If this were a sorted array, how would I solve it?" Then figure out how to get that same logic to work on the tree shape.

Let's also establish the BST property formally, because Pattern 1 depends on being precise about it:

```
For every node X in a BST:
- ALL nodes in X's LEFT subtree have values STRICTLY LESS than X.val
- ALL nodes in X's RIGHT subtree have values STRICTLY GREATER than X.val

Note: This applies to the ENTIRE subtree, not just direct children.
```

This distinction (entire subtree, not just children) is the source of the most common BST mistake, and we'll address it head-on in Pattern 1.

---

## Our Standard Node Definition

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

---

## Pattern 1: BST Validation

### The Story

A company claims their database is sorted. You need to verify it. A naive inspector checks: "Is each manager earning more than their left report and less than their right report?" But this can be fooled:

```
      10
     /  \
    5    15
   / \
  3   12   ← 12 is greater than 10 (the ROOT), but it's in the LEFT subtree!
             This tree is NOT a valid BST.
```

The naive check (only compare with direct parent) misses this. The 12 looks fine locally (12 > 5), but violates the global BST invariant (12 should be less than 10, since it's in 10's left subtree).

The fix: pass down a valid RANGE for each subtree, not just the parent's value.

### The Classic Mistake in Detail

```python
# WRONG: only checks parent-child relationship
def is_valid_bst_wrong(root):
    if not root:
        return True
    if root.left and root.left.val >= root.val:
        return False
    if root.right and root.right.val <= root.val:
        return False
    return is_valid_bst_wrong(root.left) and is_valid_bst_wrong(root.right)

# This INCORRECTLY accepts:
#       10
#      /  \
#     5    15
#    / \
#   3   12    ← 12 > 5 (ok locally), but 12 > 10 (violates BST globally!)
```

The wrong approach checks if 12 > 5 (its parent) — passes. But it doesn't know that 12 is supposed to be less than 10 (the grandparent root).

### The Correct Approach: Range Bounds

```
        10  [min=-inf, max=+inf]
       /  \
      5    15
[min=-inf,  [min=10,
 max=10]     max=+inf]
     / \
    3   12
[min=-inf, [min=5,
 max=5]     max=10]
            ↑
            12 must be in range (5, 10)
            But 12 > 10, so INVALID!
```

Every node receives a range [min_val, max_val] from its parent. The node's value must fall strictly within that range.

### Full Implementation

```python
def is_valid_bst(root):
    """
    Validate BST by passing min/max bounds top-down.

    Each node must satisfy: min_val < node.val < max_val
    - Left child inherits: same min_val, max_val = current node's value
    - Right child inherits: min_val = current node's value, same max_val
    """
    def validate(node, min_val, max_val):
        if not node:
            return True  # null node is always valid

        # Check this node's value against its valid range
        if node.val <= min_val or node.val >= max_val:
            return False

        # Recurse: tighten the bounds for children
        left_valid = validate(node.left, min_val, node.val)   # left must be < node.val
        right_valid = validate(node.right, node.val, max_val)  # right must be > node.val

        return left_valid and right_valid

    return validate(root, float('-inf'), float('inf'))


# Trace on invalid tree:
#       10
#      /  \
#     5    15
#    / \
#   3   12
#
# validate(10, -inf, +inf): 10 in (-inf, +inf) ✓
#   validate(5, -inf, 10): 5 in (-inf, 10) ✓
#     validate(3, -inf, 5): 3 in (-inf, 5) ✓
#       validate(None, ...) → True
#       validate(None, ...) → True
#       return True
#     validate(12, 5, 10): 12 in (5, 10)?? 12 > 10 → False! ✗
#   → False propagates up
# Result: False (invalid BST)
```

### Visual: Valid vs Invalid BSTs

```
VALID BST:              INVALID BST:
      8                       8
     / \                     / \
    3   10                  3   10
   / \    \                / \    \
  1   6    14             1   6    5  ← 5 < 8 but in RIGHT subtree!
     / \                     / \
    4   7                   4   7

All left descendants < node ✓    5 should be < 8, but it's to the right ✗
All right descendants > node ✓

Range check:
1 in (-inf, 3) ✓              5 in (10, +inf)?? 5 < 10 → INVALID ✗
3 in (-inf, 8) ✓
6 in (3, 8) ✓
4 in (3, 6) ✓
7 in (6, 8) ✓
10 in (8, +inf) ✓
14 in (10, +inf) ✓
```

### Iterative Variant Using Inorder

Since inorder of BST = sorted array, we can validate by checking that inorder sequence is strictly increasing:

```python
def is_valid_bst_iterative(root):
    """
    Alternative: inorder traversal must be strictly increasing.
    """
    stack = []
    prev_val = float('-inf')
    current = root

    while stack or current:
        # Go as far left as possible
        while current:
            stack.append(current)
            current = current.left

        current = stack.pop()

        # Inorder visit: check strictly increasing
        if current.val <= prev_val:
            return False
        prev_val = current.val

        current = current.right

    return True
```

### Complexity
- **Time**: O(N) — each node visited once
- **Space**: O(H) for the recursion stack (O(log N) for balanced, O(N) for skewed)

### When NOT to Use Range Validation

- When you just need to search for a value (use Pattern 2)
- When you're modifying the tree (use Pattern 2's insert/delete)

---

## Pattern 2: BST Search, Insert, and Delete

### The Story

A BST is like a well-organized library where books are arranged so that at every shelf junction, everything to the left has a smaller dewey decimal number and everything to the right has a larger one. To find a book, you never need to check both sides — the value tells you which way to go.

This is the core BST navigation pattern: at each node, decide LEFT or RIGHT based on value comparison.

### Operation 1: Search

```python
def search_bst(root, target):
    """
    Find the node with value = target in BST.
    Iterative (preferred — avoids O(H) stack overhead).
    """
    current = root

    while current:
        if target == current.val:
            return current       # found!
        elif target < current.val:
            current = current.left   # target is smaller → go left
        else:
            current = current.right  # target is larger → go right

    return None  # not found


def search_bst_recursive(root, target):
    """Recursive variant."""
    if not root:
        return None
    if target == root.val:
        return root
    elif target < root.val:
        return search_bst_recursive(root.left, target)
    else:
        return search_bst_recursive(root.right, target)
```

### Operation 2: Insert

```python
def insert_bst(root, val):
    """
    Insert value into BST. Returns the root of the modified tree.
    Strategy: navigate to the correct null position, create node there.
    """
    if not root:
        return TreeNode(val)  # found the insertion point!

    if val < root.val:
        root.left = insert_bst(root.left, val)   # insert into left subtree
    elif val > root.val:
        root.right = insert_bst(root.right, val)  # insert into right subtree
    # if val == root.val: duplicate, do nothing (or handle as needed)

    return root

# Trace: insert 4 into BST rooted at 5
#       5              5
#      / \     →      / \
#     3   7          3   7
#    / \            / \
#   2   4          2   4  ← inserted here!
#
# insert(5, 4): 4 < 5, go left
#   insert(3, 4): 4 > 3, go right
#     insert(None, 4): return TreeNode(4)
#   3.right = TreeNode(4), return 3
# 5.left = 3, return 5
```

### Operation 3: Delete (The Tricky One)

Deletion has three cases, and the third case (node has two children) requires a clever trick.

```
Case 1: Node has no children (leaf)
        → Just remove it. Easy.

        Delete 4:
        5               5
       / \     →       / \
      3   7           3   7
     / \             /
    2   4           2

Case 2: Node has exactly one child
        → Replace node with its child.

        Delete 3 (has only left child 2):
        5               5
       / \     →       / \
      3   7           2   7
     /
    2

Case 3: Node has two children
        → Replace node's value with its INORDER SUCCESSOR
          (the smallest value in its right subtree),
          then delete the inorder successor from the right subtree.

        Delete 3 (has two children 2 and 4):
        5               5
       / \     →       / \
      3   7           4   7
     / \             /
    2   4           2

        Inorder successor of 3 = 4 (smallest in right subtree of 3)
        Replace 3's value with 4, then delete 4 from right subtree.
```

```python
def delete_bst(root, key):
    """
    Delete node with value = key from BST.
    Returns the root of the modified tree.
    """
    if not root:
        return None

    if key < root.val:
        root.left = delete_bst(root.left, key)    # key is in left subtree
    elif key > root.val:
        root.right = delete_bst(root.right, key)  # key is in right subtree
    else:
        # Found the node to delete!

        # Case 1: No children (leaf) — handled by Case 2 automatically
        # Case 2: One child
        if not root.left:
            return root.right  # replace with right child (or None if no children)
        if not root.right:
            return root.left   # replace with left child

        # Case 3: Two children
        # Find inorder successor (smallest in right subtree)
        inorder_successor = find_min(root.right)

        # Replace current node's value with successor's value
        root.val = inorder_successor.val

        # Delete the successor from the right subtree
        # (the successor is now a "duplicate" that needs to be removed)
        root.right = delete_bst(root.right, inorder_successor.val)

    return root


def find_min(node):
    """Find the minimum value node in a BST (leftmost node)."""
    while node.left:
        node = node.left
    return node


def find_max(node):
    """Find the maximum value node in a BST (rightmost node)."""
    while node.right:
        node = node.right
    return node
```

### Complexity Summary

| Operation | Average (Balanced) | Worst (Skewed) |
|---|---|---|
| Search | O(log N) | O(N) |
| Insert | O(log N) | O(N) |
| Delete | O(log N) | O(N) |

The worst case occurs when the BST degenerates into a linked list (e.g., inserting sorted data).

---

## Pattern 3: BST Inorder = Sorted Array

### The Story

This is the crown jewel of BST knowledge. The inorder traversal of a BST visits nodes in ascending order. This means any problem that would be "easy if you had a sorted array" can be solved efficiently on a BST.

```
BST:                Inorder traversal:
      5
     / \             1, 2, 3, 4, 5, 6, 7, 8, 9
    3   7
   / \ / \
  2  4 6  9
 /       /
1       8

The tree IS the sorted array [1,2,3,4,5,6,7,8,9].
It's just arranged in 2D for fast search.
```

### Application 1: Kth Smallest Element

Find the kth smallest element in a BST. If you extracted to a sorted array first, the answer would be at index k-1. But you can stop early!

```python
def kth_smallest(root, k):
    """
    Find kth smallest using iterative inorder traversal.
    Stop as soon as we've visited k nodes.
    Time: O(H + k) — don't need to visit all N nodes!
    """
    stack = []
    current = root
    count = 0

    while stack or current:
        # Go as far left as possible (these are the smallest values)
        while current:
            stack.append(current)
            current = current.left

        current = stack.pop()
        count += 1

        if count == k:
            return current.val  # found the kth smallest!

        current = current.right

    return -1  # k is larger than the tree's size


# Trace for kth_smallest(tree, k=3):
# tree:       5
#            / \
#           3   7
#          / \
#         2   4
#        /
#       1
#
# Push 5, 3, 2, 1 (going left)
# Pop 1 → count=1 (1st smallest)
# Go right (None)
# Pop 2 → count=2 (2nd smallest)
# Go right (None)
# Pop 3 → count=3 (3rd smallest = 3!) ← return 3
```

### Application 2: Find Closest Value to Target

```python
def closest_value(root, target):
    """
    Find the value in BST closest to the given target.
    Use BST property to navigate: go left if target < root, right if target > root.
    Track the closest value seen so far.
    """
    closest = root.val

    while root:
        # Update closest if current node is closer to target
        if abs(root.val - target) < abs(closest - target):
            closest = root.val

        # Navigate: go toward the target
        if target < root.val:
            root = root.left
        elif target > root.val:
            root = root.right
        else:
            return root.val  # exact match!

    return closest
```

### Application 3: Check if Two BSTs Have Same Elements

```python
def same_elements(root1, root2):
    """
    Check if two BSTs contain the same set of values.
    Inorder both to sorted sequences, compare.
    """
    def inorder(root):
        result = []
        stack = []
        current = root
        while stack or current:
            while current:
                stack.append(current)
                current = current.left
            current = stack.pop()
            result.append(current.val)
            current = current.right
        return result

    return inorder(root1) == inorder(root2)

# More efficient: use generators to avoid storing full arrays
def same_elements_efficient(root1, root2):
    def inorder_gen(root):
        stack, current = [], root
        while stack or current:
            while current:
                stack.append(current)
                current = current.left
            current = stack.pop()
            yield current.val
            current = current.right

    for v1, v2 in zip(inorder_gen(root1), inorder_gen(root2)):
        if v1 != v2:
            return False
    # Also check lengths are equal
    return True
```

### Application 4: Validate BST Using Inorder

```python
def validate_bst_inorder(root):
    """
    Inorder must be strictly increasing for a valid BST.
    """
    prev = [float('-inf')]

    def inorder(node):
        if not node:
            return True
        if not inorder(node.left):
            return False
        if node.val <= prev[0]:
            return False
        prev[0] = node.val
        return inorder(node.right)

    return inorder(root)
```

### Complexity
- **Full inorder to array**: O(N) time, O(N) space
- **Kth smallest (early stop)**: O(H + k) time, O(H) space

---

## Pattern 4: Range Queries on BST

### The Story

You have a BST of employee salaries. Your HR department asks: "How many employees earn between $50K and $100K?" A naive approach visits all employees (inorder) and filters. But smart BST traversal prunes entire branches:

- If a node's salary < $50K → everything in its left subtree is also < $50K → skip left
- If a node's salary > $100K → everything in its right subtree is also > $100K → skip right

This pruning is the superpower of range queries on BSTs.

### The Key Insight: Strategic Pruning

```
Tree of salaries (in thousands):
           75
          /  \
        40    90
       /  \  /  \
      20  60 80  110
             \
              85

Query: sum of salaries in [70, 90]

Visit 75: in range! Add 75.
  Go left (40): 40 < 70, so 40 and everything left of 40 are OUT.
    But 40's right subtree might have values in range! Go right.
    Visit 60: 60 < 70, still out of range.
      60's right is None. Stop.
  Go right (90): 90 in [70, 90]! Add 90.
    Go left (80): 80 in range! Add 80.
      80's right: 85 in range! Add 85.
    Go right (110): 110 > 90, so 110 and everything right of 110 are OUT.
      But 110's left subtree might have values in range... (None in this case)

Total: 75 + 90 + 80 + 85 = 330
```

### Full Implementation: Range Sum BST

```python
def range_sum_bst(root, low, high):
    """
    Sum all values in BST where low <= val <= high.
    Prune branches that can't possibly contain valid values.
    """
    if not root:
        return 0

    total = 0

    # Include current node if it's in range
    if low <= root.val <= high:
        total += root.val

    # Only recurse left if current node could have valid left children
    # (current node's value > low means left subtree MIGHT have values >= low)
    if root.val > low:
        total += range_sum_bst(root.left, low, high)

    # Only recurse right if current node could have valid right children
    # (current node's value < high means right subtree MIGHT have values <= high)
    if root.val < high:
        total += range_sum_bst(root.right, low, high)

    return total


# Time complexity analysis:
# Naive (inorder all, filter): O(N)
# With pruning: O(N) worst case (query covers everything),
#              O(log N + K) average where K = nodes in range
#              (the log N is for navigating to the range boundaries)
```

### Collect All Values in Range

```python
def range_query_bst(root, low, high):
    """
    Collect all values in BST where low <= val <= high.
    Returns sorted list (since BST inorder is sorted).
    """
    result = []

    def dfs(node):
        if not node:
            return

        # Prune left: only go left if there might be valid values there
        if node.val > low:
            dfs(node.left)

        # Visit: add if in range
        if low <= node.val <= high:
            result.append(node.val)

        # Prune right: only go right if there might be valid values there
        if node.val < high:
            dfs(node.right)

    dfs(root)
    return result  # automatically sorted due to inorder pattern!
```

### Find Closest Values in Range (Nearest Nodes)

```python
def find_k_closest_to_target(root, target, k):
    """
    Find k values in BST closest to the given target.
    Strategy: inorder gives sorted sequence; use sliding window or heap.
    """
    from collections import deque

    window = deque()

    def inorder(node):
        if not node:
            return

        inorder(node.left)

        # Maintain window of k closest values
        if len(window) < k:
            window.append(node.val)
        elif abs(node.val - target) < abs(window[0] - target):
            # Current value is closer than the oldest in our window
            window.popleft()
            window.append(node.val)
        else:
            # Inorder: once current is farther than window's oldest,
            # all subsequent values will be even farther (for sorted order)
            return

        inorder(node.right)

    inorder(root)
    return list(window)
```

### Complexity Comparison

| Approach | Time | Space | Notes |
|---|---|---|---|
| Inorder all, then filter | O(N) | O(N) | Visits every node |
| BST range query with pruning | O(log N + K) avg | O(H) | Skips irrelevant branches |
| Where K = number of results in range | | | |

---

## Pattern 5: Augmented BST (Order Statistics)

### The Story

You're running a leaderboard for a game. Players join and leave constantly. You need to answer in real-time: "What rank is player X?" or "Who is in 5th place?" A regular BST supports search/insert/delete in O(log N), but rank queries naively take O(N).

The solution: augment each node with a `size` field — the number of nodes in its subtree (including itself). With this extra information, rank queries become O(log N).

### The Augmented Node

```python
class AugmentedNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.size = 1  # subtree size including this node

# Visual:
#          10 (size=7)
#         /          \
#    5 (size=4)    15 (size=2)
#   /      \          \
# 3(s=2)  7(s=1)    20(s=1)
# /
# 1(s=1)
#
# Size of any node = 1 + size(left) + size(right)
```

### Finding Kth Smallest Using Augmented BST

```python
def kth_smallest_augmented(root, k):
    """
    Find kth smallest using subtree sizes.
    O(log N) for balanced BST.

    At each node:
    - left_size = size of left subtree
    - If k == left_size + 1: current node is the answer
    - If k <= left_size: answer is in left subtree
    - If k > left_size + 1: answer is in right subtree (adjust k)
    """
    while root:
        left_size = root.left.size if root.left else 0

        if k == left_size + 1:
            return root.val  # this is the kth smallest!
        elif k <= left_size:
            root = root.left  # kth smallest is in the left subtree
        else:
            k -= left_size + 1  # skip left subtree and current node
            root = root.right

    return -1  # k out of bounds


# Trace: find 4th smallest in tree above
# root=10, left_size=4
#   k=4, left_size+1=5 → 4 < 5, so answer is in left
#   root=5, left_size=2
#     k=4, left_size+1=3 → 4 > 3, so answer in right, k = 4-2-1 = 1
#     root=7, left_size=0
#       k=1, left_size+1=1 → k==1! → return 7
# 4th smallest = 7? Let's verify: inorder = 1,3,5,7,10,15,20 → 4th = 7 ✓
```

### Rank of an Element

```python
def get_rank(root, val):
    """
    Return the rank of val in the BST (1-indexed: rank 1 = smallest).
    """
    rank = 0

    while root:
        if val < root.val:
            root = root.left
        elif val > root.val:
            left_size = root.left.size if root.left else 0
            rank += left_size + 1  # count left subtree + current node
            root = root.right
        else:  # val == root.val
            left_size = root.left.size if root.left else 0
            rank += left_size + 1
            return rank

    return -1  # val not in tree
```

### Maintaining the Size During Insert

```python
def insert_augmented(root, val):
    """
    Insert while maintaining size fields.
    """
    if not root:
        return AugmentedNode(val)

    if val < root.val:
        root.left = insert_augmented(root.left, val)
    elif val > root.val:
        root.right = insert_augmented(root.right, val)

    # Update size after insertion
    left_size = root.left.size if root.left else 0
    right_size = root.right.size if root.right else 0
    root.size = 1 + left_size + right_size

    return root
```

### Complexity
- **Kth smallest with augmentation**: O(log N) for balanced BST vs O(H + k) for iterative inorder
- **Space overhead**: O(1) per node (just one extra integer)
- **Insert/delete**: O(log N) with size updates propagating up

---

## Pattern 6: Convert BST to/from Other Structures

### The Story

BSTs don't exist in isolation. Sometimes you need to flatten them into arrays, wire them into linked lists, or reshape them entirely. These transformations follow predictable patterns based on the inorder = sorted property.

### Conversion 1: Sorted Array to Balanced BST

The key: always pick the **midpoint** as the root. This guarantees both sides have equal (or ±1) nodes, creating a balanced tree.

```python
def sorted_array_to_bst(nums):
    """
    Convert sorted array to height-balanced BST.
    Midpoint becomes root, left half becomes left subtree, right half becomes right.
    """
    def build(left, right):
        if left > right:
            return None

        mid = (left + right) // 2
        root = TreeNode(nums[mid])
        root.left = build(left, mid - 1)
        root.right = build(mid + 1, right)
        return root

    return build(0, len(nums) - 1)

# Example: nums = [1, 2, 3, 4, 5, 6, 7]
# build(0, 6): mid=3, root=4
#   build(0, 2): mid=1, root=2
#     build(0, 0): mid=0, root=1 (leaf)
#     build(2, 2): mid=2, root=3 (leaf)
#   build(4, 6): mid=5, root=6
#     build(4, 4): mid=4, root=5 (leaf)
#     build(6, 6): mid=6, root=7 (leaf)
#
# Result:
#         4
#        / \
#       2   6
#      / \ / \
#     1  3 5  7
```

### Conversion 2: BST to Doubly Linked List (In-place)

Wire the BST nodes into a circular doubly linked list using inorder traversal. The left pointer becomes "previous" and the right pointer becomes "next."

```python
def bst_to_doubly_linked_list(root):
    """
    Convert BST to sorted circular doubly linked list in-place.
    No new nodes — just rewire left/right pointers.

    Returns the head (smallest element) of the linked list.
    """
    if not root:
        return None

    # Track the head and previous node during inorder traversal
    head = [None]   # smallest node (first in inorder)
    prev = [None]   # previous node in inorder

    def inorder(node):
        if not node:
            return

        inorder(node.left)

        # Wire current node into the doubly linked list
        if prev[0]:
            prev[0].right = node  # prev.next = current
            node.left = prev[0]   # current.prev = prev
        else:
            head[0] = node  # first node in inorder = head of list

        prev[0] = node

        inorder(node.right)

    inorder(root)

    # Make it circular: connect head and tail
    tail = prev[0]
    head[0].left = tail
    tail.right = head[0]

    return head[0]
```

### Conversion 3: BST to Greater Sum Tree (Reverse Inorder)

Replace each node's value with the sum of all values **greater than or equal to it** in the BST. This is solved by reverse inorder traversal (right → node → left), accumulating the sum.

```python
def convert_bst_to_greater_tree(root):
    """
    Replace each node's value with sum of all values >= node.val.

    Key insight: reverse inorder (right → root → left) visits nodes
    in DECREASING order. We accumulate the running sum.

    Example:
    BST:             Greater Sum Tree:
        5                  18 (18 = 5+6+7)
       / \        →       /  \
      2   6              20    13 (13 = 6+7)
       \   \               \    \
        3   7               22    7
    (greater sums for 2 = 2+3+5+6+7=23, etc.)

    Wait: each node becomes sum of all values >= itself:
    7 → 7
    6 → 6+7 = 13
    5 → 5+6+7 = 18
    3 → 3+5+6+7 = 21
    2 → 2+3+5+6+7 = 23
    """
    cumsum = [0]

    def reverse_inorder(node):
        if not node:
            return

        reverse_inorder(node.right)   # process larger values first

        cumsum[0] += node.val
        node.val = cumsum[0]          # replace with cumulative sum

        reverse_inorder(node.left)    # then process smaller values

    reverse_inorder(root)
    return root
```

### Conversion 4: Flatten BST to Sorted Linked List (using right pointers)

```python
def bst_to_sorted_list(root):
    """
    Flatten BST into a "linked list" using only right pointers.
    Result: root → 2nd smallest → 3rd smallest → ... → largest
    (Like a right-skewed tree where right pointer = next in sorted order)
    """
    # Collect inorder, rebuild as right-chain
    sorted_vals = []

    def inorder(node):
        if not node:
            return
        inorder(node.left)
        sorted_vals.append(node.val)
        inorder(node.right)

    inorder(root)

    if not sorted_vals:
        return None

    dummy = TreeNode(0)
    current = dummy
    for val in sorted_vals:
        current.right = TreeNode(val)
        current = current.right

    return dummy.right
```

### Complexity
- **Sorted array to BST**: O(N) time, O(log N) space (recursion)
- **BST to doubly linked list**: O(N) time, O(H) space
- **Greater sum tree**: O(N) time, O(H) space

---

## Pattern 7: Two BSTs / Multi-Tree Problems

### The Story

Sometimes problems involve multiple BSTs and you need to operate across them: merge two BSTs, find elements in both, find the median of combined data. The go-to technique: convert each BST to its sorted inorder sequence, then use the sorted-array algorithms you already know.

### Merge Two BSTs

```python
def merge_two_bsts(root1, root2):
    """
    Merge two BSTs into one balanced BST.

    Strategy:
    1. Get inorder sequence of BST1 (sorted array A)
    2. Get inorder sequence of BST2 (sorted array B)
    3. Merge sorted arrays A and B (like merge sort's merge step)
    4. Build balanced BST from merged sorted array
    """

    def inorder_to_list(node):
        result = []
        def traverse(n):
            if not n:
                return
            traverse(n.left)
            result.append(n.val)
            traverse(n.right)
        traverse(node)
        return result

    def merge_sorted(a, b):
        merged = []
        i = j = 0
        while i < len(a) and j < len(b):
            if a[i] <= b[j]:
                merged.append(a[i])
                i += 1
            else:
                merged.append(b[j])
                j += 1
        merged.extend(a[i:])
        merged.extend(b[j:])
        return merged

    def sorted_to_bst(nums, left, right):
        if left > right:
            return None
        mid = (left + right) // 2
        node = TreeNode(nums[mid])
        node.left = sorted_to_bst(nums, left, mid - 1)
        node.right = sorted_to_bst(nums, mid + 1, right)
        return node

    list1 = inorder_to_list(root1)
    list2 = inorder_to_list(root2)
    merged = merge_sorted(list1, list2)
    return sorted_to_bst(merged, 0, len(merged) - 1)


# Example:
# BST1:   BST2:
#   2       1
#  / \     / \
# 1   4   0   3
#
# inorder(BST1) = [1, 2, 4]
# inorder(BST2) = [0, 1, 3]
# merged = [0, 1, 1, 2, 3, 4]
# balanced BST from [0,1,1,2,3,4]:
#         1
#        / \
#       0   2
#        \   \
#         1   3
#              \
#               4
```

### Find All Elements in Both BSTs

```python
def find_common_elements(root1, root2):
    """
    Find all values that appear in both BSTs.
    Strategy: inorder both to sorted arrays, find intersection.
    """
    def inorder(node):
        result = []
        stack, current = [], node
        while stack or current:
            while current:
                stack.append(current)
                current = current.left
            current = stack.pop()
            result.append(current.val)
            current = current.right
        return result

    list1 = inorder(root1)
    list2 = inorder(root2)

    # Find intersection of two sorted arrays
    result = []
    i = j = 0
    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            result.append(list1[i])
            i += 1
            j += 1
        elif list1[i] < list2[j]:
            i += 1
        else:
            j += 1

    return result
```

### Median of a BST Stream (Two-BST Approach with Two Heaps)

For finding the running median as values are inserted:

```python
import heapq

class MedianFinderBST:
    """
    Find median dynamically as values are inserted.
    Uses two heaps (conceptually two sorted halves).

    Invariant:
    - max_heap holds the lower half (python's heapq is min-heap, so negate values)
    - min_heap holds the upper half
    - len(max_heap) >= len(min_heap) (max_heap can have one more element)
    - All values in max_heap <= all values in min_heap
    """
    def __init__(self):
        self.max_heap = []  # lower half, stored as negative (simulates max-heap)
        self.min_heap = []  # upper half

    def add_num(self, num):
        # Always push to max_heap first
        heapq.heappush(self.max_heap, -num)

        # Ensure max_heap's top <= min_heap's top
        if self.min_heap and -self.max_heap[0] > self.min_heap[0]:
            val = -heapq.heappop(self.max_heap)
            heapq.heappush(self.min_heap, val)

        # Rebalance sizes: max_heap can have at most 1 more element
        if len(self.max_heap) > len(self.min_heap) + 1:
            val = -heapq.heappop(self.max_heap)
            heapq.heappush(self.min_heap, val)
        elif len(self.min_heap) > len(self.max_heap):
            val = heapq.heappop(self.min_heap)
            heapq.heappush(self.max_heap, -val)

    def find_median(self):
        if len(self.max_heap) > len(self.min_heap):
            return -self.max_heap[0]  # odd total, median is max_heap's top
        return (-self.max_heap[0] + self.min_heap[0]) / 2  # even total
```

### BST Iterator (Flatten BST for Sequential Access)

```python
class BSTIterator:
    """
    Implement an iterator over BST (returns values in sorted order).
    Each call to next() returns the next smallest element.

    Space: O(H) — only stores the path to current node, not the full tree.
    Time: O(1) amortized per next() call.
    """
    def __init__(self, root):
        self.stack = []
        self._push_left(root)

    def _push_left(self, node):
        """Push all left children onto the stack."""
        while node:
            self.stack.append(node)
            node = node.left

    def next(self):
        node = self.stack.pop()
        if node.right:
            self._push_left(node.right)
        return node.val

    def has_next(self):
        return len(self.stack) > 0
```

### Complexity
- **Merge two BSTs**: O(M + N) time where M, N are tree sizes; O(M + N) space
- **Common elements**: O(M + N) time, O(M + N) space
- **BST Iterator**: O(1) amortized per next(), O(H) space

---

## The BST Cheat Sheet

```
Problem says...                           →  Use this pattern
──────────────────────────────────────────────────────────────────
"is this a valid BST?"                    →  Pattern 1 (Range Bounds)
"search/find value in BST"                →  Pattern 2 (Navigate by value)
"insert into BST"                         →  Pattern 2 (Navigate to null spot)
"delete from BST"                         →  Pattern 2 (3 cases)
"kth smallest"                            →  Pattern 3 (Inorder = sorted)
"closest value to target"                 →  Pattern 3 (Navigate BST)
"sum of values in range [L, R]"           →  Pattern 4 (Range query with pruning)
"all values between L and R"              →  Pattern 4 (Range query)
"kth smallest with O(log N)"              →  Pattern 5 (Augmented BST)
"rank of element"                         →  Pattern 5 (Augmented BST)
"sorted array to BST"                     →  Pattern 6 (Midpoint as root)
"BST to doubly linked list"               →  Pattern 6 (Inorder wiring)
"BST to greater sum tree"                 →  Pattern 6 (Reverse inorder)
"merge two BSTs"                          →  Pattern 7 (Inorder both, merge, rebuild)
"find common elements in two BSTs"        →  Pattern 7 (Inorder both, find intersection)
──────────────────────────────────────────────────────────────────
```

---

## Common BST Mistakes to Avoid

### Mistake 1: Comparing only with immediate parent

```python
# WRONG
def is_valid(node, parent_val, is_left):
    if not node:
        return True
    if is_left and node.val >= parent_val:
        return False
    if not is_left and node.val <= parent_val:
        return False
    return is_valid(node.left, node.val, True) and is_valid(node.right, node.val, False)

# RIGHT: pass full bounds
def is_valid(node, min_val, max_val):
    if not node:
        return True
    if not (min_val < node.val < max_val):
        return False
    return is_valid(node.left, min_val, node.val) and is_valid(node.right, node.val, max_val)
```

### Mistake 2: Using index-based split instead of value-based search

```python
# WRONG for inorder extraction (this is array logic, not BST logic)
mid = n // 2

# RIGHT: use BST navigation
while current:
    if target < current.val:
        current = current.left
    elif target > current.val:
        current = current.right
    else:
        return current
```

### Mistake 3: Forgetting to update size in augmented BST

```python
# WRONG: insert without updating size
def insert(root, val):
    if not root:
        return AugmentedNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    return root  # FORGOT to update root.size!

# RIGHT: always update size after modifying children
def insert(root, val):
    if not root:
        return AugmentedNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    # Update size
    root.size = 1 + (root.left.size if root.left else 0) + (root.right.size if root.right else 0)
    return root
```

### Mistake 4: Off-by-one in kth smallest with augmented BST

```python
# WRONG: forgetting +1 for current node
left_size = root.left.size if root.left else 0
if k == left_size:       # ← BUG: should be left_size + 1
    return root.val

# RIGHT
if k == left_size + 1:   # left_size nodes to the left, plus this node = left_size+1
    return root.val
```

---

## Interview Strategy for BST Problems

When you see a BST problem in an interview, go through this mental checklist:

1. **Is this just BST navigation?** (search/insert/delete) → Pattern 2
2. **Does it involve a sorted property?** ("kth smallest", "closest value") → Pattern 3 (inorder = sorted)
3. **Is there a range constraint?** ("sum in [L,R]", "values between") → Pattern 4 (prune branches)
4. **Do I need O(log N) rank queries?** → Pattern 5 (augment with size)
5. **Am I converting to/from another structure?** → Pattern 6
6. **Are there multiple BSTs?** → Pattern 7 (convert to sorted arrays)
7. **Am I validating?** → Pattern 1 (range bounds, not parent comparison)

The meta-skill: **think about what the sorted order gives you**, and work backward from there to the BST structure.
