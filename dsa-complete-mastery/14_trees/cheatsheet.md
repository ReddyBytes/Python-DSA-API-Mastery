# Trees — Cheatsheet

---

## Terminology Quick Reference

```
              1           ← root (depth 0, level 1)
            /   \
           2     3        ← internal nodes (depth 1)
          / \     \
         4   5     6      ← leaves (depth 2)

height of tree     = 2   (longest path from root to leaf)
depth of node 5    = 2   (edges from root to node)
diameter           = 4   (longest path: 4→2→1→3→6, passes through root)
balanced           = |height(left) - height(right)| <= 1 at every node
```

| Term      | Definition                                              |
|-----------|---------------------------------------------------------|
| Root      | Top node, no parent                                     |
| Leaf      | Node with no children                                   |
| Height    | Edges on longest path from node to a leaf               |
| Depth     | Edges from root to this node                            |
| Diameter  | Longest path between any two nodes (may not pass root)  |
| Subtree   | Node and all its descendants                            |
| Ancestor  | Any node on path from root to this node                 |
| LCA       | Deepest node that is ancestor of both target nodes      |

---

## Python TreeNode Definition

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Build small tree manually
#       1
#      / \
#     2   3
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
```

---

## Traversal Comparison Table

| Traversal  | Order               | Use Case                              | Result on example  |
|------------|---------------------|---------------------------------------|--------------------|
| Preorder   | root, left, right   | Copy tree, serialize, prefix expr     | 1 2 4 5 3 6        |
| Inorder    | left, root, right   | BST → sorted order                    | 4 2 5 1 3 6        |
| Postorder  | left, right, root   | Delete tree, evaluate expr, height    | 4 5 2 6 3 1        |
| Level-order| level by level      | Shortest path, level properties       | 1 / 2 3 / 4 5 6    |

---

## Traversal Templates — Recursive

```python
def preorder(root):
    if not root: return []
    return [root.val] + preorder(root.left) + preorder(root.right)

def inorder(root):
    if not root: return []
    return inorder(root.left) + [root.val] + inorder(root.right)

def postorder(root):
    if not root: return []
    return postorder(root.left) + postorder(root.right) + [root.val]
```

---

## Traversal Templates — Iterative

### Iterative Inorder (Stack)

```python
def inorder_iter(root):
    stack, res = [], []
    cur = root
    while cur or stack:
        while cur:                      # go as far left as possible
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()               # process node
        res.append(cur.val)
        cur = cur.right                 # move to right subtree
    return res
```

### Iterative Preorder (Stack)

```python
def preorder_iter(root):
    if not root: return []
    stack, res = [root], []
    while stack:
        node = stack.pop()
        res.append(node.val)
        if node.right: stack.append(node.right)   # right first (LIFO)
        if node.left:  stack.append(node.left)
    return res
```

### Iterative Postorder (Two Stacks / Reversed Preorder)

```python
def postorder_iter(root):
    if not root: return []
    stack, res = [root], []
    while stack:
        node = stack.pop()
        res.append(node.val)
        if node.left:  stack.append(node.left)    # left first (reversed)
        if node.right: stack.append(node.right)
    return res[::-1]                              # reverse at end
```

---

## Level-Order (BFS) Template

```python
from collections import deque

