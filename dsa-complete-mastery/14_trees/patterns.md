# Tree Problem Patterns — The Complete Recognition Guide

> "Every tree problem is just one of eight stories. Learn the stories, solve any problem."

---

## How to Use This Guide

Before diving in, here is the meta-skill: when you see a tree problem, your first job is NOT to write code. Your first job is to ask ONE question:

**"Which direction is information flowing?"**

- Information flows **downward** (parent tells children something)? That's a top-down DFS pattern.
- Information flows **upward** (children report back to parent)? That's a bottom-up DFS pattern.
- Information flows **level by level** (we process siblings before cousins)? That's a BFS pattern.
- We're **building** a tree from raw data? That's a construction pattern.
- The path doesn't start at root? That's the path problem pattern.
- We need a common meeting point of two nodes? That's LCA.
- We're encoding/decoding the tree? That's serialization.
- We have O(1) space constraint? That's Morris traversal.

That's it. Eight stories. Let's learn each one deeply.

---

## The Cast of Characters

Before the patterns, let's define our standard tree node so all code examples share the same foundation:

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

And a quick helper to build trees from lists (for testing):

```python
from collections import deque

def build_tree(values):
    """Build tree from level-order list. None means no node."""
    if not values:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root
```

---

## Pattern 1: DFS — Top-Down (Pre-order Style)

### The Story

Imagine you're a tour guide walking a group through a massive building. Before entering each room, you tell your group: "We've walked 3 floors already, so keep that in mind." You're passing information **forward and downward** — each room gets the accumulated context from all the rooms before it.

That's top-down DFS. The parent knows something (a running sum, a current path, the depth so far), and it **passes that knowledge down** to its children before they do their own work.

### When to Use It

Use top-down DFS when:
- You need to track something that **accumulates as you go deeper**
- The decision at a node depends on **what happened above it**
- You're looking for **paths from the root** to somewhere specific
- You want to check if a **running total** matches a target

### Recognition Clues

Look for these phrases in the problem statement:
- "find all root-to-leaf paths..."
- "check if there exists a path from root to leaf with sum equal to..."
- "maximum depth from root..."
- "find nodes at depth K"
- "path from root to node X"
- "is there a path sum equal to target?"
- "encode the path as you go"

The key giveaway: the answer at a leaf node depends on everything that happened on the way down to it.

### The Mental Model

```
        1          ← root starts with accumulated = 0
       / \            it passes accumulated + 1 = 1 down
      2   3
     / \   \
    4   5   6

Top-down flow (passing target_remaining = 7, going down):

root(1): remaining = 7 - 1 = 6  → pass 6 to children
  left(2): remaining = 6 - 2 = 4  → pass 4 to children
    left(4): remaining = 4 - 4 = 0  → FOUND! (leaf with remaining=0)
    right(5): remaining = 4 - 5 = -1  → not found
  right(3): remaining = 6 - 3 = 3  → pass 3 to children
    right(6): remaining = 3 - 6 = -3  → not found
```

The parent does NOT wait for children to return — it gives children what they need to proceed.

### The Template

```python
def top_down_dfs(node, accumulated_value):
    # BASE CASE: handle null node
    if not node:
        return

    # PROCESS: use current node + accumulated value
    # (this is the "pre-order" part — we act BEFORE visiting children)
    new_accumulated = accumulated_value + node.val  # or whatever you're tracking

    # LEAF CHECK: if we're at a leaf, check if we have an answer
    if not node.left and not node.right:
        if new_accumulated == target:
            # record answer
            pass
        return

    # RECURSE: pass the accumulated value DOWN to children
    top_down_dfs(node.left, new_accumulated)
    top_down_dfs(node.right, new_accumulated)
```

### Full Example: Path Sum II

**Problem**: Given a binary tree and a target sum, find all root-to-leaf paths where the sum equals the target.

Example:
```
Tree:           target = 22
      5
     / \
    4   8
   /   / \
  11  13   4
 /  \       \
7    2       1

Paths: [5,4,11,2] → sum=22 ✓
       [5,8,4,1]  → sum=18 ✗
       [5,4,11,7] → sum=27 ✗
```

```python
def path_sum_ii(root, targetSum):
    """
    Find all root-to-leaf paths with sum = targetSum.

    Strategy: top-down DFS
    - Carry the current path (list of nodes visited so far)
    - Carry the remaining sum needed
    - At each leaf, check if remaining == 0
    """
    result = []

    def dfs(node, remaining, current_path):
        if not node:
            return

        # Add current node to path (PRE-ORDER: act before recursing)
        current_path.append(node.val)
        remaining -= node.val

        # Leaf check: have we used up exactly the target?
        if not node.left and not node.right and remaining == 0:
            result.append(list(current_path))  # copy! list is mutable

        # Pass the updated state DOWN to children
        dfs(node.left, remaining, current_path)
        dfs(node.right, remaining, current_path)

        # BACKTRACK: remove current node before returning to parent
        # This is crucial — we're sharing the list across calls
        current_path.pop()

    dfs(root, targetSum, [])
    return result


# Trace through the example:
# dfs(5, 22, [])
#   path=[5], remaining=17
#   dfs(4, 17, [5])
#     path=[5,4], remaining=13
#     dfs(11, 13, [5,4])
#       path=[5,4,11], remaining=2
#       dfs(7, 2, [5,4,11])
#         path=[5,4,11,7], remaining=-5
#         leaf! remaining != 0, skip
#         pop 7 → path=[5,4,11]
#       dfs(2, 2, [5,4,11])
#         path=[5,4,11,2], remaining=0
#         leaf! remaining == 0 → ADD [5,4,11,2] to result!
#         pop 2 → path=[5,4,11]
#       pop 11 → path=[5,4]
#     pop 4 → path=[5]
#   dfs(8, 17, [5])
#     path=[5,8], remaining=9
#     dfs(13, 9, [5,8])
#       path=[5,8,13], remaining=-4
#       leaf! remaining != 0, skip
#       pop 13 → path=[5,8]
#     dfs(4, 9, [5,8])
#       path=[5,8,4], remaining=5
#       dfs(None, ...) → return
#       dfs(1, 5, [5,8,4])
#         path=[5,8,4,1], remaining=4
#         leaf! remaining != 0, skip
#         pop 1 → path=[5,8,4]
#       pop 4 → path=[5,8]
#     pop 8 → path=[5]
#   pop 5 → path=[]
```

