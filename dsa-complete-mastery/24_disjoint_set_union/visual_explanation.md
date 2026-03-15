# Disjoint Set Union — The Friend Group Problem

---

## The School Where Everyone Belongs Somewhere

First day of high school. Eight students arrive: 1, 2, 3, 4, 5, 6, 7, 8.

Nobody knows each other yet. Eight separate loners.

Over the next week, friendships form:
- 1 and 2 become friends → they're a group
- 3 and 4 become friends → separate group
- 5 and 6 become friends → another group
- Then 2 and 3 become friends → suddenly groups {1,2} and {3,4} merge into {1,2,3,4}

Now your school counselor has one obsessive question they need to answer instantly,
at any moment, for any two students:

> "Are student X and student Y in the same friend group?"

This question gets asked thousands of times a day. And new friendships form constantly.

That's the Disjoint Set Union (DSU) problem. Also called Union-Find.

---

## Scene 1: The Friendships Form

Let's watch the groups evolve as friendships are established.

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

Now: `Find(2, 4)` → same group? YES.
Now: `Find(3, 7)` → same group? NO.

The counselor asks this a thousand times a day. We need it to be fast.

---

## Scene 2: The Naive Approach — Why It Breaks

The obvious solution: give every student in the same group the same color.

```
Start:
  Student: 1   2   3   4   5   6   7   8
  Color:   R   G   B   Y   P   O   Pu  Pi

Union(1, 2): change everyone with color G to R.
  Student: 1   2   3   4   5   6   7   8
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

We need something smarter.

---

## Scene 3: Elect a Class President

Here's the key idea. Instead of recoloring everyone, each group just **elects one
representative** — call them the "class president."

To check if two students are in the same group, ask each one: "Who's your president?"
If they name the same person, they're in the same group.

We represent this with a `parent` array. Initially, everyone is their own president.

```
parent = [0, 1, 2, 3, 4, 5, 6, 7]
           ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑
           Each student points to themselves.
```

When we form a friendship, we make one group's president report to the other group's
president. We're building a chain of "who do I report to?"

```
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

---

## Scene 4: Path Compression — The Shortcut You Earn Once

When we ask "who's the president of student 5?" and have to walk a long chain:

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
```

While we're walking that path, we already did all the work. Why not remember it?
**Point every node we visited directly at the root.**

```
After find(5) with path compression:

  0
 /|\
1 3 5    ← now 5, 3, AND 1 all point directly to 0

Next time someone asks for find(3): 3 → 0. Done in 1 step.
Next time someone asks for find(5): 5 → 0. Done in 1 step.
```

The code is almost embarrassingly simple:

```python
def find(parent, x):
    if parent[x] != x:
        parent[x] = find(parent, parent[x])   # point straight to root while returning
    return parent[x]
```

That recursive call does the magic: on the way back up the recursion stack,
every node gets its parent updated to point directly at the root.

One expensive find "flattens" the tree for everyone who comes after.

---

## Scene 5: Union by Rank — Keep Trees Short from the Start

Path compression is reactive. Union by rank is proactive.

When merging two groups, we have a choice: make group A's root point to B's root,
or B's root point to A's root. Which is better?

**Bad union (tall tree gets taller):**

```
Tree A (height 3):     Tree B (height 1):

    A1                    B1
    |                     |
    A2                    B2
    |
    A3

Attach B under A (wrong choice):

    A1
    |
    A2
    |
    A3
    |
    B1
    |
    B2

New height: 5. Worse than before.
```

**Good union (short tree attaches under tall tree):**

```
Attach A under B? Still bad — B's height=1, A's height=3, result height=4.

Actually: Attach B UNDER A (small tree under large tree):

    A1
   / \
  A2  B1
  |   |
  A3  B2

New height: 3. Tree A didn't grow at all!
```

The rule: always attach the shorter tree (smaller rank) under the taller tree (larger rank).

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

**Rank only increases** when two equal-height trees merge. This means:
- A tree of rank 1 → contains at least 2 nodes
- A tree of rank 2 → contains at least 4 nodes
- A tree of rank k → contains at least 2^k nodes

For n nodes: max rank ≤ log₂(n). Tree height is bounded by O(log n).
With path compression on top: practically O(1) per operation.

---

## Scene 6: Cycle Detection — Catching the Loop

DSU has a famous application: detecting cycles in an undirected graph.

The logic is elegant:

> If you're about to add an edge between two nodes that are **already in the same
> connected component**, that edge creates a cycle.

Let's build a graph with 5 nodes (0-4), adding edges one at a time:

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

  CYCLE DETECTED! ✗
```

The moment `find(u) == find(v)` before we union, we've caught a cycle.

This is exactly how the build-phase of Kruskal's Minimum Spanning Tree algorithm works.
It processes edges in order of weight and skips any edge that would form a cycle.

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

---

## Scene 7: The Complexity Story — Near Magic

With both optimizations together (path compression + union by rank), the amortized
cost per operation is:

```
O(α(n))
```

α is the **inverse Ackermann function**. It is, for all practical purposes, a constant.

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

For any problem a computer can solve in the lifetime of the universe: **O(1) per operation**.

Not O(log n). Not O(log log n). Effectively O(1).

---

## Quick Reference

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

The mental model to keep: each group has a president (root). To check membership,
ask "who's your president?" — path compression means you remember the answer,
and union by rank means the chain of command never gets unreasonably long.

When a problem involves groups merging, connectivity queries, or cycle detection —
DSU gives you near-O(1) per operation with almost no code.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
