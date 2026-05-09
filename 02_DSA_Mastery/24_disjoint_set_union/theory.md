<a id="top"></a>
# Disjoint Set Union (Union-Find) — Managing Connected Groups Efficiently

> Imagine you are Gael, a village elder on a vast archipelago.
> Each island is its own isolated community.
>
> Over time, bridges are built between islands.
>
> Travelers constantly ask you:
>
> "Are these two islands connected — can I walk from one to the other?"

You don't want to send scouts across the entire bridge network every time someone asks.

Disjoint Set Union solves this efficiently — it lets Gael answer connectivity questions in near-constant time, no matter how many bridges have been built.

## 📖 Table of Contents

1. [Real Life Story — Friend Circles](#1-real-life-story)
   - [Eight Students Arrive](#eight-students-arrive)
   - [The Counselor's Question](#the-counselors-question)
2. [The Problem Without DSU](#2-the-problem-without-dsu)
   - [Recoloring Approach](#recoloring-approach)
   - [DFS/BFS Approach](#dfsbfs-approach)
3. [Core Idea](#3-core-idea)
   - [Elect a Representative](#elect-a-representative)
   - [Tree Structure](#tree-structure)
   - [Worst Case Without Optimization](#worst-case-without-optimization)
4. [Initial Setup](#4-initial-setup)
   - [Parent Array Initialization](#parent-array-initialization)
5. [Find Operation](#5-find-operation)
   - [Tracing to the Root](#tracing-to-the-root)
6. [Union Operation](#6-union-operation)
   - [Merging Two Groups](#merging-two-groups)
   - [Cycle Detection Application](#cycle-detection-application)
7. [Path Compression](#7-path-compression)
   - [Flattening the Tree](#flattening-the-tree)
   - [Iterative Two-Pass Version](#iterative-two-pass-version)
8. [Union by Rank / Size](#8-union-by-rank-size)
   - [Bad Union vs Good Union](#bad-union-vs-good-union)
   - [Union by Size Alternative](#union-by-size-alternative)
9. [Time Complexity](#9-time-complexity)
   - [Inverse Ackermann Function](#inverse-ackermann-function)
10. [Why DSU Is Better Than DFS](#10-why-dsu-is-better-than-dfs)
    - [Quick Reference Cheat Sheet](#quick-reference-cheat-sheet)
11. [Common Use Cases](#11-common-use-cases)
    - [Cycle Detection in Undirected Graph](#cycle-detection-in-undirected-graph)
    - [Connected Components](#connected-components)
    - [Network Connectivity Problems](#network-connectivity-problems)
12. [Mental Model and Interview Template](#12-mental-model-and-interview-template)
    - [The Group Leader System](#the-group-leader-system)
    - [Interview-Ready DSU Template](#interview-ready-dsu-template)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
find operation · union operation · path compression

**Should Learn** — Important for real projects, comes up regularly:
union by rank/size · cycle detection in graphs · Kruskal's MST application

**Good to Know** — Useful in specific situations, not always tested:
connected components use case · time complexity (inverse Ackermann)

**Reference** — Know it exists, look up syntax when needed:
weighted DSU · DSU with rollback · persistent DSU · bipartite checking

<a id="1-real-life-story"></a>
# 1. Real Life Story — Friend Circles

Gael remembers his first day as a village elder — the day eight new families arrived on the archipelago, each settling on their own island. No bridges existed yet. Eight isolated communities, eight separate worlds.

<a id="eight-students-arrive"></a>

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

<a id="the-counselors-question"></a>

Now your school counselor has one obsessive question they need to answer instantly, at any moment, for any two students:

> "Are student X and student Y in the same friend group?"

This question gets asked thousands of times a day. And new friendships form constantly.

`Find(2, 4)` → same group? YES.
`Find(3, 7)` → same group? NO.

That's the Disjoint Set Union (DSU) problem. Also called Union-Find. Gael faces the same challenge — travelers ask "Can I get from Island A to Island B?" thousands of times a day, and new bridges keep being built.

> [↑ Back to Top](#top)

<a id="2-the-problem-without-dsu"></a>
# 2. The Problem Without DSU

Gael first tried the obvious approach: paint every island in the same alliance the same color. When two alliances merged, he'd repaint every island in one alliance to match the other. For small archipelagos this was fine — but as the population grew into the thousands, the repainting crews couldn't keep up.

<a id="recoloring-approach"></a>

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

<a id="dfsbfs-approach"></a>

To check connectivity the DFS/BFS way:

Run DFS or BFS. Time: O(V + E)

If many queries: Too slow.

DSU makes it almost O(1). We need something smarter.

> [↑ Back to Top](#top)

<a id="3-core-idea"></a>
# 3. Core Idea

Gael had a breakthrough: instead of repainting every island when alliances merged, each alliance would simply elect one island as its capital. To check if two islands belong to the same alliance, just ask each one: "Who is your capital?" If both name the same capital — they're connected.

<a id="elect-a-representative"></a>

Here's the key idea. Instead of recoloring everyone, each group just **elects one representative** — call them the "class president."

To check if two students are in the same group, ask each one: "Who's your president?" If they name the same person, they're in the same group.

Each element belongs to a set. We maintain:

- Parent array
- Each set has a representative (root)

If two elements have the same root, they are connected.

<a id="tree-structure"></a>

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

<a id="worst-case-without-optimization"></a>

But what's the depth? In the worst case, our tree could be a long chain:

```
8 → 7 → 6 → 5 → 4 → 3 → 2 → 1
```

Finding 8's president takes 7 steps. For n students: O(n). Still slow.

We need two optimizations. They're simple. They change everything.

> [↑ Back to Top](#top)

<a id="4-initial-setup"></a>
# 4. Initial Setup

Gael's first step when a new island joins the archipelago: register it as its own independent nation. Every island starts as its own capital — pointing to itself. Only when bridges are built do alliances form and capitals change.

<a id="parent-array-initialization"></a>

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

When a traveler arrives at any island and asks "Who is the capital of your alliance?", Gael tells them to follow the chain of authority — each island points to its superior, and the superior points further up, until you reach an island that points to itself. That self-pointing island is the capital. That's the Find operation.

<a id="tracing-to-the-root"></a>

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

When Gael builds a bridge between two islands from different alliances, he doesn't repaint anything. He simply tells one capital to recognize the other as its new superior. One meeting between two leaders, one handshake, and now thousands of islanders are in the same alliance — without any of them needing to know it happened.

<a id="merging-two-groups"></a>

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

<a id="cycle-detection-application"></a>

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
# 7. Path Compression

Gael noticed a problem: some islands were deep in the chain of command. Island Z reported to Island Y, which reported to Island X, which reported to the capital. Every time someone from Island Z asked "Who's my capital?", a messenger had to traverse the entire chain. So Gael made a rule: once you learn who the capital is, update your records to point directly to the capital. Next time you ask, the answer is immediate.

<a id="flattening-the-tree"></a>

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

<a id="iterative-two-pass-version"></a>

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

Gael learned another lesson the hard way. When two alliances merged, he initially let the smaller alliance absorb the larger one — meaning thousands of islanders in the big alliance suddenly had a longer chain to their new capital. The smarter move: always make the smaller alliance join the larger one. The big tree stays short; the small tree just gets one extra link at the top.

Always attach the smaller tree under the bigger tree. Keeps the tree shallow.

When merging two groups, we have a choice: make group A's root point to B's root, or B's root point to A's root.

<a id="bad-union-vs-good-union"></a>

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

<a id="union-by-size-alternative"></a>

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

Gael once asked the island mathematician: "How many hops does it take in the worst case, with both my optimizations?" The mathematician smiled and said: "For any number of islands that could fit in the observable universe — at most 5 hops. Effectively instant."

<a id="inverse-ackermann-function"></a>

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
# 10. Why DSU Is Better Than DFS

Gael has two messengers. The DFS messenger physically walks the entire bridge network every time someone asks a connectivity question — visiting every island and every bridge until he finds (or doesn't find) the destination. The DSU messenger just checks his notebook: "Who's your capital? Same as theirs? Done." For one question, the DFS messenger is fine. For a thousand questions a day with bridges being built constantly — only the DSU messenger can keep up.

DFS:
O(V + E) per query.

DSU:
Near O(1) per query after preprocessing.

If many connectivity queries, DSU is superior.

<a id="quick-reference-cheat-sheet"></a>

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

Gael has seen the same pattern repeat across his archipelago career — certain problems keep coming back, and DSU solves them all with the same elegant structure. Here are the three patterns he sees most often.

<a id="cycle-detection-in-undirected-graph"></a>

**Cycle Detection in Undirected Graph**

If two nodes already have the same root, adding an edge between them creates a cycle.

Used in Kruskal's algorithm. This is exactly how the build-phase of Kruskal's Minimum Spanning Tree algorithm works — it processes edges in order of weight and skips any edge that would form a cycle.

**Common mistake — assuming DSU works for directed graph cycle detection:** DSU only handles undirected connectivity. For directed graphs, use DFS with a visited/in-stack coloring approach instead.

> 📝 **Practice:** [Q7 · Cycle detection](./practice.md#q7--cycle-detection--undirected-graph) · [Q8 · Redundant connection](./practice.md#q8--redundant-connection--last-cycle-creating-edge)

<a id="connected-components"></a>

**Connected Components**

Count distinct roots.

> 📝 **Practice:** [Q4 · Count connected components](./practice.md#q4--connected-components--count-distinct-roots)

<a id="network-connectivity-problems"></a>

**Network Connectivity Problems**

Leetcode: Number of Provinces · Redundant Connection · Accounts Merge

Very common.

> 📝 **Practice:** [Q13 · Accounts merge](./practice.md#q13--accounts-merge--email-grouping) · [Q12 · Kruskal's MST](./practice.md#q12--kruskals-mst--greedy-edge-selection)

> [↑ Back to Top](#top)

<a id="12-mental-model-and-interview-template"></a>
# 12. Mental Model and Interview Template

Gael summarizes his decades of experience into one sentence for young elders: "Each alliance has a capital. To check membership, ask 'who is your capital?' Path compression means you remember the answer forever, and union by rank means the chain of command never gets unreasonably long."

<a id="the-group-leader-system"></a>

Think of DSU as a group leader system.

Each group has a leader. To check if two people are in the same group: check if they have the same leader.

Union merges leaders. Find finds the leader.

The mental model to keep: each group has a president (root). To check membership, ask "who's your president?" — path compression means you remember the answer, and union by rank means the chain of command never gets unreasonably long.

When a problem involves groups merging, connectivity queries, or cycle detection — DSU gives you near-O(1) per operation with almost no code.

<a id="interview-ready-dsu-template"></a>

**Interview-Ready DSU Template**

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

<a id="summary"></a>
## 🔥 Summary

Disjoint Set Union is:

- Data structure for grouping
- Efficient connectivity checker
- Used in graph algorithms
- Near constant-time operations
- Powerful when many queries exist

Real-world applications:

- Social network grouping
- Network cable connectivity
- Image segmentation
- Cluster detection
- Kruskal's Minimum Spanning Tree
- Group management systems

DSU is widely used in graph algorithms.

Mastering DSU prepares you for:

- Kruskal's algorithm
- Advanced graph problems
- Competitive programming
- Connectivity-based system problems

DSU is elegant and efficient. Gael's parting wisdom: "Any time you see groups merging and connectivity questions being asked — reach for Union-Find. Two arrays, two optimizations, near-constant time. It is one of the most powerful tools in your algorithmic toolkit."

> [↑ Back to Top](#top)

**[Back to README](../README.md)**

| Prev | Next |
|------|------|
| [← 23 Segment Tree](../23_segment_tree/theory.md) | [25 Advanced Graphs →](../25_advanced_graphs/theory.md) |

**This folder:** [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)

**Related modules:** [18 Graphs](../18_graphs/theory.md) · [25 Advanced Graphs](../25_advanced_graphs/theory.md) · [19 Greedy](../19_greedy/theory.md)

**Jump to:** [Arrays](../02_arrays/theory.md) · [Trees](../14_trees/theory.md) · [Dynamic Programming](../21_dynamic_programming/theory.md) · [Graphs](../18_graphs/theory.md)
