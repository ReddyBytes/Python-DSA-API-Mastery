# 🎯 Heaps — Interview Preparation Guide (Priority Mastery)

> Heap problems test whether you understand **priority-based thinking**.
>
> They are very common in:
> - Top K problems
> - Streaming data
> - Scheduling
> - Graph shortest path
>
> If you see:
> - “K largest”
> - “K smallest”
> - “Top K frequent”
> - “Median of stream”
> - “Priority”
>
> Think: **Heap**

Heaps are one of the most practical interview tools.

---

# 🔎 How Heap Questions Appear in Interviews

Rarely asked:
“Define heap.”

More commonly:

- Kth largest element
- Top K frequent elements
- Merge k sorted lists
- Median from data stream
- Reorganize string
- Task scheduler
- Find smallest range covering elements
- Dijkstra’s algorithm (priority queue)

If problem says:
- “Repeatedly find smallest/largest”
- “Maintain top elements dynamically”
- “Process by priority”

Think heap.

---

# 🧠 How to Respond Before Coding

Instead of:

“I’ll use heap.”

Say:

> “Since we need to repeatedly access the smallest (or largest) element efficiently, a heap provides O(1) access to the top element and O(log n) insertion and deletion.”

This shows you understand why.

---

# 🔹 Basic Level Questions (0–2 Years)

---

**Q1: What is a Heap?**

<details>
<summary>💡 Show Answer</summary>

Professional answer:

A heap is a complete binary tree that satisfies the heap property — either min-heap (parent ≤ children) or max-heap (parent ≥ children).

</details>

<br>

**Q2: What is Time Complexity?**

<details>
<summary>💡 Show Answer</summary>

Insert → O(log n)  
Delete → O(log n)  
Peek → O(1)  
Build heap → O(n)

Mention build heap O(n) — interviewers like that.

</details>

<br>

**Q3: Difference Between Min Heap and Max Heap**

<details>
<summary>💡 Show Answer</summary>

Min Heap:
Smallest at root.

Max Heap:
Largest at root.

Python supports min heap by default.

</details>

<br>

**Q4: Why Heap Stored as Array?**

<details>
<summary>💡 Show Answer</summary>

Because complete tree can be mapped using index formulas:

Left child = 2i + 1  
Right child = 2i + 2  
Parent = (i - 1) // 2  

No pointers required.

Efficient memory usage.

</details>


# 🔹 Intermediate Level Questions (2–5 Years)

---

**Q5: Kth Largest Element**

<details>
<summary>💡 Show Answer</summary>

Approach 1:
Build max heap → pop k times → O(n + k log n)

Approach 2 (better):
Maintain min heap of size k.

For each element:
Push into heap.
If size > k:
Pop smallest.

Root becomes kth largest.

Time:
O(n log k)

Strong candidates mention space optimization.

</details>

<br>

**Q6: Top K Frequent Elements**

<details>
<summary>💡 Show Answer</summary>

Steps:

1. Count frequency using hashmap.
2. Use heap of size k based on frequency.

Time:
O(n log k)

Mention:
Space trade-off.

</details>

<br>

**Q7: Merge K Sorted Lists**

<details>
<summary>💡 Show Answer</summary>

Push first element of each list into heap.

Repeatedly:
Pop smallest.
Push next element from same list.

Time:
O(n log k)

Classic heap pattern.

</details>

<br>

**Q8: Median from Data Stream**

<details>
<summary>💡 Show Answer</summary>

Use two heaps:

- Max heap (lower half)
- Min heap (upper half)

Balance sizes.

Median:
If equal → average of roots
Else → root of larger heap

Time:
Insert O(log n)
Find median O(1)

Advanced but common.

</details>


# 🔹 Advanced Level Questions (5–10 Years)

---

**Q9: Why Build Heap is O(n), Not O(n log n)?**

<details>
<summary>💡 Show Answer</summary>

Because heapify runs bottom-up.

Nodes near bottom require minimal swaps.

Total cost sums to O(n).

Strong candidates can explain amortized reasoning.

