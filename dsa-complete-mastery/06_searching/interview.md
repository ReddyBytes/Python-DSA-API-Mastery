# 🎯 Searching — Interview Preparation Guide

> Searching problems test clarity of thinking more than coding ability.
>  
> Interviewers evaluate:
> - Whether you identify if data is sorted
> - Whether you choose the right strategy
> - Whether you implement binary search correctly
> - Whether you handle edge cases without errors
> - Whether you can reason about monotonic functions

Searching questions are precision-based. Small logical mistakes fail solutions.

---

# 🔍 How Searching Questions Usually Appear

Rarely asked as:
“Implement linear search.”

More commonly:

- “Optimize this brute-force approach.”
- “Can we do better than O(n)?”
- “Can we reduce search space?”
- “Find the first/last occurrence.”
- “Find minimum value satisfying condition.”
- “Search in rotated array.”

Recognizing pattern is half the solution.

---

# 🔹 Basic Level Questions (0–2 Years)

## 1️⃣ What is the difference between linear search and binary search?

Linear Search:
- Works on unsorted data
- O(n)

Binary Search:
- Requires sorted data
- O(log n)

Key difference:
Binary search reduces search space by half each step.

---

## 2️⃣ Why does binary search require sorted data?

Binary search eliminates half the array each step.

Without sorted order:
You cannot decide which half to discard.

Sorted order enables directional elimination.

---

## 3️⃣ What is the time complexity of binary search?

Each step halves search space.

If n = 2^k:

After k steps → size becomes 1.

So:
Time complexity = O(log n)

---

## 4️⃣ What is the space complexity of binary search?

Iterative:
O(1)

Recursive:
O(log n) (stack space)

Many candidates forget recursion stack space.

---

## 5️⃣ What are common binary search mistakes?

- Incorrect loop condition (`low < high` vs `<=`)
- Infinite loops
- Wrong mid calculation
- Not updating boundaries correctly
- Not handling edge cases (empty array)

Binary search errors are usually boundary-related.

---

# 🔹 Intermediate Level Questions (2–5 Years)

## 6️⃣ How do you find the first occurrence of an element?

Modified binary search:

When target found:
Continue searching left half.

Core idea:
Do not stop immediately.

Pattern:

- If match found → store index
- Move `high = mid - 1`

Return stored index.

---

## 7️⃣ How do you find the last occurrence?

Same logic but:

When found:
Move `low = mid + 1`

These variations are extremely common.

---

## 8️⃣ What is lower bound and upper bound?

Lower bound:
First element ≥ target.

Upper bound:
First element > target.

These are useful in:

- Range counting problems
- Frequency calculations
- Competitive programming

---

## 9️⃣ What is “search on answer”?

Instead of searching in array,
you search in solution space.

Example:

Find minimum speed such that work finishes within time.

Observation:
If speed works,
all higher speeds also work.

Monotonic condition:

```
False False False True True True
```

Binary search finds first True.

Very common in interviews.

---

## 🔟 How do you search in a rotated sorted array?

Example:

```
[4,5,6,7,0,1,2]
```

At least one half is always sorted.

Steps:

1. Find sorted half.
2. Check if target lies inside.
3. Adjust boundaries.

Time:
O(log n)

Frequently asked question.

---

# 🔹 Advanced Level Questions (5–10 Years)

## 1️⃣1️⃣ When is sorting before searching justified?

If:
You need to search multiple times.

Example:
1 million searches on same dataset.

Better:
Sort once → O(n log n)
Search each → O(log n)

Total far better than repeated linear scans.

Shows preprocessing trade-off reasoning.

---

## 1️⃣2️⃣ How does searching scale in distributed systems?

Binary search assumes random access.

In distributed systems:

- Data partitioned
- Index structures used (B-Trees)
- Hash-based indexing used

Searching strategy depends on storage architecture.

Senior-level awareness required.

---

## 1️⃣3️⃣ When does binary search fail conceptually?

Binary search requires:

- Monotonic property
- Sorted order
- Deterministic decision boundary

If condition not monotonic:
Binary search invalid.

Understanding monotonicity is critical.

---

## 1️⃣4️⃣ How would you debug a failing binary search?

Checklist:

- Print low, mid, high
- Verify boundary update logic
- Check loop condition
- Verify sorted property
- Test edge cases:
  - Empty array
  - Single element
  - All same elements
  - Target not present

Systematic debugging approach matters.

---

## 1️⃣5️⃣ Compare searching strategies for large data systems.

Options:

- Linear scan
- Binary search
- Hash-based lookup
- Tree-based indexing
- Database indexing

Each has trade-offs in:

- Memory
- Update cost
- Query cost
- Scalability

Senior engineers compare beyond algorithm level.

---

# 🔥 Scenario-Based Questions

---

## Scenario 1:
Given 10 million sorted integers, find if 999999 exists.

Expected:
Binary search.

Linear scan unacceptable.

---

## Scenario 2:
Given unsorted data and frequent searches.

Options:

- Sort once + binary search
- Use hash set

Which is better?

Hash set:
O(1) average lookup.

Depends on memory constraints.

Trade-off discussion expected.

---

## Scenario 3:
You must find minimum capacity to ship packages within D days.

Brute force:
Try all capacities → too slow.

Better:
Binary search on answer.

Key:
Capacity feasibility is monotonic.

---

## Scenario 4:
Binary search implementation works for most cases but fails for duplicates.

Likely issue:
Not handling first/last occurrence properly.

---

## Scenario 5:
Searching in linked list using binary search.

Problem:
No random access.

Binary search becomes inefficient.

Linear scan better.

Demonstrates structural awareness.

---

# 🧠 Senior-Level Structured Answer Example

If interviewer asks:

“How do you approach search problems?”

Professional answer:

I first determine whether the data is sorted or can be made sorted efficiently. If unsorted and frequent lookups are required, I consider hashing. If sorted and random access is available, binary search is optimal. For optimization problems with monotonic constraints, I apply binary search on the answer space. I also evaluate preprocessing trade-offs, memory constraints, and data update frequency before finalizing approach.

This shows strategy-based reasoning, not just algorithm recall.

---

# 🎯 Rapid-Fire Revision Points

- Linear search → O(n)
- Binary search → O(log n)
- Sorted data required
- Iterative binary search → O(1) space
- Search on answer uses monotonic property
- Rotated array requires modified binary search
- First/last occurrence are common variations
- Always verify boundary updates

If you can implement binary search without boundary mistakes
and explain when NOT to use it,
you are ready for mid-level and senior search discussions.

