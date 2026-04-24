# 📘 Segment Tree — The Power of Efficient Range Queries

> Suppose you have an array.
>
> You must:
> - Query sum of range many times
> - Update elements frequently
>
> Brute force becomes too slow.
>
> Segment Tree solves this efficiently.

Segment Tree is a data structure designed for:

- Fast range queries
- Fast updates

> 📝 **Practice:** [Q67 · segment-tree-range-query](../dsa_practice_questions_100.md#q67--thinking--segment-tree-range-query)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
segment tree structure · range query · point update · O(log n) operations

**Should Learn** — Important for real projects, comes up regularly:
lazy propagation · Fenwick tree (BIT) as simpler alternative

**Good to Know** — Useful in specific situations, not always tested:
when to use over prefix sum · build complexity O(n)

**Reference** — Know it exists, look up syntax when needed:
persistent segment tree · 2D segment trees · square root decomposition

---

# 🧠 1️⃣ Real Life Story — Warehouse Inventory

Imagine a warehouse with 1000 shelves.

Each shelf has number of products.

You need to answer:

“How many products between shelf 200 and 450?”

And shelves keep changing.

Brute force:
Loop every time → O(n)

Too slow if queries are frequent.

Segment Tree:
Preprocess and answer in O(log n).

---

# 📦 2️⃣ Problem Without Segment Tree

Array:

[1, 3, 5, 7, 9, 11]

Query:
Sum from index 1 to 4.

Without optimization:
Add manually → O(n)

If 10⁵ queries:
Very slow.

---

# 🌳 3️⃣ Core Idea of Segment Tree

Break array into segments.

Store sum of segments in tree nodes.

Each node represents:

Sum of a range.

Tree structure:

```
                [0-5]
              /        \
         [0-2]          [3-5]
        /     \        /     \
    [0-1]    [2-2]  [3-4]   [5-5]
```

Each node stores sum of its range.

---

# 🛠 4️⃣ Building Segment Tree

Build bottom-up.

Leaf nodes:
Store individual elements.

Parent:
Sum of children.

Time:
O(n)

Space:
O(4n) safe allocation.

---

# 🔍 5️⃣ Querying Range

Suppose query [1,4]

Three cases:

1. Complete overlap → return node value.
2. No overlap → return 0.
3. Partial overlap → query both children.

Each query:
O(log n)

Because tree height ≈ log n.

---

# 🔄 6️⃣ Updating Element

If arr[2] changes:

Update leaf.
Update all parents on path.

Time:
O(log n)

Efficient for frequent updates.

---

# ⚡ 7️⃣ Why Segment Tree Is Powerful

Operations:

Build → O(n)
Query → O(log n)
Update → O(log n)

Without it:

Query → O(n)

Huge improvement for many queries.

---

# 🔥 8️⃣ Lazy Propagation (Advanced)

Problem:

Update entire range.

Example:
Add +5 to range [1,4]

Naively:
Update each element → O(n)

Lazy propagation:
Delay update.
Mark node as lazy.
Propagate when needed.

Time:
O(log n)

Very important for range updates.

---

# 📐 9️⃣ When to Use Segment Tree

Use when:

- Many range queries
- Many updates
- Need fast performance
- Query type associative (sum, min, max, gcd)

---

# ⚠️ 1️⃣0️⃣ When NOT to Use

Avoid when:

- Queries are few
- No updates
- Simpler prefix sum works
- Small input size

Segment tree adds complexity.

---

# 🧠 1️⃣1️⃣ Compare With Other Structures

Prefix Sum:
Fast queries O(1)
No updates O(n)

Fenwick Tree:
Simpler than segment tree
Handles prefix queries

Segment Tree:
More flexible
Handles range queries + updates

Choose wisely.

---

# 🌍 1️⃣2️⃣ Real-World Applications

- Financial data range queries
- Real-time analytics
- Gaming leaderboards
- Database aggregation queries
- CPU monitoring ranges

Segment trees power range analytics systems.

---

# ⚠️ 1️⃣3️⃣ Common Mistakes

- Wrong indexing
- Forgetting partial overlap case
- Incorrect lazy propagation
- Using too small array size
- Off-by-one errors

Segment tree requires careful implementation.

---

# 🧠 1️⃣4️⃣ Mental Model

Think of segment tree as:

Breaking big problem into halves repeatedly.

Each node stores summary of its segment.

Instead of recalculating range,
you combine precomputed segments.

---

# 📌 1️⃣5️⃣ Final Understanding

Segment Tree is:

- Tree over array
- Stores range information
- Supports fast range query
- Supports fast updates
- O(log n) operations
- Advanced but powerful

Mastering segment tree prepares you for:

- Competitive programming
- Advanced algorithm interviews
- High-performance systems
- Range aggregation problems

Segment Tree is a power tool.
Use when necessary.

---

## 🌳 Fenwick Tree (Binary Indexed Tree) — Simpler Range Queries

> If a segment tree is a full surgical kit, a Fenwick tree is a pocket knife — less powerful, but faster to code and half the memory when point updates and prefix sums are all you need.

A **Fenwick tree** (also called a **Binary Indexed Tree** or BIT) supports two operations on an array in O(log n):
1. **Point update** — change a single element
2. **Prefix sum query** — sum from index 1 to i

Unlike a segment tree, a Fenwick tree cannot handle range minimum/maximum queries, but for prefix sums and point updates it requires less code and half the memory.

```python
class FenwickTree:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)   # ← 1-indexed

    def update(self, i, delta):
        """Add delta to position i (1-indexed)."""
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)           # ← move to next responsible node (lowbit trick)

    def query(self, i):
        """Prefix sum from 1 to i (inclusive)."""
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & (-i)           # ← move to parent (remove lowbit)
        return total

    def range_query(self, l, r):
        """Sum from l to r inclusive (1-indexed)."""
        return self.query(r) - self.query(l - 1)


# Build from existing array in O(n log n):
def build(arr):
    ft = FenwickTree(len(arr))
    for i, val in enumerate(arr):
        ft.update(i + 1, val)       # ← convert to 1-indexed
    return ft
```

> 📝 **Practice:** [Q68 · fenwick-tree](../dsa_practice_questions_100.md#q68--normal--fenwick-tree)


**The lowbit trick explained:**
```
i & (-i)  extracts the lowest set bit of i

i = 6  →  binary: 110  →  lowbit = 010 = 2
i = 12 →  binary: 1100 →  lowbit = 0100 = 4

Each index i is responsible for a range of lowbit(i) elements
```

**Fenwick tree vs Segment tree:**

```
                 Fenwick Tree        Segment Tree
─────────────────────────────────────────────────
Code complexity     Simple (10 lines)   Moderate (30+ lines)
Memory              O(n)                O(4n)
Point update        O(log n)            O(log n)
Range sum           O(log n)            O(log n)
Range min/max       ✗ Not supported     ✓ Supported
Lazy propagation    ✗ Not supported     ✓ Supported
Range update        ✓ With trick        ✓ Native
─────────────────────────────────────────────────
Use Fenwick when: only prefix sum queries + point updates needed
Use Segment when: range min/max, lazy propagation, or range updates
```

**Range update with Fenwick (difference array trick):**

```python
# To support range update [l, r] += val:
# Use two Fenwick trees (advanced pattern)
# Or: maintain difference array in Fenwick tree
ft.update(l, val)        # ← add val at l
ft.update(r + 1, -val)   # ← subtract at r+1
# Then point query at i = ft.query(i)
```

**Complexity:** O(n) build, O(log n) update and query, O(n) space

---

# 🔁 Navigation

Previous:  
[22_bit_manipulation/interview.md](/dsa-complete-mastery/22_bit_manipulation/interview.md)

Next:  
[23_segment_tree/interview.md](/dsa-complete-mastery/23_segment_tree/interview.md)  
[24_disjoint_set_union/theory.md](/dsa-complete-mastery/24_disjoint_set_union/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Bit Manipulation — Interview Q&A](../22_bit_manipulation/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
