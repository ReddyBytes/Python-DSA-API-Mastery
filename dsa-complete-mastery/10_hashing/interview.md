# 🎯 Hashing — Interview Preparation Guide (From O(n²) to O(n) Thinking)

> Hashing is the topic that separates average candidates from strong candidates.
>
> Why?
>
> Because many brute-force solutions are O(n²),
> and hashing reduces them to O(n).
>
> Interviewers use hashing problems to test:
> - Optimization instinct
> - Space-time trade-off understanding
> - Edge-case handling
> - Collision awareness
> - System-level reasoning

Master hashing, and you unlock speed.

---

# 🔎 How Hashing Questions Appear in Interviews

Rarely asked as:
“Explain hash table.”

More commonly:

- Two Sum
- Find duplicates
- Group anagrams
- Subarray sum equals K
- Longest consecutive sequence
- Design LRU cache
- Count frequency of elements
- Detect cycle in graph (with visited set)

If you see:
- “Find in O(n)”
- “Avoid nested loops”
- “Check existence quickly”
- “Frequency counting”

Think: **Hashing**

---

# 🧠 How to Respond Before Coding

Instead of:

“I’ll use a dictionary.”

Say:

> “Since we need constant-time lookups to avoid nested iteration, I’ll use a hash map to store previously seen elements.”

This shows reasoning, not memorization.

---

# 🔹 Basic Level Questions (0–2 Years)

---

**Q1: What is hashing?**

<details>
<summary>💡 Show Answer</summary>

Professional answer:

Hashing is a technique that uses a hash function to map keys to indices in a hash table, enabling average O(1) insertion, deletion, and lookup operations.

Keep it concise.

</details>

<br>

**Q2: Why is hash table lookup O(1)?**

<details>
<summary>💡 Show Answer</summary>

Because instead of searching,
we compute index using hash function.

But clarify:
O(1) average case.
O(n) worst case (due to collisions).

Mentioning worst case shows maturity.

</details>

<br>

**Q3: What is a collision?**

<details>
<summary>💡 Show Answer</summary>

When two keys map to the same index.

Example:

```
hash("cat") = 5
hash("tac") = 5
```

Collision resolution required.

</details>

<br>

**Q4: How are collisions handled?**

<details>
<summary>💡 Show Answer</summary>

Two common approaches:

- Separate chaining (linked list per index)
- Open addressing (probing for next slot)

Strong candidates mention both.

</details>

<br>

**Q5: Why must keys be immutable?**

<details>
<summary>💡 Show Answer</summary>

If key changes,
its hash changes,
index becomes incorrect.

Hence:
- Strings → allowed
- Tuples → allowed (if immutable elements)
- Lists → not allowed

This is frequently asked.

</details>


# 🔹 Intermediate Level Questions (2–5 Years)

---

**Q6: Two Sum — How to Respond**

<details>
<summary>💡 Show Answer</summary>

Instead of brute force:

Say:

> “I’ll iterate once and store elements in a hash map. For each element, I’ll check if (target - current) already exists.”

Time: O(n)  
Space: O(n)

Explain logic clearly.

</details>

<br>

**Q7: How to Find Duplicates in O(n)?**

<details>
<summary>💡 Show Answer</summary>

Use set.

Traverse:
If element already in set → duplicate found.

Time: O(n)

Explain space trade-off.

</details>

<br>

**Q8: Group Anagrams**

<details>
<summary>💡 Show Answer</summary>

Key idea:
Anagrams share same sorted form.

Use sorted string as key:

```python
d[tuple(sorted(word))].append(word)
```

Time:
O(n k log k)

Strong candidates explain why tuple is used (hashable).

</details>

<br>

**Q9: Subarray Sum Equals K**

<details>
<summary>💡 Show Answer</summary>

Use prefix sum + hashmap.

Store:
prefix_sum → frequency.

If current_sum - k exists:
Valid subarray found.

Time: O(n)

This is a classic hashing + prefix pattern.

</details>

<br>

**Q10: Longest Consecutive Sequence**

<details>
<summary>💡 Show Answer</summary>

Store numbers in set.

For each number:
If (num - 1) not in set → start counting forward.

Avoid repeated counting.

Time: O(n)

This tests optimization instinct.

</details>


# 🔹 Advanced Level Questions (5–10 Years)

---

**Q11: Explain Load Factor**

<details>
<summary>💡 Show Answer</summary>

