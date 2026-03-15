# 📘 Heaps — The Structure of Priority

> A heap is not about sorting everything.
>
> It is about knowing the most important element instantly.
>
> If BST organizes everything,
> Heap focuses only on the top priority.

Heaps power:

- Priority queues
- Scheduling systems
- Dijkstra’s algorithm
- Top K problems
- System resource management

Heaps are extremely important in interviews.

---

# 🏆 1️⃣ Real Life Story — School Assembly Line

Imagine students standing in line for awards.

You don’t care about full ranking.
You only care about:

Who is the highest scorer?

You want to quickly find the top student.

Heap does exactly that.

It guarantees:

Top element always at root.

---

# 🌳 2️⃣ What Is a Heap?

A heap is:

A complete binary tree that satisfies heap property.

Two types:

- Min Heap
- Max Heap

---

# 📐 3️⃣ Complete Binary Tree (Very Important)

Complete means:

- All levels filled
- Last level filled from left to right

Example:

```
        10
       /  \
     20    30
    /  \
  40   50
```

Valid complete tree.

But this is NOT complete:

```
        10
       /  \
     20    30
           /
         40
```

Because left child missing.

Completeness is mandatory.

---

# 🔼 4️⃣ Heap Property

---

## 🔹 Min Heap

Parent ≤ children.

Smallest element at root.

---

## 🔹 Max Heap

Parent ≥ children.

Largest element at root.

---

Example Min Heap:

```
        2
       / \
      5   8
     / \
    10 12
```

Root always smallest.

---

# 📦 5️⃣ Heap Stored as Array

Very important:

Heap is stored in array.

No pointers needed.

If index = i

Left child = 2i + 1  
Right child = 2i + 2  
Parent = (i - 1) // 2  

This works because tree is complete.

Efficient memory usage.

---

# 🔁 6️⃣ Insert in Heap (Bubble Up)

Steps:

1. Insert at end.
2. Compare with parent.
3. Swap if heap property violated.
4. Continue upward.

Example:

Insert 1 in min heap:

```
        2
       / \
      5   8
```

Insert at end:

```
        2
       / \
      5   8
     /
    1
```

Bubble up:

Swap with 5.

Swap with 2.

New root = 1.

Time:
O(log n)

Because height ≈ log n.

---

# 🔽 7️⃣ Delete from Heap (Bubble Down)

Remove root.

Replace with last element.

Heapify downward.

Example:

Remove 2 from:

```
        2
       / \
      5   8
```

Replace with 8:

```
        8
       /
      5
```

Bubble down:

Swap with smaller child.

Time:
O(log n)

---

# ⚡ 8️⃣ Heapify (Build Heap Efficiently)

Given array:

Build heap in O(n).

Start from last non-leaf node.
Heapify downward.

Important insight:

Heapify is O(n), not O(n log n).

This surprises many.

---

# 🧠 9️⃣ Why Heap Is Powerful

Operations:

Insert → O(log n)  
Delete → O(log n)  
Peek → O(1)

Always know min or max instantly.

That’s powerful.

---

# 🔢 1️⃣0️⃣ Heaps in Python

Python provides:

```python
import heapq

heap = []
heapq.heappush(heap, 5)
heapq.heappop(heap)
```

Python has min heap by default.

For max heap:
Insert negative values.

---

# 🎯 1️⃣1️⃣ Common Interview Patterns

Heaps are used in:

- Top K elements
- Kth largest element
- Merge k sorted lists
- Median of stream
- Dijkstra’s shortest path
- Task scheduling
- Priority queues

Very common in medium-hard interviews.

---

# ⚖️ 1️⃣2️⃣ Heap vs BST

Heap:
Only root guaranteed min/max.
Not fully sorted.

BST:
Fully ordered.
Inorder gives sorted list.

Heap:
Faster top element access.

BST:
Better for range queries.

Choose wisely.

---

# 🌍 1️⃣3️⃣ Real-World Applications

- CPU scheduling
- Network packet priority
- Event-driven simulation
- Operating systems
- Job schedulers
- Load balancing

Heaps manage priorities in real systems.

---

# ⚠️ 1️⃣4️⃣ Common Mistakes

- Forgetting completeness requirement
- Confusing heap with sorted structure
- Incorrect index calculations
- Assuming heap gives sorted array
- Not heapifying after deletion

Heap is not fully sorted.

---

# 🧠 1️⃣5️⃣ Mental Model

Think of heap as:

A mountain.

Top is highest (max heap)
or lowest (min heap).

Everything else is somewhere below.

You only guarantee peak.

---

# 📌 Final Understanding

Heap is:

- Complete binary tree
- Maintains priority order
- Efficient for top element access
- O(log n) insert/delete
- O(1) peek
- Used in priority queue

Heaps are essential for many advanced algorithms.

Mastering heap prepares you for:

- Dijkstra
- A*
- Scheduling problems
- Median maintenance
- Advanced system design

---

# 🔁 Navigation

Previous:  
[15_binary_search_trees/interview.md](/dsa-complete-mastery/15_binary_search_trees/interview.md)

Next:  
[16_heaps/interview.md](/dsa-complete-mastery/16_heaps/interview.md)  
[17_trie/theory.md](/dsa-complete-mastery/17_trie/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Binary Search Trees — Interview Q&A](../15_binary_search_trees/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
