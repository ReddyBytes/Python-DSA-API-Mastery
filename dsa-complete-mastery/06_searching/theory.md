# 📘 Searching in Python — Complete Theory (Zero to Advanced)

> Searching is not just about finding an element.
> It is about choosing the right strategy based on data order and constraints.

Every search problem begins with one critical question:

Is the data sorted?

Your entire approach depends on this.

---

# 1️⃣ The Two Worlds of Searching

Searching problems fall into two major categories:

1. Searching in Unsorted Data
2. Searching in Sorted Data

If unsorted → options are limited.
If sorted → powerful optimizations become available.

Understanding this distinction is fundamental.

---

# 2️⃣ Linear Search — The Baseline Strategy

When data is unsorted:

You must scan one-by-one.

Example:

```
[4, 9, 2, 7, 1]
```

Searching for 7:
Check 4 → no  
Check 9 → no  
Check 2 → no  
Check 7 → yes  

Time Complexity:
O(n)

Best Case:
O(1)

Worst Case:
O(n)

Linear search is unavoidable in unsorted arrays.

---

# 3️⃣ Why Binary Search Is Powerful

Binary search only works if:

Data is sorted.

Key idea:
Reduce search space by half each step.

Example:

```
[1, 3, 5, 7, 9, 11, 13]
```

Searching 9:

Step 1:
Check middle (7)

Step 2:
9 > 7 → search right half

Step 3:
Check middle (11)

Step 4:
9 < 11 → search left half

Space reduced each step.

Time:
O(log n)

---

# 4️⃣ Binary Search — Core Conditions

Binary search requires:

- Sorted data
- Random access (arrays, not linked lists)

Basic structure:

```python
low = 0
high = len(arr) - 1

while low <= high:
    mid = (low + high) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        low = mid + 1
    else:
        high = mid - 1
```

---

# 5️⃣ Common Binary Search Mistakes

1. Infinite loop (wrong boundary updates)
2. Using `low < high` instead of `<=`
3. Overflow in other languages (low + high issue)
4. Off-by-one errors
5. Forgetting sorted condition

Binary search is simple in concept,
but error-prone in implementation.

---

# 6️⃣ Variations of Binary Search (Important)

Binary search is rarely asked directly.
Variations are common.

---

## 🔹 First Occurrence

Find first index of target in sorted array.

Key idea:
When found,
move left to check earlier occurrence.

---

## 🔹 Last Occurrence

When found,
move right to check later occurrence.

---

## 🔹 Lower Bound

First element ≥ target.

---

## 🔹 Upper Bound

First element > target.

These are extremely common in interviews.

---

# 7️⃣ Search on Answer (Advanced Pattern)

Instead of searching in array,
you search in answer space.

Example:

Find minimum value that satisfies condition.

Condition is monotonic:

```
False False False True True True
```

Binary search can find transition point.

This pattern appears in:

- Capacity problems
- Scheduling
- Minimum speed problems
- Allocation problems

Understanding monotonic behavior is critical.

---

# 8️⃣ Time Complexity Comparison

| Method | Requirement | Time |
|--------|------------|------|
| Linear | None | O(n) |
| Binary | Sorted | O(log n) |

Binary search is exponentially faster for large n.

Example:

n = 1,000,000

Linear → 1,000,000 checks  
Binary → ~20 checks  

Difference is massive.

---

# 9️⃣ Searching in Rotated Sorted Array

Array is sorted but rotated.

Example:

```
[4,5,6,7,0,1,2]
```

Modified binary search required.

Key idea:
One half is always sorted.
Identify sorted half.
Decide where target lies.

Time:
O(log n)

Common interview problem.

---

# 🔟 Searching in 2D Matrix

Matrix where:

- Rows sorted
- Columns sorted

Approaches:

1. Flatten + binary search
2. Start top-right and eliminate rows/columns

Time:
O(n + m) or O(log(nm))

---

# 1️⃣1️⃣ Searching in Real Systems

Searching appears in:

## 🔹 Databases
Index-based lookup → binary search in B-trees.

## 🔹 File Systems
Directory lookups.

## 🔹 Search Engines
Index structures enable fast retrieval.

## 🔹 Networking
Routing tables.

Binary search principles power indexing structures.

---

# 1️⃣2️⃣ When NOT to Use Binary Search

Avoid when:

- Data not sorted
- Data changes frequently
- Structure does not allow random access (linked list)

Sorting just to binary search may not always be optimal.

---

# 1️⃣3️⃣ Space Complexity

Iterative binary search:
O(1)

Recursive binary search:
O(log n) stack space

Be aware of this distinction.

---

# 1️⃣4️⃣ Performance Thinking

If n = 10⁶:

Linear search:
Too slow if repeated many times.

Binary search:
Very efficient.

Repeated searching scenario:
Sort once → O(n log n)
Search multiple times → O(log n) each

Often worth preprocessing.

---

# 📌 Final Perspective

Searching is about:

- Understanding data order
- Choosing strategy
- Avoiding unnecessary scanning
- Leveraging monotonic behavior
- Minimizing comparisons

Binary search is one of the most important algorithms in computer science.

Mastering searching prepares you for:

- Two pointers
- Sliding window
- Heaps
- Greedy problems
- Many optimization problems

Searching is where logic precision matters most.