Load factor = n / table_size.

If too high:
Collisions increase.

Python automatically resizes.

Senior candidates mention resizing cost is amortized.

</details>

<br>

**Q12: When Does Hashing Fail?**

<details>
<summary>💡 Show Answer</summary>

Worst case:
All elements collide.

Time:
O(n)

Good hash function minimizes this risk.

Mention adversarial inputs.

</details>

<br>

**Q13: Ordered vs Unordered Maps**

<details>
<summary>💡 Show Answer</summary>

Python 3.7+ preserves insertion order.

But hash table itself is unordered by nature.

If sorted order required:
Use tree-based map instead.

</details>

<br>

**Q14: How Hashing Impacts Memory**

<details>
<summary>💡 Show Answer</summary>

Hash tables require extra space:

- Array for buckets
- Linked lists or probing space

Trade-off:
Space for speed.

Senior candidates always mention this.

</details>

<br>

**Q15: Hashing in Real Systems**

<details>
<summary>💡 Show Answer</summary>

Examples:

- Caching (Redis)
- Session storage
- Database indexing
- Symbol tables in compilers
- LRU cache (hash map + doubly linked list)

Strong candidates connect DSA to real systems.

</details>


# 🔥 Scenario-Based Interview Questions

---

## Scenario 1:

Brute-force solution is O(n²).
Input size = 10⁵.

<details>
<summary>💡 Show Answer</summary>

Will it pass?

No.

Use hashing to reduce to O(n).

</details>
---

## Scenario 2:

You need to count frequencies of millions of words.

<details>
<summary>💡 Show Answer</summary>

Approach:
Use dictionary.

Concern:
Memory usage.

Discuss trade-offs.

</details>
---

## Scenario 3:

Hash table performance degraded suddenly.

<details>
<summary>💡 Show Answer</summary>

Possible reasons:

- Poor hash function
- Too many collisions
- Load factor too high
- Adversarial input

Explain debugging approach.

</details>
---

## Scenario 4:

Need to design LRU cache.

<details>
<summary>💡 Show Answer</summary>

Correct answer:

Use:
- Hash map for O(1) lookup
- Doubly linked list for O(1) insert/delete

Explain why both needed.

</details>
---

## Scenario 5:

Need to check if two arrays share common element.

<details>
<summary>💡 Show Answer</summary>

Naive:
Nested loop → O(n²)

Better:
Store one array in set → O(n)

Then check second array.

Total:
O(n)

</details>
---

# 🧠 How to Communicate Like a Strong Candidate

Weak candidate:

“I’ll use dictionary.”

Strong candidate:

> “To reduce time complexity from quadratic to linear, I’ll maintain a hash map to store previously processed elements. This allows constant-time membership checks.”

Communication reflects clarity.

---

# 🎯 Interview Cracking Strategy for Hashing

1. Identify if nested loops can be avoided.
2. Look for existence-check pattern.
3. Look for frequency-count pattern.
4. Consider prefix-sum + hashmap pattern.
5. State time & space complexity.
6. Mention worst-case scenario.
7. Discuss space trade-off.

Hashing is often the first optimization step.

---

# ⚠️ Common Weak Candidate Mistakes

- Forgetting worst-case O(n)
- Ignoring space complexity
- Using list instead of set for membership
- Forgetting to handle duplicates properly
- Not considering load factor

---

# 🎯 Rapid-Fire Revision Points

- Hashing → O(1) average lookup
- Collisions must be handled
- Load factor impacts performance
- Keys must be immutable
- Two-sum uses hashmap
- Prefix sum + hashmap solves subarray problems
- LRU uses hashmap + linked list
- Hashing trades space for time

---

# 🏆 Final Interview Mindset

Hashing is about thinking:

“How do I avoid scanning everything?”

If you can:

- Spot O(n²) patterns quickly
- Replace them with hash-based lookup
- Explain space-time trade-offs
- Mention collision and worst case
- Connect to real systems

You are ready for strong performance in product-based interviews.

---

# 🔁 Navigation

Previous:  
[10_hashing/theory.md](/dsa-complete-mastery/10_hashing/theory.md)

Next:  
[11_two_pointers/theory.md](/dsa-complete-mastery/11_two_pointers/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Common Mistakes](./common_mistakes.md) &nbsp;|&nbsp; **Next:** [Two Pointers — Theory →](../11_two_pointers/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Collision Handling](./collision_handling.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md)