### Complexity
- **Time**: O(N) — every node visited exactly once
- **Space**: O(H) for the call stack (H = height), plus O(N) for storing all paths in worst case

### When NOT to Use Top-Down DFS

Do NOT use top-down when:
- The answer at a node depends on what its children return (use bottom-up instead)
- You need to process nodes level-by-level (use BFS)
- The path can start from any node, not just root (use the path problem pattern)

---

## Pattern 2: DFS — Bottom-Up (Post-order Style)

### The Story

Now you're a contractor inspecting a building for structural integrity. You start at the basement and work your way up. Each floor tells you: "My left wing can hold X tons, my right wing can hold Y tons." You combine these reports and pass your conclusion UP to the floor above you.

That's bottom-up DFS. Children finish their work first and return results. The parent then combines those results to produce its own answer.

### When to Use It

Use bottom-up DFS when:
- A node's answer **depends on information from its subtrees**
- You're computing **aggregates** (height, sum, count, diameter)
- You need to **combine** left and right subtree answers at each node
- The problem asks you to check/compute something about the **entire tree structure**

### Recognition Clues

- "height of the tree"
- "diameter of binary tree"
- "is the tree balanced?"
- "maximum path sum"
- "count nodes with specific property"
- "find the deepest node"
- "merge/combine subtrees"

The key giveaway: you cannot know a node's answer without first knowing its children's answers.

### The Mental Model

```
        1
       / \
      2   3
     / \
    4   5

Bottom-up flow (computing height):

Step 1: 4 is a leaf → returns height 1
Step 2: 5 is a leaf → returns height 1
Step 3: 2 gets reports from 4 and 5 → height = 1 + max(1, 1) = 2
Step 4: 3 is a leaf → returns height 1
Step 5: 1 gets reports from 2 and 3 → height = 1 + max(2, 1) = 3

The information flows UPWARD:

    4 → (1)
           \
    5 → (1) → 2 → (2)
                        \
    3 → (1) ----------→ 1 → (3)  ← FINAL ANSWER
```

Children complete BEFORE parent. This is post-order: left, right, THEN node.

### The Template

```python
def bottom_up_dfs(node):
    # BASE CASE: null node returns a "neutral" value
    if not node:
        return 0  # or None, or (0, 0), whatever makes sense

    # RECURSE FIRST: get children's answers
    left_result = bottom_up_dfs(node.left)
    right_result = bottom_up_dfs(node.right)

    # COMBINE: merge children's results at current node
    # (this is the "post-order" part — we act AFTER visiting children)
    current_result = 1 + max(left_result, right_result)  # example: height

    # RETURN: pass result UP to parent
    return current_result
```

### Full Example: Diameter of Binary Tree

**Problem**: Find the length of the longest path between any two nodes. The path may or may not pass through the root.

```
        1
       / \
      2   3
     / \
    4   5

The diameter is 3 (path: 4 → 2 → 1 → 3  OR  4 → 2 → 5, both length 3 edges)
Wait: 4 → 2 → 5 = 2 edges, 4 → 2 → 1 → 3 = 3 edges → diameter = 3
```

Key insight: at every node, the "longest path through this node" = left_height + right_height. The diameter is the max of this over all nodes.

```python
def diameter_of_binary_tree(root):
    """
    Strategy: bottom-up DFS
    - Each call returns the HEIGHT of its subtree
    - But as a side effect, it updates the global diameter
    - The diameter passing through any node = left_height + right_height
    """
    diameter = [0]  # use list so inner function can modify it

    def height(node):
        if not node:
            return 0

        # BOTTOM-UP: get children's heights first
        left_h = height(node.left)
        right_h = height(node.right)

        # UPDATE DIAMETER: the path through this node
        # uses left_h edges going left + right_h edges going right
        path_through_here = left_h + right_h
        diameter[0] = max(diameter[0], path_through_here)

        # RETURN HEIGHT to parent (parent needs this, not diameter)
        return 1 + max(left_h, right_h)

    height(root)
    return diameter[0]


# Trace:
# height(4): left=0, right=0 → diameter=max(0,0+0)=0, return 1
# height(5): left=0, right=0 → diameter=max(0,0+0)=0, return 1
# height(2): left=1, right=1 → diameter=max(0,1+1)=2, return 2
# height(3): left=0, right=0 → diameter=max(2,0+0)=2, return 1
# height(1): left=2, right=1 → diameter=max(2,2+1)=3, return 3
# Final: diameter = 3  ✓
```

### Bonus: Balanced Binary Tree Check (Same Pattern)

