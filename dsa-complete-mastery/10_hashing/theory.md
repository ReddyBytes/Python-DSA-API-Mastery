# 📘 Hashing — The Power of Instant Lookup

> Hashing is about one thing:
>
> **Turning search into instant access.**
>
> Without hashing, many real-world systems would be painfully slow.

Hashing is not just a data structure.
It is a strategy to reduce lookup time.

---

# 1️⃣ Real Life Analogy — Library Without and With Hashing

Imagine a library with 1 million books.

### ❌ Without Hashing

You search for a book by scanning shelves one by one.

Time grows as number of books grows.

This is linear search → O(n)

---

### ✅ With Hashing

Each book has a unique code.
You directly go to that shelf.

Instant access.

That is hashing.

Instead of searching,
you compute the location.

---

# 2️⃣ What Is Hashing?

Hashing uses a function called a **hash function**.

The hash function:

Input → Key  
Output → Index

Example:

```
hash("apple") → 4
hash("banana") → 7
```

Index tells where data should be stored.

This allows:

Insertion → O(1) average  
Search → O(1) average  
Deletion → O(1) average  

Hashing is about fast lookup.

---

# 3️⃣ Hash Table Structure

Internally:

```
Index: 0 1 2 3 4 5 6 7
Value: - - - - A - - B
```

Hash function decides index.

But there is a problem.

Two keys may produce same index.

That is called collision.

---

# 4️⃣ Collision — The Core Challenge

Example:

```
hash("cat") → 3
hash("tac") → 3
```

Both want index 3.

We must resolve collision.

Two main strategies:

---

## 🔹 Separate Chaining

Each index stores a linked list.

```
Index 3 → cat → tac → act
```

Time complexity:
O(1) average
O(n) worst case

---

## 🔹 Open Addressing

If index occupied,
find next available slot.

Techniques:
- Linear probing
- Quadratic probing
- Double hashing

---

# 5️⃣ Load Factor

Load factor = (number of elements) / (table size)

If load factor becomes high:
Collisions increase.

When load factor crosses threshold (e.g., 0.7):
Table resizes.

Resizing:
- Create bigger table
- Rehash all elements

This is why hash operations are amortized O(1).

---

# 6️⃣ Hashing in Python (Dictionary & Set)

Python provides:

- dict
- set

Both use hash tables internally.

Example:

```python
d = {}
d["apple"] = 10
```

Lookup:

```python
d["apple"]
```

Average:
O(1)

---

# 7️⃣ Why Strings Are Immutable (Connection to Hashing)

Hash tables require keys to be immutable.

Why?

If key changes after hashing,
its index becomes incorrect.

That’s why:

- Strings → immutable
- Tuples → hashable
- Lists → not hashable

Understanding this shows depth.

---

# 8️⃣ Common Hashing Patterns in Interviews

Most problems using hashing involve:

- Frequency counting
- Duplicate detection
- Two-sum problem
- Anagram checking
- Subarray sum
- Grouping elements

Hashing reduces nested loops.

---

# 9️⃣ Example — Two Sum

Without hashing:

Double loop → O(n²)

With hashing:

Store visited numbers in set/dictionary.

For each element:
Check if (target - current) exists.

Time:
O(n)

Hashing transforms problem.

---

# 🔟 Space-Time Trade-Off

Hashing trades space for speed.

You use extra memory
to reduce time complexity.

Senior-level understanding:
Always consider memory constraints.

---

# 1️⃣1️⃣ Worst Case of Hashing

If many collisions occur:

Hash table degrades to linked list.

Worst case:
O(n)

Good hash function minimizes collision probability.

---

# 1️⃣2️⃣ Hash Function Properties

A good hash function should:

- Be fast
- Distribute keys uniformly
- Minimize collisions
- Be deterministic

Poor hash functions cause performance issues.

---

# 1️⃣3️⃣ Real-World Usage of Hashing

Hashing powers:

- Database indexing
- Caching systems
- Password storage (hashed)
- Routing tables
- Compilers (symbol tables)
- Blockchain (cryptographic hashing)

Hashing is foundational to modern computing.

---

# 1️⃣4️⃣ When NOT to Use Hashing

Avoid hashing when:

- Order matters
- Sorted traversal required
- Memory is highly constrained
- Deterministic iteration order needed

Use tree-based structures instead.

---

# 📌 Final Understanding

Hashing:

- Enables instant lookup
- Uses hash function to compute index
- Handles collisions carefully
- Trades memory for speed
- Powers dictionaries and sets

It is one of the most powerful tools in algorithm design.

If you master hashing,
many medium-level problems become easy.

---

# 🔁 Navigation

Previous:  
[09_queue/theory.md](/dsa-complete-mastery/09_queue/theory.md)

Next:  
[10_hashing/interview.md](/dsa-complete-mastery/10_hashing/interview.md)  
[11_two_pointers/theory.md](/dsa-complete-mastery/11_two_pointers/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Queue — Interview Q&A](../09_queue/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Collision Handling](./collision_handling.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
