# 📘 Disjoint Set Union (Union-Find) — Managing Connected Groups Efficiently

> Imagine you have many people.
> Some of them are friends.
>
> Over time, friendships form.
>
> You want to quickly answer:
>
> “Are these two people connected?”

You don’t want to search entire network every time.

Disjoint Set Union solves this efficiently.

---

# 🧠 1️⃣ Real Life Story — Friend Circles

Imagine 7 students:

1, 2, 3, 4, 5, 6, 7

Initially:
Everyone is separate.

Friendships happen:

1–2  
2–3  
4–5  

Now groups are:

{1,2,3}
{4,5}
{6}
{7}

If someone asks:
“Are 1 and 3 connected?”

Yes.

“Are 1 and 5 connected?”

No.

DSU manages this efficiently.

---

# 🔍 2️⃣ The Problem Without DSU

To check connectivity:

Run DFS or BFS.

Time:
O(V + E)

If many queries:
Too slow.

DSU makes it almost O(1).

---

# 🧱 3️⃣ Core Idea

Each element belongs to a set.

We maintain:

- Parent array
- Each set has representative (root)

If two elements have same root,
they are connected.

---

# 🛠 4️⃣ Initial Setup

Each element is its own parent.

```
parent[i] = i
```

Each node is separate set.

---

# 🔎 5️⃣ Find Operation

Find representative of element.

Example:

1 → 2 → 3

Find(1) returns 3.

Implementation:

```python
def find(x):
    if parent[x] != x:
        return find(parent[x])
    return x
```

---

# 🔄 6️⃣ Union Operation

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

---

# ⚡ 7️⃣ Path Compression (Very Important)

Problem:

Find can be slow if tree deep.

Example:

1 → 2 → 3 → 4 → 5

Find(1) takes long.

Path compression:

While finding root,
attach nodes directly to root.

```python
def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]
```

After find:
1 → 5
2 → 5
3 → 5
4 → 5

Tree flattens.

---

# ⚖️ 8️⃣ Union by Rank / Size

Always attach smaller tree under bigger tree.

Keeps tree shallow.

Maintain:

rank or size array.

```python
if rank[rootA] < rank[rootB]:
    parent[rootA] = rootB
else:
    parent[rootB] = rootA
```

Improves performance.

---

# 📏 9️⃣ Time Complexity

With:

- Path compression
- Union by rank

Time per operation:

Almost O(1)

More precisely:
O(α(n))

Where α is inverse Ackermann function.

Practically constant.

Very powerful.

---

# 🌳 1️⃣0️⃣ Why DSU Is Better Than DFS Here

DFS:
O(V + E) per query.

DSU:
Near O(1) per query after preprocessing.

If many connectivity queries,
DSU is superior.

---

# 🔥 1️⃣1️⃣ Common Use Cases

---

## 🔹 Cycle Detection in Undirected Graph

If two nodes already have same root,
adding edge creates cycle.

Used in Kruskal’s algorithm.

---

## 🔹 Connected Components

Count distinct roots.

---

## 🔹 Network Connectivity Problems

Leetcode:
Number of Provinces
Redundant Connection
Accounts Merge

Very common.

---

# 🌍 1️⃣2️⃣ Real-World Applications

- Social network grouping
- Network cable connectivity
- Image segmentation
- Cluster detection
- Kruskal’s Minimum Spanning Tree
- Group management systems

DSU is widely used in graph algorithms.

---

# ⚠️ 1️⃣3️⃣ Common Mistakes

- Forgetting path compression
- Forgetting union by rank
- Incorrect parent initialization
- Mixing up root vs node
- Assuming DSU works for directed graph cycle detection (it doesn't)

DSU only handles undirected connectivity easily.

---

# 🧠 1️⃣4️⃣ Mental Model

Think of DSU as:

Group leader system.

Each group has leader.

To check if two people same group:
Check if same leader.

Union merges leaders.

Find finds leader.

Simple but powerful.

---

# 📌 1️⃣5️⃣ Final Understanding

Disjoint Set Union is:

- Data structure for grouping
- Efficient connectivity checker
- Used in graph algorithms
- Near constant-time operations
- Powerful when many queries exist

Mastering DSU prepares you for:

- Kruskal’s algorithm
- Advanced graph problems
- Competitive programming
- Connectivity-based system problems

DSU is elegant and efficient.

---

# 🔁 Navigation

Previous:  
[23_segment_tree/interview.md](/dsa-complete-mastery/23_segment_tree/interview.md)

Next:  
[24_disjoint_set_union/interview.md](/dsa-complete-mastery/24_disjoint_set_union/interview.md)  
[25_advanced_graphs/theory.md](/dsa-complete-mastery/25_advanced_graphs/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Segment Tree — Interview Q&A](../23_segment_tree/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