```python
def is_balanced(root):
    """
    A tree is balanced if every node's left and right subtrees
    differ in height by at most 1.

    Strategy: bottom-up — if any subtree is unbalanced, return -1
    as a sentinel value to propagate the "unbalanced" signal upward.
    """
    def check_height(node):
        if not node:
            return 0

        left_h = check_height(node.left)
        if left_h == -1:  # already found imbalance below
            return -1

        right_h = check_height(node.right)
        if right_h == -1:  # already found imbalance below
            return -1

        if abs(left_h - right_h) > 1:
            return -1  # THIS node is imbalanced — signal upward

        return 1 + max(left_h, right_h)

    return check_height(root) != -1
```

### Complexity
- **Time**: O(N) — every node visited once
- **Space**: O(H) for the call stack

### When NOT to Use Bottom-Up DFS

- When the answer at a node only depends on what came FROM ABOVE (use top-down)
- When you need nodes in level order (use BFS)
- When you need O(1) space (use Morris traversal)

### Top-Down vs Bottom-Up: The Quick Cheat

Ask yourself: "To answer the question at node X, do I need to know about X's ancestors or X's descendants?"

- Need to know about **ancestors** → top-down (pass info down)
- Need to know about **descendants** → bottom-up (collect info up)

---

## Pattern 3: BFS — Level Order

### The Story

Think about how a fire spreads in a field. It starts at one point (the root) and spreads to all neighboring areas (children). Then from all those areas, it spreads further (grandchildren). The fire processes everything at distance 1, then everything at distance 2, then distance 3...

BFS (Breadth-First Search) with a queue does exactly this. It processes all nodes at depth 1 before any node at depth 2. This is the only pattern that gives you access to "which level is this node on?" information.

### When to Use It

Use BFS when:
- You need to process nodes **level by level**
- You need to know the **depth** of a node
- You need the **right-side view** or **left-side view** of a tree
- You need to find the **leftmost/rightmost node** at each level
- You're doing anything with **cousins** (same level, different parent)
- You want the **minimum depth** (BFS finds it faster than DFS)

### Recognition Clues

- "level order traversal"
- "return nodes by level / in levels"
- "right side view" / "left side view"
- "zigzag level order"
- "average of each level"
- "are these nodes cousins?" (same depth, different parent)
- "minimum depth" (BFS finds the first leaf it reaches)
- "connect nodes at same level"

### The Mental Model

```
Tree:
        3
       / \
      9  20
         / \
        15   7

BFS processing:

Queue state over time:

Start:  [3]
After processing 3:   [9, 20]      Level 1 output: [3]
After processing 9:   [20]
After processing 20:  [15, 7]      Level 2 output: [9, 20]
After processing 15:  [7]
After processing 7:   []           Level 3 output: [15, 7]

The trick: BEFORE processing a level, we know the queue has
exactly (len(queue)) nodes in it from that level.
```

### The Template

```python
from collections import deque

def bfs_level_order(root):
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)  # SNAPSHOT: how many nodes at this level
        level_nodes = []

        for _ in range(level_size):  # process EXACTLY this level's nodes
            node = queue.popleft()
            level_nodes.append(node.val)

            # Add children (they belong to NEXT level)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(level_nodes)

    return result
```

The critical line is `level_size = len(queue)`. This is the BFS "snapshot" trick — it freezes how many nodes belong to the current level before we start processing them (and adding their children to the queue).

### Full Example: Binary Tree Level Order Traversal

```python
def level_order(root):
    """
    Return [[level0_nodes], [level1_nodes], [level2_nodes], ...]
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        current_level = []

        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(current_level)

    return result

# Input tree: [3, 9, 20, None, None, 15, 7]
# Output: [[3], [9, 20], [15, 7]]
```

### Variations Built on the Same Template

**Right Side View** (last node at each level):

```python
def right_side_view(root):
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)

        for i in range(level_size):
            node = queue.popleft()

            if i == level_size - 1:  # last node in this level
                result.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return result
```

**Zigzag Level Order** (alternate left-to-right and right-to-left):

```python
def zigzag_level_order(root):
    if not root:
        return []

    result = []
    queue = deque([root])
    left_to_right = True  # first level goes left to right

    while queue:
        level_size = len(queue)
        level = []

        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        # Reverse alternate levels
        if not left_to_right:
            level.reverse()

        result.append(level)
        left_to_right = not left_to_right

    return result
```

**Level Averages**:

```python
def average_of_levels(root):
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        level_sum = 0

        for _ in range(level_size):
            node = queue.popleft()
            level_sum += node.val

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(level_sum / level_size)

    return result
```

**Are Nodes Cousins?** (same level, different parents):

```python
def is_cousins(root, x, y):
    """
    Cousins: same depth, different parents.
    BFS naturally tracks depth. Track parent alongside each node.
    """
    queue = deque([(root, None, 0)])  # (node, parent, depth)
    x_info = y_info = None

    while queue:
        node, parent, depth = queue.popleft()

        if node.val == x:
            x_info = (parent, depth)
        if node.val == y:
            y_info = (parent, depth)

        if x_info and y_info:
            break

        if node.left:
            queue.append((node.left, node, depth + 1))
        if node.right:
            queue.append((node.right, node, depth + 1))

    # Cousins: same depth, different parents
    return (x_info[1] == y_info[1]) and (x_info[0] != y_info[0])
```