def level_order(root):
    if not root: return []
    q = deque([root])
    res = []
    while q:
        level = []
        for _ in range(len(q)):         # process entire level
            node = q.popleft()
            level.append(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        res.append(level)
    return res
# Returns [[1], [2,3], [4,5,6]] — list of levels
```

---

## Common Tree Patterns

### Max Depth

```python
def max_depth(root):
    if not root: return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

### Min Depth

```python
def min_depth(root):
    if not root: return 0
    if not root.left:  return 1 + min_depth(root.right)   # not a leaf
    if not root.right: return 1 + min_depth(root.left)    # not a leaf
    return 1 + min(min_depth(root.left), min_depth(root.right))
# Gotcha: min_depth(None) for one-sided nodes must not count as leaf path
```

### Diameter of Tree

```python
def diameter(root):
    res = [0]
    def depth(node):
        if not node: return 0
        l = depth(node.left)
        r = depth(node.right)
        res[0] = max(res[0], l + r)    # path through this node
        return 1 + max(l, r)           # height going up
    depth(root)
    return res[0]
```

### Check Balanced (Height-Balanced)

```python
def is_balanced(root):
    def check(node):
        if not node: return 0
        l = check(node.left)
        r = check(node.right)
        if l == -1 or r == -1: return -1    # already unbalanced
        if abs(l - r) > 1:    return -1    # this node unbalanced
        return 1 + max(l, r)
    return check(root) != -1
```

### Lowest Common Ancestor (General Tree)

```python
def lca(root, p, q):
    if not root or root == p or root == q:
        return root                     # base: found one of targets (or None)
    left  = lca(root.left,  p, q)
    right = lca(root.right, p, q)
    if left and right:
        return root                     # p in left subtree, q in right
    return left or right                # both in same subtree
```

### Path Sum (Root to Leaf)

```python
def has_path_sum(root, target):
    if not root: return False
    if not root.left and not root.right:    # leaf
        return root.val == target
    return (has_path_sum(root.left,  target - root.val) or
            has_path_sum(root.right, target - root.val))
```

### All Root-to-Leaf Paths

```python
def path_sum_all(root, target):
    res = []
    def dfs(node, remaining, path):
        if not node: return
        path.append(node.val)
        if not node.left and not node.right and remaining == node.val:
            res.append(list(path))
        dfs(node.left,  remaining - node.val, path)
        dfs(node.right, remaining - node.val, path)
        path.pop()                      # backtrack
    dfs(root, target, [])
    return res
```

### Max Path Sum (Any Node to Any Node)

```python
def max_path_sum(root):
    res = [float('-inf')]
    def gain(node):
        if not node: return 0
        l = max(gain(node.left),  0)   # ignore negative subtrees
        r = max(gain(node.right), 0)
        res[0] = max(res[0], node.val + l + r)   # path through node
        return node.val + max(l, r)              # return single-branch gain
    gain(root)
    return res[0]
```

---

## Serialize / Deserialize Tree

```python
# Preorder with None markers
def serialize(root):
    res = []
    def dfs(node):
        if not node:
            res.append('N')
            return
        res.append(str(node.val))
        dfs(node.left)
        dfs(node.right)
    dfs(root)
    return ','.join(res)

def deserialize(data):
    vals = iter(data.split(','))
    def dfs():
        v = next(vals)
        if v == 'N': return None
        node = TreeNode(int(v))
        node.left  = dfs()
        node.right = dfs()
        return node
    return dfs()
```

---

## Tree Construction from Traversals

```
Need exactly 2 traversals to reconstruct (one must be inorder).

Preorder + Inorder  → unique tree
Postorder + Inorder → unique tree
Preorder + Postorder → NOT unique (unless full binary tree)
```

```python
def build_from_preorder_inorder(preorder, inorder):
    if not preorder: return None
    root_val = preorder[0]
    root = TreeNode(root_val)
    mid = inorder.index(root_val)       # split inorder
    root.left  = build_from_preorder_inorder(preorder[1:mid+1], inorder[:mid])
    root.right = build_from_preorder_inorder(preorder[mid+1:],  inorder[mid+1:])
    return root
# Optimize: use hash map for inorder index lookup → O(n) instead of O(n²)
```

---

## Interview Signals

```
"if it were a BST..."           → inorder traversal gives sorted order
"top-down"                      → pass information from root to leaves (DFS with params)
"bottom-up"                     → compute at leaves, return to parent (DFS with return value)
"level by level"                → BFS (deque)
"path from root"                → DFS with running sum/path
"any node to any node path"     → postorder — collect max from both sides
"symmetric / mirror"            → check left.left==right.right and left.right==right.left
"right side view"               → BFS, take last node per level
"zigzag level order"            → BFS, alternate append direction
```

---

## Top-Down vs Bottom-Up

```
Top-Down (like preorder):              Bottom-Up (like postorder):
- Pass data as parameters              - Return data from children
- Make decisions at current node       - Make decisions after children return
- Good for: path tracking              - Good for: height, diameter, balance

def top_down(node, acc):               def bottom_up(node):
    if not node: return                    if not node: return 0
    acc += node.val                        l = bottom_up(node.left)
    top_down(node.left, acc)               r = bottom_up(node.right)
    top_down(node.right, acc)              # use l, r to compute answer
```

---

## Complexity Reference

| Operation              | Time       | Space         |
|------------------------|------------|---------------|
| DFS traversal          | O(n)       | O(h) stack    |
| BFS traversal          | O(n)       | O(w) queue    |
| Max/Min depth          | O(n)       | O(h)          |
| LCA                    | O(n)       | O(h)          |
| h = height, w = max level width, worst case h=n (skewed), balanced h=log n |
