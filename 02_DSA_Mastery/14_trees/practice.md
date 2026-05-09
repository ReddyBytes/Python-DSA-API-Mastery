# Trees — Practice Questions

> 25 questions covering tree node definition, all traversals, BFS/DFS, height, path sums,
> LCA, serialization, tree construction, and common traps.
>
> Work through each question before opening the hint or answer.
> For coding questions: open `practice_local.py` and implement the stub, then compare.

---

## Quick Index

| # | Topic | Difficulty |
|---|-------|------------|
| [Q1](#q1) | TreeNode definition | Basic |
| [Q2](#q2) | Inorder traversal — recursive | Basic |
| [Q3](#q3) | Preorder traversal — recursive | Basic |
| [Q4](#q4) | Postorder traversal — recursive | Basic |
| [Q5](#q5) | Inorder traversal — iterative | Basic |
| [Q6](#q6) | Preorder traversal — iterative | Basic |
| [Q7](#q7) | Postorder traversal — iterative | Basic |
| [Q8](#q8) | Level-order traversal (BFS) | Basic |
| [Q9](#q9) | Tree height | Intermediate |
| [Q10](#q10) | Count nodes | Intermediate |
| [Q11](#q11) | Check symmetric tree | Intermediate |
| [Q12](#q12) | Check balanced tree | Intermediate |
| [Q13](#q13) | Lowest common ancestor | Intermediate |
| [Q14](#q14) | Path sum — root to leaf | Intermediate |
| [Q15](#q15) | All root-to-leaf paths with sum | Intermediate |
| [Q16](#q16) | DFS vs BFS — when to use each | Intermediate |
| [Q17](#q17) | When does inorder give sorted output? | Intermediate |
| [Q18](#q18) | Right side view | Intermediate |
| [Q19](#q19) | Minimum depth | Intermediate |
| [Q20](#q20) | Max path sum (any node to any node) | Advanced |
| [Q21](#q21) | Serialize a binary tree | Advanced |
| [Q22](#q22) | Deserialize a binary tree | Advanced |
| [Q23](#q23) | Build tree from preorder + inorder | Advanced |
| [Q24](#q24) | Build tree from inorder + postorder | Advanced |
| [Q25](#q25) | Which traversal pairs reconstruct a tree? | Advanced |

---

## Basic (Q1–Q8)

---

<a id="q1"></a>
### Q1 — Tree Node Definition

Write the Python `TreeNode` class used for binary trees. Then manually build this tree:

```
    1
   / \
  2   3
```

<details>
<summary>Hint</summary>

Each node needs a value, a left pointer, and a right pointer. All start as `None` by default.

</details>

<details>
<summary>Answer</summary>

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Build manually:
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
```

**Why:** Every tree algorithm depends on this definition. The `val=0, left=None, right=None` defaults let you construct nodes with just a value, keeping code concise.

**Time:** O(1) per node construction. **Space:** O(1) per node.

</details>

---

<a id="q2"></a>
### Q2 — Inorder Traversal Recursive

Implement recursive inorder traversal. Return a list of values.

```
Input:     1
          / \
         2   3
        / \
       4   5

Expected: [4, 2, 5, 1, 3]
```

<details>
<summary>Hint</summary>

Inorder = Left → Root → Right. Recurse left first, then append current node, then recurse right.

</details>

<details>
<summary>Answer</summary>

```python
def inorder(root):
    if not root:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)

# Or with explicit list (avoids list concatenation overhead):
def inorder_v2(root):
    result = []
    def dfs(node):
        if not node:
            return
        dfs(node.left)
        result.append(node.val)
        dfs(node.right)
    dfs(root)
    return result
```

**Why:** The order Left → Root → Right mirrors how you'd read a BST in sorted order. The helper-function version is preferred for large trees — it avoids creating a new list at every node.

**Time:** O(n). **Space:** O(h) call stack, where h = height.

</details>

---

<a id="q3"></a>
### Q3 — Preorder Traversal Recursive

Implement recursive preorder traversal. Return a list of values.

```
Input:     1
          / \
         2   3
        / \
       4   5

Expected: [1, 2, 4, 5, 3]
```

<details>
<summary>Hint</summary>

Preorder = Root → Left → Right. Process the current node before either child.

</details>

<details>
<summary>Answer</summary>

```python
def preorder(root):
    if not root:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)

def preorder_v2(root):
    result = []
    def dfs(node):
        if not node:
            return
        result.append(node.val)   # root first
        dfs(node.left)
        dfs(node.right)
    dfs(root)
    return result
```

**Why:** Preorder visits every node before its descendants. Classic uses: serialization (root first means easy reconstruction), copying a tree, generating a prefix expression from an AST.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q4"></a>
### Q4 — Postorder Traversal Recursive

Implement recursive postorder traversal. Return a list of values.

```
Input:     1
          / \
         2   3
        / \
       4   5

Expected: [4, 5, 2, 3, 1]
```

<details>
<summary>Hint</summary>

Postorder = Left → Right → Root. Children are fully processed before the parent.

</details>

<details>
<summary>Answer</summary>

```python
def postorder(root):
    if not root:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]

def postorder_v2(root):
    result = []
    def dfs(node):
        if not node:
            return
        dfs(node.left)
        dfs(node.right)
        result.append(node.val)   # root last
    dfs(root)
    return result
```

**Why:** Postorder is the natural order when you need a node's children to be complete before acting on the node — tree deletion, evaluating expression trees, computing height bottom-up.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q5"></a>
### Q5 — Inorder Traversal Iterative

Implement inorder traversal without recursion. Use an explicit stack.

<details>
<summary>Hint</summary>

Use a pointer `cur` that walks left, pushing nodes onto the stack. When you can't go left, pop, visit, then move right.

</details>

<details>
<summary>Answer</summary>

```python
def inorder_iterative(root):
    stack, result = [], []
    cur = root
    while cur or stack:
        while cur:              # go as far left as possible
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()       # leftmost unvisited node
        result.append(cur.val)  # visit it
        cur = cur.right         # now explore its right subtree
    return result
```

**Why:** The iterative version simulates exactly what the call stack does in the recursive version. It is crucial when the tree is so deep that recursion overflows the stack (Python default ~1000 frames).

**Time:** O(n). **Space:** O(h) for the stack.

</details>

---

<a id="q6"></a>
### Q6 — Preorder Traversal Iterative

Implement preorder traversal without recursion.

<details>
<summary>Hint</summary>

Push root onto the stack. Each iteration: pop, visit, push right child then left child (right first because stack is LIFO — left gets processed first).

</details>

<details>
<summary>Answer</summary>

```python
def preorder_iterative(root):
    if not root:
        return []
    stack, result = [root], []
    while stack:
        node = stack.pop()
        result.append(node.val)
        if node.right:
            stack.append(node.right)   # push right first
        if node.left:
            stack.append(node.left)    # push left second (processed first)
    return result
```

**Why:** By pushing right before left, the stack ensures left is popped first — matching the Root → Left → Right order. The key insight is that LIFO reverses the push order.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q7"></a>
### Q7 — Postorder Traversal Iterative

Implement postorder traversal without recursion.

<details>
<summary>Hint</summary>

Generate "reversed preorder" (Root → Right → Left) by using a stack that processes right before left, then reverse the entire result at the end.

</details>

<details>
<summary>Answer</summary>

```python
def postorder_iterative(root):
    if not root:
        return []
    stack, result = [root], []
    while stack:
        node = stack.pop()
        result.append(node.val)
        if node.left:
            stack.append(node.left)    # push left first (processed second = right first)
        if node.right:
            stack.append(node.right)
    return result[::-1]                # reverse: Root→R→L becomes L→R→Root
```

**Why:** Postorder iteratively is tricky; the reversed-preorder trick is the cleanest approach. The final `[::-1]` converts Root→Right→Left into Left→Right→Root (postorder). Alternatively, use two stacks.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q8"></a>
### Q8 — Level-Order Traversal (BFS)

Implement level-order traversal. Return a list of lists — one sublist per level.

```
Input:     1
          / \
         2   3
        / \
       4   5

Expected: [[1], [2, 3], [4, 5]]
```

<details>
<summary>Hint</summary>

Use a `deque`. Before processing a level, snapshot `len(queue)` — that tells you exactly how many nodes belong to the current level.

</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)     # snapshot: nodes at this level
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
```

**Why:** The `level_size = len(queue)` snapshot is the key — it separates the current level from the next before we start adding children. Without it, you can't tell where one level ends and the next begins.

**Time:** O(n). **Space:** O(w) where w = max width (up to O(n) for a complete binary tree's bottom level).

</details>

---

## Intermediate (Q9–Q19)

---

<a id="q9"></a>
### Q9 — Tree Height

Implement `max_depth(root)` — return the number of nodes on the longest root-to-leaf path (height in nodes, not edges).

```
Input:     1
          / \
         2   3
        /
       4

Expected: 3
```

<details>
<summary>Hint</summary>

At each node: height = 1 + max(height of left subtree, height of right subtree). Base case: null node has height 0.

</details>

<details>
<summary>Answer</summary>

```python
def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

**Why:** This is the canonical bottom-up pattern. Each leaf returns 1 to its parent. Each internal node adds 1 and takes the max of both subtrees. The root receives the total height.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q10"></a>
### Q10 — Count Nodes

Implement `count_nodes(root)` — return the total number of nodes in the tree.

<details>
<summary>Hint</summary>

At each node, the count is 1 (itself) + count of left subtree + count of right subtree. Base case: null node = 0.

</details>

<details>
<summary>Answer</summary>

```python
def count_nodes(root):
    if not root:
        return 0
    return 1 + count_nodes(root.left) + count_nodes(root.right)
```

**Why:** Every node contributes exactly 1 to the count. The recursion naturally accumulates all 1s from leaves up to the root. For a complete binary tree you can optimize to O(log²n) using the structure, but O(n) works for any binary tree.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q11"></a>
### Q11 — Check Symmetric Tree

A tree is symmetric if it is a mirror of itself around the root (left subtree is a mirror of the right subtree).

```
Symmetric:      Not Symmetric:
    1                1
   / \              / \
  2   2            2   2
 / \ / \            \   \
3  4 4  3            3   3
```

<details>
<summary>Hint</summary>

Define a helper `is_mirror(left, right)`. Two nodes are mirrors if their values match AND left.left mirrors right.right AND left.right mirrors right.left.

</details>

<details>
<summary>Answer</summary>

```python
def is_symmetric(root):
    def is_mirror(left, right):
        if not left and not right:
            return True                       # both None: symmetric
        if not left or not right:
            return False                      # one None, one not: asymmetric
        return (left.val == right.val and
                is_mirror(left.left, right.right) and   # outer pair
                is_mirror(left.right, right.left))      # inner pair
    return is_mirror(root.left, root.right)
```

**Why:** The mirror check compares "outer" pairs (left.left vs right.right) and "inner" pairs (left.right vs right.left). This exactly captures the definition of a mirror image. The two-pointer approach compares nodes at symmetric positions.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q12"></a>
### Q12 — Check Balanced Tree

A height-balanced binary tree is one where the height difference between left and right subtrees is at most 1 at every node.

<details>
<summary>Hint</summary>

Use a single post-order pass. Return -1 as a sentinel if any subtree is unbalanced. Otherwise return the height. Check both `l == -1` and `r == -1` before computing the difference.

</details>

<details>
<summary>Answer</summary>

```python
def is_balanced(root):
    def check(node):
        if not node:
            return 0
        l = check(node.left)
        if l == -1:
            return -1                         # imbalance found below
        r = check(node.right)
        if r == -1:
            return -1                         # imbalance found below
        if abs(l - r) > 1:
            return -1                         # THIS node is unbalanced
        return 1 + max(l, r)
    return check(root) != -1
```

**Why:** The naive O(n²) approach recomputes height from scratch at every node. The -1 sentinel trick allows a single O(n) pass: once an imbalance is detected, it propagates upward immediately without wasted work.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q13"></a>
### Q13 — Lowest Common Ancestor

Given a binary tree and two nodes `p` and `q`, find their lowest common ancestor (LCA). The LCA is the deepest node that has both p and q as descendants (a node is considered a descendant of itself).

```
        3
       / \
      5   1
     / \ / \
    6  2 0  8
      / \
     7   4

LCA(5, 1) = 3
LCA(5, 4) = 5   ← 5 is an ancestor of 4
LCA(6, 4) = 5
```

<details>
<summary>Hint</summary>

Post-order DFS. If the current node equals p or q, return it immediately. If both left and right return non-null, the current node is the LCA. Otherwise bubble up whichever side found something.

</details>

<details>
<summary>Answer</summary>

```python
def lowest_common_ancestor(root, p, q):
    if not root or root == p or root == q:
        return root                           # found a target (or fell off tree)
    left  = lowest_common_ancestor(root.left,  p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:
        return root                           # p on one side, q on the other
    return left or right                      # both in same subtree
```

**Why:** When `root == p`, we return immediately — even if q is below p, p IS the LCA (a node is a descendant of itself). When both sides return non-null, the current node is exactly where the two paths diverge: it is the LCA.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q14"></a>
### Q14 — Path Sum (Root to Leaf)

Given a root and a target sum, return `True` if any root-to-leaf path has node values that sum to `target`.

```
target = 22
      5
     / \
    4   8
   /   / \
  11  13   4
 /  \       \
7    2       1

Answer: True  (path 5→4→11→2 = 22)
```

<details>
<summary>Hint</summary>

Subtract the current node's value from the target as you go down. At a leaf, check if the remaining target equals zero.

</details>

<details>
<summary>Answer</summary>

```python
def has_path_sum(root, target):
    if not root:
        return False
    if not root.left and not root.right:      # leaf
        return root.val == target
    return (has_path_sum(root.left,  target - root.val) or
            has_path_sum(root.right, target - root.val))
```

**Why:** Subtracting the node value as we descend means at the leaf we only need to check if `val == target` (the remainder). The `or` short-circuits: if the left path finds a solution, we don't explore the right. Critically, the leaf check requires BOTH children to be None — a node with one child is NOT a leaf.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q15"></a>
### Q15 — All Root-to-Leaf Paths With Sum

Return all root-to-leaf paths whose node values sum to `target`.

<details>
<summary>Hint</summary>

Top-down DFS. Carry the current path as a list. At each leaf where remaining == 0, append a copy of the path. After recursing, pop the last element (backtrack).

</details>

<details>
<summary>Answer</summary>

```python
def path_sum_all(root, target):
    result = []
    def dfs(node, remaining, path):
        if not node:
            return
        path.append(node.val)
        if not node.left and not node.right and remaining == node.val:
            result.append(list(path))         # copy: path is mutable
        dfs(node.left,  remaining - node.val, path)
        dfs(node.right, remaining - node.val, path)
        path.pop()                            # backtrack
    dfs(root, target, [])
    return result
```

**Why:** The `list(path)` copy is critical — without it, all entries in `result` would point to the same (now-empty) list after backtracking. The `path.pop()` after both recursive calls restores the path to its state before we entered this node.

**Time:** O(n). **Space:** O(h) stack + O(n) for storing all paths in the worst case.

</details>

---

<a id="q16"></a>
### Q16 — DFS vs BFS on Trees: When to Use Each

Explain when you would choose DFS over BFS for a tree problem, and vice versa. Give a concrete example for each.

<details>
<summary>Hint</summary>

Think about what information each traversal naturally produces. DFS digs deep on one path; BFS processes all nodes at the same depth before going deeper.

</details>

<details>
<summary>Answer</summary>

**Use DFS when:**
- The answer depends on the path from root to a node (path sums, root-to-leaf paths)
- You need to combine results from both subtrees at each node (height, diameter, LCA)
- You're searching for a single target (stop early once found)
- Space matters: DFS uses O(h) while BFS uses O(w) — for tall narrow trees, DFS wins

**Example:** Find if a path from root to leaf sums to target — you must track the accumulated sum along a single path, which is exactly what top-down DFS carries via parameters.

**Use BFS when:**
- The problem involves levels or depth (right-side view, zigzag, connect level nodes)
- You want the MINIMUM depth or nearest node — BFS finds the first leaf it hits
- The problem asks "cousins" or "nodes at same depth"
- You need nodes in document order (left-to-right, top-to-bottom)

**Example:** Right side view — take the last node at each level. BFS naturally groups nodes by level, so you just save the last value in each round.

**Space trade-off:**
- DFS: O(h) stack — great for tall skewed trees if you only need one path
- BFS: O(w) queue — great for wide shallow trees; worst case O(n) for the bottom level of a complete binary tree

</details>

---

<a id="q17"></a>
### Q17 — When Does Inorder Give Sorted Output?

True or False: inorder traversal of ANY binary tree gives a sorted result.

If False, correct the statement and explain why the misconception is dangerous in interviews.

<details>
<summary>Hint</summary>

Inorder gives sorted output only when a specific structural property holds about the tree's node values.

</details>

<details>
<summary>Answer</summary>

**False.** Inorder traversal of a **Binary Search Tree (BST)** gives sorted output. It does NOT for a general binary tree.

**Correct statement:** Inorder traversal of a BST gives values in non-decreasing order because the BST property guarantees all left-subtree values are smaller than the root, which is smaller than all right-subtree values.

**Counter-example — general binary tree:**
```
    3
   / \
  5   1
```
Inorder: [5, 3, 1] — NOT sorted.

**Why this is dangerous in interviews:**
- If you assume inorder = sorted on a general tree, you might incorrectly validate a BST or use inorder to sort an arbitrary tree.
- The correct use: use inorder to VERIFY a BST (the output should be strictly increasing). Do not use inorder to sort values in a general tree.

**Key rule:** Inorder → sorted output if and only if the tree is a valid BST.

</details>

---

<a id="q18"></a>
### Q18 — Right Side View

Given a binary tree, return the values of nodes you can see from the right side, ordered top to bottom.

```
Input:     1
          / \
         2   3
          \   \
           5   4

Output: [1, 3, 4]
```

<details>
<summary>Hint</summary>

BFS level-order. At each level, the rightmost node is the last one in the level — capture it.

</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

def right_side_view(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:           # last node at this level
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return result
```

**Why:** BFS naturally processes nodes level by level. The last node popped at each level is the rightmost visible node. Alternative: DFS visiting right before left and tracking depth, but BFS is more direct and readable.

**Time:** O(n). **Space:** O(w) — max queue size equals widest level.

</details>

---

<a id="q19"></a>
### Q19 — Minimum Depth

Return the minimum depth of the tree — the number of nodes on the shortest path from root to a leaf.

```
Input:    1
           \
            2

Expected: 2 — NOT 1 (node 1 is not a leaf; it has a right child)
```

<details>
<summary>Hint</summary>

A leaf has BOTH children as None. A node with only one child is NOT a leaf — the minimum depth must pass through that one child.

</details>

<details>
<summary>Answer</summary>

```python
def min_depth(root):
    if not root:
        return 0
    if not root.left:
        return 1 + min_depth(root.right)   # must go right (no leaf via left)
    if not root.right:
        return 1 + min_depth(root.left)    # must go left (no leaf via right)
    return 1 + min(min_depth(root.left), min_depth(root.right))

# BFS alternative — cleaner, finds first leaf naturally:
from collections import deque

def min_depth_bfs(root):
    if not root:
        return 0
    queue = deque([(root, 1)])
    while queue:
        node, depth = queue.popleft()
        if not node.left and not node.right:  # first leaf in BFS = minimum depth
            return depth
        if node.left:
            queue.append((node.left, depth + 1))
        if node.right:
            queue.append((node.right, depth + 1))
```

**Why:** The one-child case is the classic trap. If a node has only a right child, the left subtree has no leaves — taking `min(0, right_depth)` would incorrectly return 0+1=1, treating the non-leaf as a leaf. BFS is actually cleaner here: the first leaf it encounters is guaranteed to be at minimum depth.

**Time:** O(n). **Space:** O(h) for DFS, O(w) for BFS.

</details>

---

## Advanced (Q20–Q25)

---

<a id="q20"></a>
### Q20 — Max Path Sum (Any Node to Any Node)

Find the maximum path sum where the path can start and end at any node. Node values may be negative.

```
Input:    -10
          /  \
         9   20
             / \
            15   7

Output: 42   (path: 15 → 20 → 7)
```

<details>
<summary>Hint</summary>

At each node, the maximum "bent" path through it = left_gain + node.val + right_gain, where gain = max(0, subtree_gain) to exclude negative branches. The function returns only a single-branch gain to the parent (it can't extend a bent path further up).

</details>

<details>
<summary>Answer</summary>

```python
def max_path_sum(root):
    max_sum = [float('-inf')]

    def gain(node):
        if not node:
            return 0
        left_gain  = max(0, gain(node.left))    # drop branch if negative
        right_gain = max(0, gain(node.right))   # drop branch if negative
        path_through = node.val + left_gain + right_gain
        max_sum[0] = max(max_sum[0], path_through)   # update global max
        return node.val + max(left_gain, right_gain) # return ONE arm to parent

    gain(root)
    return max_sum[0]
```

**Why:** Two things happen at every node: (1) we compute the best "bent" path through this node and update the global maximum — this path cannot be extended upward. (2) We return the best "straight" path (one arm) so the parent can extend it. The `max(0, ...)` is critical: it means we never include a subtree that makes the sum worse.

**Time:** O(n). **Space:** O(h).

</details>

---

<a id="q21"></a>
### Q21 — Serialize a Binary Tree

Convert a binary tree into a string that uniquely encodes its structure. Null nodes must be represented.

<details>
<summary>Hint</summary>

Preorder DFS with a null marker (e.g., 'N'). Delimit values with commas. The null markers are what make the encoding unique — without them, different trees can produce the same value sequence.

</details>

<details>
<summary>Answer</summary>

```python
def serialize(root):
    vals = []
    def dfs(node):
        if not node:
            vals.append('N')            # null marker preserves structure
            return
        vals.append(str(node.val))
        dfs(node.left)
        dfs(node.right)
    dfs(root)
    return ','.join(vals)

# Example:
#     1
#    / \
#   2   3
# → "1,2,N,N,3,N,N"
```

**Why:** Without null markers, "1,2,3" is ambiguous — it could represent many different tree shapes. The null markers uniquely pin down where each subtree ends. Preorder is chosen because the root comes first, making deserialization straightforward: read the root, then recursively build left, then right.

**Time:** O(n). **Space:** O(n) for the output string.

</details>

---

<a id="q22"></a>
### Q22 — Deserialize a Binary Tree

Given the string produced by Q21's serialize function, reconstruct the exact original tree.

<details>
<summary>Hint</summary>

Split on the delimiter to get a list of tokens. Use `iter()` to consume tokens one at a time. When you read 'N', return None. Otherwise create a node and recursively build left then right.

</details>

<details>
<summary>Answer</summary>

```python
def deserialize(data):
    tokens = iter(data.split(','))

    def build():
        val = next(tokens)
        if val == 'N':
            return None
        node = TreeNode(int(val))
        node.left  = build()     # consume left subtree tokens in order
        node.right = build()     # consume right subtree tokens in order
        return node

    return build()
```

**Why:** Using `iter()` + `next()` maintains a shared cursor across all recursive calls — each call advances the same iterator, so tokens are consumed in exactly the preorder sequence they were written. This avoids passing index variables through the recursion.

**Time:** O(n). **Space:** O(h) call stack.

</details>

---

<a id="q23"></a>
### Q23 — Build Tree From Preorder + Inorder

Given preorder and inorder traversal arrays, reconstruct the binary tree.

```
preorder = [3, 9, 20, 15, 7]
inorder  = [9, 3, 15, 20, 7]

Output:
    3
   / \
  9  20
     / \
    15   7
```

<details>
<summary>Hint</summary>

Root = preorder[0]. Find root in inorder — everything to its left is the left subtree, everything to its right is the right subtree. Use a hashmap for O(1) inorder index lookup.

</details>

<details>
<summary>Answer</summary>

```python
def build_tree_pre_in(preorder, inorder):
    index_map = {val: i for i, val in enumerate(inorder)}  # O(1) lookup

    def build(pre_l, pre_r, in_l, in_r):
        if pre_l > pre_r:
            return None
        root_val = preorder[pre_l]
        root = TreeNode(root_val)
        mid = index_map[root_val]           # root's position in inorder
        left_size = mid - in_l
        root.left  = build(pre_l + 1, pre_l + left_size, in_l, mid - 1)
        root.right = build(pre_l + left_size + 1, pre_r, mid + 1, in_r)
        return root

    return build(0, len(preorder) - 1, 0, len(inorder) - 1)
```

**Why:** The inorder array splits into left/right subtrees around the root. `left_size = mid - in_l` tells us exactly how many preorder elements belong to the left subtree. The hashmap avoids an O(n) search at every node, reducing overall complexity from O(n²) to O(n).

**Time:** O(n). **Space:** O(n) hashmap + O(h) call stack.

</details>

---

<a id="q24"></a>
### Q24 — Build Tree From Inorder + Postorder

Given inorder and postorder traversal arrays, reconstruct the binary tree.

```
inorder   = [9, 3, 15, 20, 7]
postorder = [9, 15, 7, 20, 3]

Same tree as Q23.
```

<details>
<summary>Hint</summary>

Root = postorder[-1] (last element). Same splitting logic as Q23, but consume from the end of the postorder array.

</details>

<details>
<summary>Answer</summary>

```python
def build_tree_in_post(inorder, postorder):
    index_map = {val: i for i, val in enumerate(inorder)}

    def build(post_l, post_r, in_l, in_r):
        if post_l > post_r:
            return None
        root_val = postorder[post_r]        # root is LAST in postorder
        root = TreeNode(root_val)
        mid = index_map[root_val]
        left_size = mid - in_l
        root.left  = build(post_l, post_l + left_size - 1, in_l, mid - 1)
        root.right = build(post_l + left_size, post_r - 1, mid + 1, in_r)
        return root

    return build(0, len(postorder) - 1, 0, len(inorder) - 1)
```

**Why:** The same inorder-split logic applies. The only change is that the root comes from the end of postorder (not the start of preorder). Inorder is always the key — it is the only traversal that cleanly separates left and right subtrees.

**Time:** O(n). **Space:** O(n) hashmap + O(h) call stack.

</details>

---

<a id="q25"></a>
### Q25 — Which Traversal Pairs Can Uniquely Reconstruct a Tree?

Three traversals exist: preorder, inorder, postorder. Which pairs can uniquely reconstruct a binary tree? Which cannot?

<details>
<summary>Hint</summary>

The critical question is: which traversal uniquely identifies the left/right split at each node?

</details>

<details>
<summary>Answer</summary>

**Pairs that CAN uniquely reconstruct:**
- Preorder + Inorder → unique tree
- Postorder + Inorder → unique tree

**Pair that CANNOT uniquely reconstruct (in general):**
- Preorder + Postorder → NOT unique

**Why inorder is essential:**
Inorder traversal is the only one that places the root between its left and right subtrees. Given the root's value (from preorder[0] or postorder[-1]), inorder tells you exactly which nodes belong to the left subtree vs the right subtree.

Without inorder, you cannot determine this split. Example where preorder + postorder fails:

```
Preorder = [1, 2]     can represent:
Postorder = [2, 1]

Tree A:    1        Tree B:    1
            \                 /
             2               2

Both produce the same preorder [1,2] and postorder [2,1].
They are different trees — impossible to distinguish.
```

**Exception:** Preorder + Postorder CAN reconstruct a tree uniquely if the tree is a FULL binary tree (every internal node has exactly 2 children, never 1). In that case there is no ambiguity about which side a single child falls on.

</details>

---

## Navigation

**[Back to README](../README.md)**

**Prev:** [Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Binary Search Trees — Theory](../15_binary_search_trees/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