### Complexity
- **Time**: O(N) — every node visited once
- **Space**: O(W) where W is the maximum width of the tree (worst case: O(N) for a complete binary tree's bottom level)

### When NOT to Use BFS

- When you need to track path information from root to leaf (use top-down DFS)
- When a node's answer depends on its subtree (use bottom-up DFS)
- When the space cost of the queue is unacceptable (DFS uses O(H) vs BFS O(W))

---

## Pattern 4: Tree Construction

### The Story

Imagine you have a receipt that lists every room in a building in the order you visited them (preorder: lobby first, then rooms inside), and another receipt listing the rooms in the order you'd see them from outside (inorder: leftmost room, then center, then rightmost). Given BOTH lists, can you reconstruct the building's floor plan?

Yes! And that's exactly what tree construction problems ask you to do.

### When to Use It

Use the tree construction pattern when:
- You're given two traversal arrays and asked to rebuild the tree
- You're given a sorted array and asked to build a balanced BST
- You're rebuilding a tree from its serialized form

### Recognition Clues

- "construct binary tree from preorder and inorder traversal"
- "construct binary tree from inorder and postorder"
- "convert sorted array to balanced BST"
- "rebuild the tree from..."

### The Key Insight

Every traversal has a different "where is the root?" signature:

```
Preorder:  [ROOT, left subtree..., right subtree...]
            ↑ FIRST element is always root

Inorder:   [left subtree..., ROOT, right subtree...]
                              ↑ root splits left and right

Postorder: [left subtree..., right subtree..., ROOT]
                                               ↑ LAST element is always root
```

The power of inorder: once you find the root's position in inorder, you know exactly how many nodes are in the left subtree (everything to the left of root in inorder), and that tells you how to split the preorder/postorder arrays too.

### The Mental Model

```
Preorder: [3, 9, 20, 15, 7]
Inorder:  [9, 3, 15, 20, 7]

Step 1: Root = preorder[0] = 3
Step 2: Find 3 in inorder → index 1
        Left of 3 in inorder:  [9]        → 1 node in left subtree
        Right of 3 in inorder: [15, 20, 7] → 3 nodes in right subtree

Step 3: Split preorder accordingly:
        Root: [3]
        Left preorder:  [9]        (next 1 node after root)
        Right preorder: [20, 15, 7] (remaining nodes)

Step 4: Recurse:
        build(preorder=[9],        inorder=[9])
          → root=9, no left, no right
        build(preorder=[20,15,7],  inorder=[15,20,7])
          → root=20, find 20 in inorder → index 1
          → left inorder=[15], right inorder=[7]
          → left preorder=[15], right preorder=[7]
          → recurse...

Final tree:
      3
     / \
    9  20
       / \
      15   7
```

### The Template (Optimized with Hashmap)

```python
def build_tree_preorder_inorder(preorder, inorder):
    """
    Build binary tree from preorder and inorder traversals.

    Naive approach: search for root in inorder each time = O(N^2)
    Optimized: precompute index of each value in inorder = O(N)
    """
    # Optimization: O(1) lookup for root's position in inorder
    inorder_index = {val: idx for idx, val in enumerate(inorder)}

    def build(pre_start, pre_end, in_start, in_end):
        """
        Build subtree from:
        - preorder[pre_start:pre_end]
        - inorder[in_start:in_end]
        """
        if pre_start >= pre_end:  # no nodes left
            return None

        # Root is always the first element of the current preorder slice
        root_val = preorder[pre_start]
        root = TreeNode(root_val)

        # Find root's position in inorder (splits left and right)
        root_inorder_idx = inorder_index[root_val]

        # How many nodes in the left subtree?
        left_size = root_inorder_idx - in_start

        # Recurse for left and right subtrees
        root.left = build(
            pre_start + 1,              # left preorder starts right after root
            pre_start + 1 + left_size,  # left preorder ends after left_size nodes
            in_start,                   # left inorder starts at in_start
            root_inorder_idx            # left inorder ends before root
        )

        root.right = build(
            pre_start + 1 + left_size,  # right preorder starts after left subtree
            pre_end,                    # right preorder ends at pre_end
            root_inorder_idx + 1,       # right inorder starts after root
            in_end                      # right inorder ends at in_end
        )

        return root

    return build(0, len(preorder), 0, len(inorder))
```

### Inorder + Postorder Variant

```python
def build_tree_postorder_inorder(inorder, postorder):
    """
    Build binary tree from inorder and postorder traversals.
    Same idea but root is LAST in postorder.
    """
    inorder_index = {val: idx for idx, val in enumerate(inorder)}

    def build(post_start, post_end, in_start, in_end):
        if post_start >= post_end:
            return None

        # Root is always the LAST element of the current postorder slice
        root_val = postorder[post_end - 1]
        root = TreeNode(root_val)

        root_inorder_idx = inorder_index[root_val]
        left_size = root_inorder_idx - in_start

        root.left = build(
            post_start,
            post_start + left_size,
            in_start,
            root_inorder_idx
        )

        root.right = build(
            post_start + left_size,
            post_end - 1,  # exclude the root we just used
            root_inorder_idx + 1,
            in_end
        )

        return root

    return build(0, len(postorder), 0, len(inorder))
```

### Sorted Array to Balanced BST

```python
def sorted_array_to_bst(nums):
    """
    Convert sorted array to height-balanced BST.

    Key: always pick the MIDDLE element as root.
    This guarantees left and right subtrees have equal (or ±1) nodes.
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

# Example: nums = [-10, -3, 0, 5, 9]
# Mid = index 2 = 0 → root
# Left: [-10, -3] → mid=index 0=-10 wait...
# build(0, 1): mid=0, root=-10? No...
# build(0, 4): mid=2 → root=0
#   build(0, 1): mid=0 → root=-10, right=build(1,1)=TreeNode(-3)
#   build(3, 4): mid=3 → root=5, right=build(4,4)=TreeNode(9)
#
#       0
#      / \
#   -10   5
#      \   \
#      -3   9
```

### Complexity
- **Time**: O(N) with hashmap optimization
- **Space**: O(N) for the hashmap + O(H) for recursion stack

### When NOT to Use This Pattern

- When you only have one traversal (impossible to uniquely reconstruct without inorder or structure)
- Note: preorder alone CAN reconstruct if you know it's a BST (since BST inorder is sorted)

---

## Pattern 5: Path Problems (Any Node to Any Node)

### The Story

Most tree problems ask about paths from the root. But "path sum" problems often allow paths to start and end ANYWHERE. This breaks the simple top-down model — you can't just track "how far from root I am."

The key insight that unlocks all these problems: **every path has a topmost node**. Even if the path is 4 → 2 → 5 (totally internal), node 2 is the topmost point. At node 2, the path "breaks" into two arms: one going left (to 4) and one going right (to 5).

So the trick is: at every node, ask "what is the best path that uses this node as the topmost point?" That's left_arm + node.val + right_arm.

### When to Use It

Use the path problem pattern when:
- Paths can start and end at any node
- You're computing something over all possible paths
- "any node to any node" appears in the problem

### Recognition Clues

- "maximum path sum" (especially if NOT restricted to root-to-leaf)
- "count paths with sum K" (any start, any end)
- "longest univalue path"
- "find the path with maximum sum" (in any direction)

### The Mental Model

```
At every node, there are multiple "path options":

        10
       /  \
      2    10
     / \     \
    20   1   -25
             /  \
            3    4

At node 10 (left child):
- Path using just this node: [2]
- Path going left: [20, 2]     ← left arm
- Path going right: [2, 1]     ← right arm
- Path going through (BOTH arms): [20, 2, 1]  ← this is the "complete" path
                                               ← CANNOT extend upward if both arms used

Key rule:
- When RETURNING to parent: return only ONE arm (left OR right), not both
- Why? If you extend with both arms, the path can't continue upward (it'd branch)
- When UPDATING ANSWER: consider both arms + current node
```

### The Template

```python
def max_path_sum(root):
    max_sum = [float('-inf')]

    def max_gain(node):
        """
        Returns the maximum gain this node can provide to its PARENT.
        (i.e., the best single-arm path through this node upward)
        """
        if not node:
            return 0

        # Get the best gain from each child
        # Use max(0, ...) because if child's contribution is negative,
        # we simply don't include that arm (it would hurt us)
        left_gain = max(0, max_gain(node.left))
        right_gain = max(0, max_gain(node.right))

        # What's the best path that has THIS node as the "peak"?
        # This path CAN include both arms (it won't be extended upward)
        path_through_here = node.val + left_gain + right_gain
        max_sum[0] = max(max_sum[0], path_through_here)

        # What we return to parent: this node's value + ONE best arm
        # (parent can only extend us in one direction)
        return node.val + max(left_gain, right_gain)

    max_gain(root)
    return max_sum[0]
```

### Full Worked Example

```
Tree:
     -10
     /  \
    9   20
        / \
       15   7

Trace max_gain():

max_gain(9):
  left_gain = max(0, max_gain(None)) = max(0, 0) = 0
  right_gain = max(0, max_gain(None)) = max(0, 0) = 0
  path_through = 9 + 0 + 0 = 9
  max_sum = max(-inf, 9) = 9
  return 9 + max(0, 0) = 9

max_gain(15):
  path_through = 15, max_sum = max(9, 15) = 15
  return 15

max_gain(7):
  path_through = 7, max_sum = max(15, 7) = 15
  return 7

max_gain(20):
  left_gain = max(0, 15) = 15
  right_gain = max(0, 7) = 7
  path_through = 20 + 15 + 7 = 42
  max_sum = max(15, 42) = 42  ← new best!
  return 20 + max(15, 7) = 20 + 15 = 35

max_gain(-10):
  left_gain = max(0, 9) = 9
  right_gain = max(0, 35) = 35
  path_through = -10 + 9 + 35 = 34
  max_sum = max(42, 34) = 42  (42 is still best)
  return -10 + max(9, 35) = -10 + 35 = 25

Final answer: 42  (path: 15 → 20 → 7)
```

### Count Paths with Sum K (Any Start, Any End)

This is a different flavor — counting paths (not maximizing), and paths must go downward but can start at any node.

```python
def path_sum_count(root, targetSum):
    """
    Count paths going downward (root-to-any, any-to-leaf, any-to-any downward)
    with sum = targetSum.

    Trick: prefix sums + hashmap
    At any node, prefix_sum = sum from root to here.
    If (prefix_sum - targetSum) was seen before, there's a valid path!
    """
    from collections import defaultdict

    count = [0]
    prefix_count = defaultdict(int)
    prefix_count[0] = 1  # empty path (sum=0) seen once

    def dfs(node, current_sum):
        if not node:
            return

        current_sum += node.val

        # How many paths ending here have sum = targetSum?
        count[0] += prefix_count[current_sum - targetSum]

        # Add current prefix sum to the map
        prefix_count[current_sum] += 1

        dfs(node.left, current_sum)
        dfs(node.right, current_sum)

        # Backtrack: remove current prefix sum (we're leaving this path)
        prefix_count[current_sum] -= 1

    dfs(root, 0)
    return count[0]
```

### Complexity
- **Time**: O(N) — every node visited once
- **Space**: O(H) for recursion stack (O(N) in worst case for skewed tree)

---

## Pattern 6: LCA — Lowest Common Ancestor

### The Story

Two cousins want to find their shared grandparent. Neither knows the full family tree — they just know their own ancestry. The LCA is the deepest ancestor that both share. Think of it like two GPS routes that diverge — the LCA is the last shared waypoint before the routes split apart.

### When to Use It

Use LCA when:
- Finding the common ancestor of two nodes
- Finding the distance between two nodes (dist = depth(p) + depth(q) - 2 * depth(LCA))
- Finding the path between two nodes (path = root-to-p + root-to-q, trimmed at LCA)
- Problems about "smallest subtree containing both nodes"

### Recognition Clues

- "lowest common ancestor"
- "find the ancestor shared by nodes p and q"
- "distance between two nodes in a tree"
- "path between two nodes"

### The Three Cases

```
Case 1: p is an ancestor of q (or vice versa)
        p is the LCA

    p               q is somewhere in p's subtree
   / \
  .   .
   \
    q

Case 2: p and q are in different subtrees of their LCA
        the LCA is "above" both

     LCA
    /   \
   .     .
  /       \
 p         q

Case 3: we're searching and neither target is in our subtree
        return None (not here)
```

### Template 1: General Tree LCA (Post-order DFS)

```python
def lowest_common_ancestor(root, p, q):
    """
    Post-order DFS: children are checked before the current node.

    Return semantics:
    - Return p if we find p
    - Return q if we find q
    - Return None if neither p nor q is in this subtree
    - Return the LCA if both p and q are in this subtree (one on each side)
    """
    # Base case: null node or we found one of our targets
    if not root or root == p or root == q:
        return root

    # Search in left and right subtrees
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)

    # Both sides found something → current node is LCA
    if left and right:
        return root

    # Only one side found something → propagate that finding upward
    return left if left else right


# Trace on this tree:
#       3
#      / \
#     5   1
#    / \ / \
#   6  2 0  8
#     / \
#    7   4
# Find LCA(5, 1):
#
# lca(3, 5, 1):
#   left = lca(5, 5, 1):
#     root==5 → return 5 immediately (don't recurse further!)
#   right = lca(1, 5, 1):
#     root==1 → return 1 immediately
#   left=5, right=1 → both non-null → return root=3
#
# LCA(5, 1) = 3  ✓
#
# Find LCA(5, 4):
# lca(3, 5, 4):
#   left = lca(5, 5, 4):
#     root==5 → return 5 immediately!
#     (yes, 4 is below 5, but we return 5 because 5 IS p)
#   right = lca(1, 5, 4):
#     lca(0, 5, 4) → None
#     lca(8, 5, 4) → None
#     → return None
#   left=5, right=None → return left=5
# LCA(5, 4) = 5  ✓ (5 is an ancestor of 4)
```

### Template 2: BST LCA (Much Simpler!)

In a BST, we can use value comparison to navigate:
- If both p and q are less than root → LCA is in left subtree
- If both p and q are greater than root → LCA is in right subtree
- If they're on different sides → current node IS the LCA

```python
def lca_bst(root, p, q):
    """
    BST LCA: use value comparison to navigate efficiently.
    No need to search blindly — we know which way to go.
    """
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left   # both targets are in left subtree
        elif p.val > root.val and q.val > root.val:
            root = root.right  # both targets are in right subtree
        else:
            return root  # they're on different sides, or one IS the root

    return None  # shouldn't reach here if p and q are in the tree

# This is O(H) time and O(1) space — no recursion needed!
```

### Finding Distance Between Two Nodes Using LCA

```python
def find_distance(root, p, q):
    """
    Distance between p and q = dist(root, p) + dist(root, q) - 2 * dist(root, LCA)
    Or equivalently: depth(p) - depth(LCA) + depth(q) - depth(LCA)
    """
    lca = lowest_common_ancestor(root, p, q)

    def depth_from(node, target, depth):
        if not node:
            return -1
        if node == target:
            return depth
        left = depth_from(node.left, target, depth + 1)
        if left != -1:
            return left
        return depth_from(node.right, target, depth + 1)

    d_p = depth_from(lca, p, 0)
    d_q = depth_from(lca, q, 0)

    return d_p + d_q
```

### Complexity
- **General LCA**: O(N) time, O(H) space
- **BST LCA**: O(H) time, O(1) space

---

## Pattern 7: Serialization / Encoding

### The Story

You need to send a tree across a network, or store it in a database. Trees aren't natively serializable — you need to convert them to a string or array, then rebuild them on the other end. The challenge: the encoding must be lossless (you can reconstruct the EXACT tree, not just any tree with the same values).

This pattern also powers "find duplicate subtrees" — you can encode each subtree as a string and check for duplicates using a hashmap.

### When to Use It

Use serialization when:
- You need to encode a tree as a string or array
- You need to find duplicate subtrees
- You need to store trees in a set/dict (trees aren't hashable natively)
- The problem asks "serialize and deserialize binary tree"

### Recognition Clues

- "serialize and deserialize"
- "find duplicate subtrees"
- "check if two trees are identical" (using encoding as hash)
- "encode the tree structure"

### The Key Insight

Preorder traversal with null markers uniquely identifies a tree. That's the key — if you include null markers (like "#" for empty), you can always reconstruct the exact tree.

```
Tree:
    1
   / \
  2   3
     / \
    4   5

Preorder with null markers:
1 → 2 → # → # → 3 → 4 → # → # → 5 → # → #

Reading back:
- Read 1: create node(1)
  - Read 2: create node(2), left child of 1
    - Read #: null left child of 2
    - Read #: null right child of 2
  - Read 3: create node(3), right child of 1
    - Read 4: create node(4), left child of 3
      - Read #: null left of 4
      - Read #: null right of 4
    - Read 5: create node(5), right child of 3
      - Read #: null left of 5
      - Read #: null right of 5
```

### Full Implementation: Serialize and Deserialize

```python
class Codec:

    def serialize(self, root):
        """
        Encode tree to string using preorder traversal.
        '#' represents null nodes.
        ',' is the delimiter.
        """
        def preorder(node):
            if not node:
                return '#'
            return str(node.val) + ',' + preorder(node.left) + ',' + preorder(node.right)

        return preorder(root)

    def deserialize(self, data):
        """
        Decode string back to tree.
        Use an iterator to consume tokens one by one.
        """
        tokens = iter(data.split(','))

        def build():
            token = next(tokens)
            if token == '#':
                return None

            node = TreeNode(int(token))
            node.left = build()    # consume left subtree tokens
            node.right = build()   # consume right subtree tokens
            return node

        return build()

# Example:
# codec = Codec()
# tree = build_tree([1, 2, 3, None, None, 4, 5])
# encoded = codec.serialize(tree)
# print(encoded)  → "1,2,#,#,3,4,#,#,5,#,#"
# decoded = codec.deserialize(encoded)
# → reconstructs the original tree
```

### Application: Find Duplicate Subtrees

```python
def find_duplicate_subtrees(root):
    """
    Find all duplicate subtrees.

    Strategy: encode each subtree as a string, track in a hashmap.
    If we've seen this encoding before, it's a duplicate.
    """
    from collections import defaultdict

    result = []
    subtree_count = defaultdict(int)

    def encode(node):
        if not node:
            return '#'

        # Postorder encoding: encode children first, then root
        left_code = encode(node.left)
        right_code = encode(node.right)

        code = f"{left_code},{right_code},{node.val}"

        subtree_count[code] += 1
        if subtree_count[code] == 2:  # first time we see a duplicate
            result.append(node)

        return code

    encode(root)
    return result
```

### Complexity
- **Serialize**: O(N) time, O(N) space for the string
- **Deserialize**: O(N) time
- **Duplicate subtrees**: O(N^2) time in worst case due to string concatenation (can optimize with integer IDs)

---

## Pattern 8: Morris Traversal (O(1) Space)

### The Story

Traditional inorder traversal uses O(H) space for the recursion stack, or O(N) for an explicit stack. But what if you have a strict O(1) space requirement? Morris traversal threads the tree temporarily — it borrows the null right pointers of nodes to create temporary "return paths," then cleans them up after use.

Think of it like leaving breadcrumbs in a maze. Before you go left, you leave a note on the rightmost node of your left subtree: "after visiting everything here, come back to me." Then you follow that breadcrumb back, erase it, and continue.

### When to Use It

Use Morris traversal when:
- O(1) extra space is required
- You need inorder traversal
- You cannot use recursion (no stack allowed)

### Recognition Clues

- "O(1) space"
- "without using extra space"
- "without recursion or stack"
- "constant space traversal"

### The Mental Model — Threading

```
Original tree:           After threading (temporarily):

    4                        4
   / \                      / \
  2   5          →         2   5
 / \                       / \
1   3                     1   3
                               \
                                4  ← thread (right pointer of inorder
                                      predecessor points back to 4)

When we reach 4 and see that 3's right already points to 4,
we know we've finished the left subtree. We unthread (remove the arrow)
and move to the right subtree (5).
```

### Full Implementation: Morris Inorder

```python
def morris_inorder(root):
    """
    Inorder traversal using O(1) space.

    Algorithm:
    1. If current has no left child: visit current, go right
    2. If current has left child:
       a. Find inorder predecessor (rightmost node in left subtree)
       b. If predecessor's right is None: thread it to current, go left
       c. If predecessor's right is current: unthread, visit current, go right
    """
    result = []
    current = root

    while current:
        if not current.left:
            # No left subtree — visit and move right
            result.append(current.val)
            current = current.right
        else:
            # Find inorder predecessor (rightmost node in left subtree)
            predecessor = current.left
            while predecessor.right and predecessor.right != current:
                predecessor = predecessor.right

            if not predecessor.right:
                # Thread: set predecessor's right to current (leave breadcrumb)
                predecessor.right = current
                current = current.left  # explore left subtree
            else:
                # Unthread: predecessor's right already points to current
                # → we've finished the left subtree
                predecessor.right = None  # remove the thread
                result.append(current.val)  # visit current
                current = current.right  # move to right subtree

    return result


# Trace on tree [4, 2, 5, 1, 3]:
#       4
#      / \
#     2   5
#    / \
#   1   3
#
# current=4, has left
#   predecessor = rightmost of left(2) = 3
#   3.right is None → thread: 3.right = 4, go left
#   current=2
# current=2, has left
#   predecessor = rightmost of left(1) = 1
#   1.right is None → thread: 1.right = 2, go left
#   current=1
# current=1, no left
#   visit 1, result=[1]
#   current = 1.right = 2 (thread!)
# current=2, has left
#   predecessor = rightmost of left(1) = 1
#   1.right == 2 → unthread: 1.right = None
#   visit 2, result=[1,2]
#   current = 2.right = 3
# current=3, no left
#   visit 3, result=[1,2,3]
#   current = 3.right = 4 (thread!)
# current=4, has left
#   predecessor = rightmost of left(2) = 3
#   3.right == 4 → unthread: 3.right = None
#   visit 4, result=[1,2,3,4]
#   current = 4.right = 5
# current=5, no left
#   visit 5, result=[1,2,3,4,5]
#   current = 5.right = None
# Done! result = [1,2,3,4,5]  ✓
```

### Complexity
- **Time**: O(N) — each edge traversed at most twice (once to thread, once to unthread)
- **Space**: O(1) — only a few pointers, no recursion stack

### When NOT to Use Morris Traversal

- When you need preorder or postorder (Morris can be adapted, but it's more complex)
- When code clarity matters more than space (Morris is harder to read and debug)
- When the tree is immutable (Morris temporarily modifies the tree)

---

## The Master Cheat Sheet

```
Problem says...                          →  Use this pattern
─────────────────────────────────────────────────────────────────
"root-to-leaf path with sum X"           →  Top-Down DFS (Pattern 1)
"paths that equal target from root"      →  Top-Down DFS (Pattern 1)
"height / depth"                         →  Bottom-Up DFS (Pattern 2)
"diameter"                               →  Bottom-Up DFS (Pattern 2)
"is balanced?"                           →  Bottom-Up DFS (Pattern 2)
"level order"                            →  BFS (Pattern 3)
"right side view"                        →  BFS (Pattern 3)
"cousins?"                               →  BFS (Pattern 3)
"minimum depth"                          →  BFS (Pattern 3)
"construct from preorder+inorder"        →  Tree Construction (Pattern 4)
"sorted array to BST"                    →  Tree Construction (Pattern 4)
"max path sum (any node to any node)"    →  Path Problems (Pattern 5)
"count paths with sum K"                 →  Path Problems (Pattern 5)
"lowest common ancestor"                 →  LCA (Pattern 6)
"distance between nodes"                 →  LCA (Pattern 6)
"serialize / deserialize"                →  Serialization (Pattern 7)
"find duplicate subtrees"                →  Serialization (Pattern 7)
"O(1) space traversal"                   →  Morris Traversal (Pattern 8)
─────────────────────────────────────────────────────────────────
```

---

## The Decision Tree (Meta-Pattern)

```
Is the problem about traversal order?
├── Yes: What order?
│   ├── Root first → Top-Down DFS
│   ├── Children first → Bottom-Up DFS
│   └── Level by level → BFS
│
Is the problem about building a tree?
└── Yes → Tree Construction
│
Does the path go through any node (not just from root)?
└── Yes → Path Problems (Pattern 5)
│
Are we finding a shared ancestor?
└── Yes → LCA (Pattern 6)
│
Are we encoding/decoding the tree?
└── Yes → Serialization (Pattern 7)
│
Is space constrained to O(1)?
└── Yes → Morris Traversal (Pattern 8)
```

---

## Common Mistakes and How to Avoid Them

### Mistake 1: Modifying the list before popping from it (in BFS)

```python
# WRONG: queue changes size as you process nodes
for node in queue:  # don't iterate directly
    ...

# RIGHT: snapshot the level size first
level_size = len(queue)
for _ in range(level_size):
    node = queue.popleft()
    ...
```

### Mistake 2: Forgetting to backtrack in top-down DFS

```python
# WRONG: path is never cleaned up
def dfs(node, path):
    path.append(node.val)
    dfs(node.left, path)
    dfs(node.right, path)
    # forgot: path.pop()

# RIGHT: always restore state after recursing
def dfs(node, path):
    path.append(node.val)
    dfs(node.left, path)
    dfs(node.right, path)
    path.pop()  # restore before returning to parent
```

### Mistake 3: Returning both arms in path problems

```python
# WRONG: you can't extend a path that branches both ways
def max_gain(node):
    left = max_gain(node.left)
    right = max_gain(node.right)
    return node.val + left + right  # WRONG! This forks the path

# RIGHT: return only ONE arm to parent, use BOTH arms for local answer
def max_gain(node):
    left = max(0, max_gain(node.left))
    right = max(0, max_gain(node.right))
    local_best = node.val + left + right  # both arms: local answer only
    update_global_max(local_best)
    return node.val + max(left, right)    # one arm: for parent to extend
```

### Mistake 4: LCA base case confusion

```python
# WRONG: continuing past a found node
if root == p:
    # still recurse to find q?? No!

# RIGHT: return immediately when found
if not root or root == p or root == q:
    return root  # if we find either target, return it — don't recurse further
```

---

## Practice Problem Mapping

| Problem | Pattern | Key Idea |
|---|---|---|
| Path Sum | Top-Down | Pass remaining sum downward |
| Path Sum II | Top-Down | Pass path list + backtrack |
| Sum Root to Leaf | Top-Down | Pass accumulated value |
| Binary Tree Height | Bottom-Up | Return height, combine |
| Diameter of Binary Tree | Bottom-Up | Track max(left+right) globally |
| Balanced Binary Tree | Bottom-Up | Return -1 sentinel if unbalanced |
| Max Path Sum | Bottom-Up + Path | Return one arm, update global |
| Level Order Traversal | BFS | Snapshot level size |
| Right Side View | BFS | Take last node per level |
| Zigzag Level Order | BFS | Reverse alternate levels |
| Connect Level Order | BFS | Link nodes at same level |
| Construct from Pre+In | Construction | Root is pre[0], split inorder |
| Sorted Array to BST | Construction | Always take midpoint |
| Lowest Common Ancestor | LCA | Post-order, bubble up |
| LCA of BST | LCA | Value comparison, iterative |
| Serialize/Deserialize | Serialization | Preorder + null markers |
| Find Duplicate Subtrees | Serialization | Encode subtrees, hash |
| Binary Tree Inorder O(1) | Morris | Thread/unthread right pointers |

---

## Final Thought

Here's the beautiful truth about tree problems: they all follow one of these eight patterns. Once you've internalized each pattern — not just memorized the code, but understood the *story* of information flowing up or down or across — you'll be able to look at any tree problem and know within 30 seconds which pattern applies.

The trees are all the same. It's the direction of information that changes everything.