</details>

<br>

**Q10: Compare Heap vs Sorting**

<details>
<summary>💡 Show Answer</summary>

Sorting:
O(n log n)

Heap for K largest:
O(n log k)

Heap better when k << n.

Optimization thinking expected.

</details>

<br>

**Q11: Heap in Graph Algorithms**

<details>
<summary>💡 Show Answer</summary>

Dijkstra’s algorithm uses min heap.

Priority queue ensures:

Node with smallest distance processed first.

Time:
O(E log V)

Understanding heap in graph context shows depth.

</details>

<br>

**Q12: When Not to Use Heap**

<details>
<summary>💡 Show Answer</summary>

Avoid heap when:

- Need full sorted order frequently.
- Need range queries.
- Random access required.

Heap gives only top element efficiently.

</details>


# 🔥 Scenario-Based Questions

---

## Scenario 1:

Need top 10 elements from million numbers.

<details>
<summary>💡 Show Answer</summary>

Sorting entire array:
O(n log n) expensive.

Better:
Min heap of size 10 → O(n log 10)

Huge improvement.

</details>
---

## Scenario 2:

Streaming input — cannot store all data.

<details>
<summary>💡 Show Answer</summary>

Heap helpful:
Maintain limited size.

Discuss memory constraints.

</details>
---

## Scenario 3:

Need dynamic median.

<details>
<summary>💡 Show Answer</summary>

Two heap approach.

Explain balancing logic carefully.

</details>
---

## Scenario 4:

Heap solution TLE.

<details>
<summary>💡 Show Answer</summary>

Possible reason:
Using heap incorrectly when k is large.

Maybe sorting is better.

Choose based on constraints.

</details>
---

## Scenario 5:

Data already sorted.

<details>
<summary>💡 Show Answer</summary>

Heap unnecessary.

Simple indexing enough.

Choose wisely.

</details>
---

# 🧠 How to Communicate Like a Strong Candidate

Weak candidate:

“I’ll use heap.”

Strong candidate:

> “Since we need to repeatedly extract the top K elements and K is much smaller than N, maintaining a heap of size K gives us O(n log k) time complexity, which is more efficient than sorting the entire dataset.”

Shows optimization awareness.

---

# 🎯 Interview Cracking Strategy for Heap Problems

1. Identify repeated min/max requirement.
2. Check if K is small relative to N.
3. Decide min-heap or max-heap.
4. Mention time complexity clearly.
5. Consider space complexity.
6. Compare with sorting approach.
7. Dry run small example.
8. Use heapq correctly in Python.

---

# ⚠️ Common Weak Candidate Mistakes

- Using heap when sorting sufficient
- Forgetting to maintain heap size
- Confusing min and max heap
- Incorrect comparator logic
- Not balancing two heaps correctly
- Assuming heap is sorted structure

Heap only guarantees top element order.

---

# 🎯 Rapid-Fire Revision Points

- Heap = complete binary tree
- Insert/delete → O(log n)
- Peek → O(1)
- Build heap → O(n)
- Use for top K problems
- Use for streaming median
- Use for priority scheduling
- Not fully sorted structure
- Choose min or max carefully

---

# 🏆 Final Interview Mindset

Heap problems test:

- Priority thinking
- Optimization instinct
- Trade-off awareness
- Algorithm selection skill

If you can:

- Identify top K patterns quickly
- Explain O(n log k) reasoning
- Balance two heaps confidently
- Compare heap vs sort logically
- Use heap in graph context

You are strong in heap-based interviews.

Heap mastery prepares you for:

- Graph algorithms
- Scheduling systems
- Streaming problems
- Advanced system design

---

# 🔁 Navigation

Previous:  
[16_heaps/theory.md](/dsa-complete-mastery/16_heaps/theory.md)

Next:  
[17_trie/theory.md](/dsa-complete-mastery/17_trie/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Common Mistakes](./common_mistakes.md) &nbsp;|&nbsp; **Next:** [Trie — Theory →](../17_trie/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md)
