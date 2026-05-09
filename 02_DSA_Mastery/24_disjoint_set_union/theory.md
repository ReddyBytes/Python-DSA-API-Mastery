<a id="top"></a>
# Disjoint Set Union (Union-Find) — Managing Connected Groups Efficiently

> Imagine you have many people.
> Some of them are friends.
>
> Over time, friendships form.
>
> You want to quickly answer:
>
> "Are these two people connected?"

You don't want to search the entire network every time.

Disjoint Set Union solves this efficiently.

## 📖 Table of Contents

1. [Real Life Story — Friend Circles](#1-real-life-story)
2. [The Problem Without DSU](#2-the-problem-without-dsu)
3. [Core Idea](#3-core-idea)
4. [Initial Setup](#4-initial-setup)
5. [Find Operation](#5-find-operation)
6. [Union Operation](#6-union-operation)
7. [Path Compression (Very Important)](#7-path-compression)
8. [Union by Rank / Size](#8-union-by-rank-size)
9. [Time Complexity](#9-time-complexity)
10. [Why DSU Is Better Than DFS Here](#10-why-dsu-is-better-than-dfs)
11. [Common Use Cases](#11-common-use-cases)
12. [Real-World Applications](#12-real-world-applications)
13. [Mental Model](#13-mental-model)
14. [Final Understanding](#14-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
find operation · union operation · path compression

**Should Learn** — Important for real projects, comes up regularly:
union by rank/size · cycle detection in graphs · Kruskal's MST application

**Good to Know** — Useful in specific situations, not always tested:
connected components use case · time complexity (inverse Ackermann)

**Reference** — Know it exists, look up syntax when needed:
weighted DSU · DSU with rollback · persistent DSU · bipartite checking

> 📝 **Practice:** [Q52 · union-find](../dsa_practice_questions_100.md#q52--thinking--union-find)

<a id="1-real-life-story"></a>
# 1. Real Life Story — Friend Circles

First day of high school. Eight students arrive: 1, 2, 3, 4, 5, 6, 7, 8.

Nobody knows each other yet. Eight separate loners.

Over the next week, friendships form:

```
Start: 8 students, all separate.

  {1}  {2}  {3}  {4}  {5}  {6}  {7}  {8}

Union(1, 2): 1 and 2 become friends.

  {1,2}  {3}  {4}  {5}  {6}  {7}  {8}

Union(3, 4): 3 and 4 become friends.

  {1,2}  {3,4}  {5}  {6}  {7}  {8}

Union(5, 6): 5 and 6 become friends.

  {1,2}  {3,4}  {5,6}  {7}  {8}

Union(1, 3): 1 and 3 become friends. Their entire groups merge!

  {1,2,3,4}  {5,6}  {7}  {8}

Union(7, 8): 7 and 8 become friends.

  {1,2,3,4}  {5,6}  {7,8}

Union(5, 7): 5 and 7 become friends. Two groups merge again.

  {1,2,3,4}  {5,6,7,8}
```

Now your school counselor has one obsessive question they need to answer instantly, at any moment, for any two students:

> "Are student X and student Y in the same friend group?"

This question gets asked thousands of times a day. And new friendships form constantly.

`Find(2, 4)` → same group? YES.
`Find(3, 7)` → same group? NO.

That's the Disjoint Set Union (DSU) problem. Also called Union-Find.

> [↑ Back to Top](#top)

<a id="2-the-problem-without-dsu"></a>
# 2. The Problem Without DSU

The obvious solution: give every student in the same group the same color.

```
Start:
  Student: 1   2   3   4   5   6   7   8
  Color:   R   G   B   Y   P   O   Pu  Pi

Union(1, 2): change everyone with color G to R.
  Color:   R   R   B   Y   P   O   Pu  Pi   (1 change)

Union(3, 4): change everyone with Y to B.
  Color:   R   R   B   B   P   O   Pu  Pi   (1 change)

Union(1, 3): merge the R group and B group.
  Must recolor ALL students with color B to R (or vice versa).
  Color:   R   R   R   R   P   O   Pu  Pi   (2 changes)
```

That was small. But imagine groups of 500 students each merging.

When two groups of 500 merge → 500 recoloring operations.
When a group of 1000 merges with a group of 1000 → 1000 operations.

For n students, worst case: O(n) per union operation.
With n unions total: O(n²) for setup alone.

For 1 million students, that's 1 trillion operations. Not acceptable.

To check connectivity the DFS/BFS way:

Run DFS or BFS. Time: O(V + E)

If many queries: Too slow.

DSU makes it almost O(1). We need something smarter.

> [↑ Back to Top](#top)

<a id="3-core-idea"></a>
# 3. Core Idea

Here's the key idea. Instead of recoloring everyone, each group just **elects one representative** — call them the "class president."

To check if two students are in the same group, ask each one: "Who's your president?" If they name the same person, they're in the same group.

Each element belongs to a set. We maintain:

- Parent array
- Each set has a representative (root)

If two elements have the same root, they are connected.

## Visual: Elect a Class President

```
parent = [0, 1, 2, 3, 4, 5, 6, 7]
           ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑
           Each student points to themselves.

Union(1, 2): Make 2's president (2) report to 1's president (1).
parent = [0, 1, 1, 3, 4, 5, 6, 7]
                ↑
                2 now reports to 1

Tree view:  1    3  4  5  6  7  8
            |
            2

Union(3, 4): Make 4 report to 3.
parent = [0, 1, 1, 3, 3, 5, 6, 7]
Tree view:  1    3    5  6  7  8
            |    |
            2    4

Union(1, 3): Make 3's president (3) report to 1's president (1).
parent = [0, 1, 1, 1, 3, 5, 6, 7]
                     ↑
                     3 now reports to 1

Tree view:  1      5  6  7  8
           / \
          2   3
              |
              4
```

Now `Find(2)` traces: 2 → 1. President is 1.
Now `Find(4)` traces: 4 → 3 → 1. President is 1.
Same president → same group!

**Union** just redirects one root to point to another. O(1).
**Find** traces the chain to the root. O(depth of tree).

But what's the depth? In the worst case, our tree could be a long chain:

```
8 → 7 → 6 → 5 → 4 → 3 → 2 → 1
```

Finding 8's president takes 7 steps. For n students: O(n). Still slow.

We need two optimizations. They're simple. They change everything.

> [↑ Back to Top](#top)

<a id="4-initial-setup"></a>
# 4. Initial Setup

Each element is its own parent.

```
parent[i] = i
```

Each node is a separate set.

```python
class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))   # CORRECT: each node is its own parent
        self.rank = [0] * n
```

**Common mistake — wrong initialization:** Using `parent = [0] * n` makes every node point to node 0, as if all nodes are already in the same component. Use `parent = list(range(n))` so each node starts as its own root.

> 📝 **Practice:** [Q1 · Initialize parent array](./practice.md#q1--dsu-structure--initialize-the-parent-array)

> [↑ Back to Top](#top)

<a id="5-find-operation"></a>
# 5. Find Operation

Find the representative of an element.

Example:

```
1 → 2 → 3
```

Find(1) returns 3.

Implementation:

```python
def find(x):
    if parent[x] != x:
        return find(parent[x])
    return x
```

**Common mistake — find without path compression:** Without path compression, every `find` walks the entire path from node to root. In a balanced tree (with union by rank), this is O(log n). With repeated `find` calls on deep nodes, the work accumulates. Always use path compression — see section 7.

**Common mistake — connectivity check with parent[] instead of find():** To check if nodes A and B are connected, you must compare their roots (what `find()` returns), not their immediate parents. Two nodes can be in the same component but have different `parent` values if they are not roots. Using `parent[a] == parent[b]` only checks if they share the same immediate parent — always use `find(a) == find(b)`.

> [↑ Back to Top](#top)

<a id="6-union-operation"></a>
# 6. Union Operation

To connect a and b:

1. Find root of a.
2. Find root of b.
3. If different, make one root parent of other.

```python
def union(a, b):
    rootA = find(a)
    rootB = find(b)
    if rootA != rootB:
        parent[rootA] = rootB
```

Simple merging.

## Visual: Cycle Detection — Catching the Loop

DSU has a famous application: detecting cycles in an undirected graph.

If you're about to add an edge between two nodes that are already in the same connected component, that edge creates a cycle.

```
Edges to add: (0,1), (1,2), (0,2), (3,4)

Start:
  parent = [0, 1, 2, 3, 4]
  0   1   2   3   4    (all separate)

Add edge (0, 1):
  find(0)=0, find(1)=1. Different components. No cycle. Union them.
  parent = [0, 0, 2, 3, 4]

  0 — 1    2    3    4

Add edge (1, 2):
  find(1)=0, find(2)=2. Different. No cycle. Union.
  parent = [0, 0, 0, 3, 4]

  0 — 1 — 2    3    4

Add edge (0, 2):
  find(0)=0, find(2)=0. SAME COMPONENT!

  0 — 1 — 2
  └───────┘    ← adding this edge creates a cycle!

  CYCLE DETECTED!
```

The moment `find(u) == find(v)` before we union, we've caught a cycle.

```python
def has_cycle(n, edges):
    parent = list(range(n))
    rank = [0] * n

    for u, v in edges:
        if find(parent, u) == find(parent, v):
            return True    # u and v already connected — this edge is a cycle!
        union(parent, rank, u, v)

    return False
```

> 📝 **Practice:** [Q3 · Basic union merge](./practice.md#q3--union-operation--basic-merge) · [Q7 · Cycle detection](./practice.md#q7--cycle-detection--undirected-graph)

> [↑ Back to Top](#top)

<a id="7-path-compression"></a>
# 7. Path Compression (Very Important)

Problem:

Find can be slow if tree is deep.

Example:

```
1 → 2 → 3 → 4 → 5
```

Find(1) takes long.

Path compression: while finding root, attach nodes directly to root.

```python
def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]
```

After find:
```
1 → 5
2 → 5
3 → 5
4 → 5
```

Tree flattens.

## Visual: Path Compression — The Shortcut You Earn Once

```
Before find(5):

  0
  |
  1
  |
  3
  |
  5   ← we start here, want to get to root (0)

Trace: 5 → 3 → 1 → 0. Root is 0.

After find(5) with path compression:

  0
 /|\
1 3 5    ← now 5, 3, AND 1 all point directly to 0

Next time someone asks for find(3): 3 → 0. Done in 1 step.
Next time someone asks for find(5): 5 → 0. Done in 1 step.
```

That recursive call does the magic: on the way back up the recursion stack, every node gets its parent updated to point directly at the root.

One expensive find "flattens" the tree for everyone who comes after.

For large n, Python's recursion limit can be a problem. The iterative two-pass version is safer:

```python
def find_iterative(parent: list, x: int) -> int:
    # Pass 1: find the root
    root = x
    while parent[root] != root:
        root = parent[root]

    # Pass 2: compress the path — set every node's parent to root
    curr = x
    while curr != root:
        next_node = parent[curr]
        parent[curr] = root    # point directly to root
        curr = next_node

    return root
```

**Common mistake — modifying rank during path compression:** Path compression changes the tree structure (shortens paths) but should NOT update the rank array. Rank is an upper bound on tree height used to decide which root becomes the child during union. After compression the tree is shorter, but rank remains a valid (if looser) upper bound. Decrementing rank during `find` corrupts the union-by-rank invariant — rank must only increase, and only during union when two equal-rank trees merge.

> 📝 **Practice:** [Q5 · Path compression](./practice.md#q5--path-compression--flatten-on-find)

> [↑ Back to Top](#top)

<a id="8-union-by-rank-size"></a>
# 8. Union by Rank / Size

Always attach the smaller tree under the bigger tree. Keeps the tree shallow.

When merging two groups, we have a choice: make group A's root point to B's root, or B's root point to A's root.

**Bad union (tall tree gets taller):**

```
Tree A (height 3):     Tree B (height 1):

    A1                    B1
    |                     |
    A2                    B2
    |
    A3

Attach A under B (wrong choice):

    B1
    |
    B2
    |
    A1
    |
    A2
    |
    A3

New height: 5. Worse than before.
```

**Good union (short tree attaches under tall tree):**

```
Attach B UNDER A (small tree under large tree):

    A1
   / \
  A2  B1
  |   |
  A3  B2

New height: 3. Tree A didn't grow at all!
```

The rule: always attach the shorter tree (smaller rank) under the taller tree (larger rank).

Maintain a rank or size array:

```python
def union(parent, rank, x, y):
    rx, ry = find(parent, x), find(parent, y)
    if rx == ry:
        return   # already same group
    if rank[rx] < rank[ry]:
        rx, ry = ry, rx          # make rx the taller one
    parent[ry] = rx              # attach shorter under taller
    if rank[rx] == rank[ry]:
        rank[rx] += 1            # only grows when both are equal height
```

Rank only increases when two equal-height trees merge:
- A tree of rank 1 → contains at least 2 nodes
- A tree of rank 2 → contains at least 4 nodes
- A tree of rank k → contains at least 2^k nodes

For n nodes: max rank ≤ log₂(n). Tree height is bounded by O(log n).
With path compression on top: practically O(1) per operation.

**Alternative: Union by Size**

Union by size is equivalent in practice. Instead of tracking tree height (rank), track the number of nodes in each tree. It has the advantage of giving you `component_size` for free:

```python
class DSU_union_by_size:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.size = [1] * n    # each tree starts with size 1

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        self.size[rx] += self.size[ry]   # update size of the merged tree
        return True
```

**Common mistake — union without union by rank/size:** Without union by rank/size, you always attach one root under the other in a fixed order. Over time, this degenerates the tree into a linked list. A `find` on the deepest node must walk every node in the list: O(n) per find. Always track rank or size and attach the smaller tree under the larger one.

> 📝 **Practice:** [Q6 · Union by rank](./practice.md#q6--union-by-rank--attach-smaller-under-larger) · [Q9 · Union by size](./practice.md#q9--component-size-tracking--union-by-size)

> [↑ Back to Top](#top)

<a id="9-time-complexity"></a>
# 9. Time Complexity

With both optimizations together (path compression + union by rank):

Almost O(1) per operation.

More precisely: O(α(n))

Where α is the **inverse Ackermann function**.

How small is α(n)?

```
n                    α(n)
─────────────────────────
1                     0
2                     1
4                     2
16                    3
65536                 4
2^65536               5
number of atoms       ≤ 5
in the observable
universe
```

You will never, in any real program, see α(n) exceed 5.

For any problem a computer can solve in the lifetime of the universe: effectively O(1) per operation.

Not O(log n). Not O(log log n). Effectively O(1).

Note: you need BOTH optimizations for the O(α(n)) guarantee. Path compression alone or union by rank alone gives O(log n).

> [↑ Back to Top](#top)

<a id="10-why-dsu-is-better-than-dfs"></a>
# 10. Why DSU Is Better Than DFS Here

DFS:
O(V + E) per query.

DSU:
Near O(1) per query after preprocessing.

If many connectivity queries, DSU is superior.

## Visual: Quick Reference

```
┌───────────────────────────────────────────────────────────┐
│  DISJOINT SET UNION CHEAT SHEET                           │
├───────────────────────────────────────────────────────────┤
│  Structure:  parent[] array (forest of trees)             │
│              rank[] array (height of each tree's root)    │
│                                                           │
│  Operations:                                              │
│    find(x)         → O(α(n)) ≈ O(1)  find root/president │
│    union(x, y)     → O(α(n)) ≈ O(1)  merge two groups    │
│    connected(x,y)  → find(x)==find(y) same component?    │
│                                                           │
│  Optimizations:                                           │
│    Path compression → flatten tree during find()         │
│    Union by rank    → small tree under large tree         │
│    (need BOTH for O(α(n)) guarantee)                      │
│                                                           │
│  Classic patterns:                                        │
│    Cycle detection in undirected graph                    │
│    Kruskal's MST algorithm                                │
│    Number of connected components                         │
│    Dynamic connectivity queries                           │
│    Percolation problems                                   │
│    Grid: count islands / connected regions               │
└───────────────────────────────────────────────────────────┘
```

> 📝 **Practice:** [Q11 · DSU vs BFS/DFS](./practice.md#q11--dsu-vs-bfsdfs--when-to-choose-which)

> [↑ Back to Top](#top)

<a id="11-common-use-cases"></a>
# 11. Common Use Cases

## Cycle Detection in Undirected Graph

If two nodes already have the same root, adding an edge between them creates a cycle.

Used in Kruskal's algorithm. This is exactly how the build-phase of Kruskal's Minimum Spanning Tree algorithm works — it processes edges in order of weight and skips any edge that would form a cycle.

**Common mistake — assuming DSU works for directed graph cycle detection:** DSU only handles undirected connectivity. For directed graphs, use DFS with a visited/in-stack coloring approach instead.

> 📝 **Practice:** [Q7 · Cycle detection](./practice.md#q7--cycle-detection--undirected-graph) · [Q8 · Redundant connection](./practice.md#q8--redundant-connection--last-cycle-creating-edge)

## Connected Components

Count distinct roots.

> 📝 **Practice:** [Q4 · Count connected components](./practice.md#q4--connected-components--count-distinct-roots)

## Network Connectivity Problems

Leetcode: Number of Provinces · Redundant Connection · Accounts Merge

Very common.

> 📝 **Practice:** [Q13 · Accounts merge](./practice.md#q13--accounts-merge--email-grouping) · [Q12 · Kruskal's MST](./practice.md#q12--kruskals-mst--greedy-edge-selection)

> [↑ Back to Top](#top)

<a id="12-real-world-applications"></a>
# 12. Real-World Applications

- Social network grouping
- Network cable connectivity
- Image segmentation
- Cluster detection
- Kruskal's Minimum Spanning Tree
- Group management systems

DSU is widely used in graph algorithms.

> [↑ Back to Top](#top)

<a id="13-mental-model"></a>
# 13. Mental Model

Think of DSU as a group leader system.

Each group has a leader. To check if two people are in the same group: check if they have the same leader.

Union merges leaders. Find finds the leader.

The mental model to keep: each group has a president (root). To check membership, ask "who's your president?" — path compression means you remember the answer, and union by rank means the chain of command never gets unreasonably long.

When a problem involves groups merging, connectivity queries, or cycle detection — DSU gives you near-O(1) per operation with almost no code.

## Interview-Ready DSU Template

```python
class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))   # CORRECT: each node is its own parent
        self.rank = [0] * n
        self.size = [1] * n            # size of each component
        self.num_components = n        # start with n separate components

    def find(self, x: int) -> int:
        """Find root with path compression. O(α(n)) amortized."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # compress — do NOT modify rank
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)  # CORRECT: use find(), not parent[]
        if rx == ry:
            return False                       # already in same component

        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx    # ensure rx always has >= rank

        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1  # rank ONLY increases in union when ranks were equal

        self.size[rx] += self.size[ry]
        self.num_components -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)   # CORRECT: compare find() results

    def component_size(self, x: int) -> int:
        return self.size[self.find(x)]
```

> 📝 **Practice:** [Q20 · Spot the five bugs](./practice.md#q20--dsu-correctness--spot-the-five-bugs)

> [↑ Back to Top](#top)

<a id="14-final-understanding"></a>
# 14. Final Understanding

Disjoint Set Union is:

- Data structure for grouping
- Efficient connectivity checker
- Used in graph algorithms
- Near constant-time operations
- Powerful when many queries exist

Mastering DSU prepares you for:

- Kruskal's algorithm
- Advanced graph problems
- Competitive programming
- Connectivity-based system problems

DSU is elegant and efficient.

**[🏠 Back to README](../README.md)**

**Prev:** [← Segment Tree — Interview Q&A](../23_segment_tree/interview.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)

> [↑ Back to Top](#top)
