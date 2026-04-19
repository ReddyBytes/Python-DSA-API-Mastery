# 📘 Strings in Python — Complete Theory (Zero to Advanced)

> This file builds a deep understanding of strings from fundamentals
> to advanced problem-solving perspective.
>  
> Focus: memory behavior, performance implications, manipulation patterns,
> and real-world engineering usage.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
string immutability · indexing and slicing · concatenation pitfall (O(n²)) · two-pointer patterns

**Should Learn** — Important for real projects, comes up regularly:
string interning · character encoding · split/reverse/replace operations

**Good to Know** — Useful in specific situations, not always tested:
palindrome checking patterns · basic substring search

**Reference** — Know it exists, look up syntax when needed:
KMP algorithm · rolling hash · Rabin-Karp · suffix arrays

---

# 1️⃣ What Is a String?

A string is a sequence of characters.

In Python:

```python
s = "hello"
```

Internally, a string is an **ordered sequence of characters stored in memory**.

Important characteristics:

- Ordered
- Indexed
- Immutable
- Iterable

That one word — **immutable** — defines most of its behavior.

---

# 2️⃣ String as an Array of Characters

Conceptually:

```
Index:   0   1   2   3   4
Value:   h   e   l   l   o
```

You can access:

```python
s[0]  # 'h'
```

Time complexity: O(1)

Because string indexing works like array indexing.

---

# 3️⃣ Why Strings Are Immutable

In Python, once a string is created, it cannot be modified.

Example:

```python
s = "hello"
s[0] = "H"   # Error
```

Why immutability?

1. Memory safety
2. Hashing stability (important for dictionaries)
3. Thread safety
4. Performance optimization (string interning)

If strings were mutable, hashing and dictionary keys would break.

---

# 4️⃣ What Happens When You Modify a String?

When you write:

```python
s = "hello"
s = s + " world"
```

Python does not modify original string.

It:

1. Creates new string
2. Copies old content
3. Appends new content
4. Reassigns reference

So concatenation creates a new object.

This is important for performance.

---

# 5️⃣ Time Complexity of String Operations

| Operation | Complexity |
|------------|------------|
| Indexing | O(1) |
| Slicing | O(k) |
| Concatenation | O(n + m) |
| Length | O(1) |
| Iteration | O(n) |
| Searching (in operator) | O(n) |

Important insight:
Slicing creates new string → O(k), not O(1).

---

# 6️⃣ Why Repeated Concatenation Is Dangerous

Example:

```python
result = ""
for char in data:
    result += char
```

Each concatenation:
- Creates new string
- Copies entire previous content

If n characters:

Total complexity becomes O(n²)

Better approach:

```python
result = []
for char in data:
    result.append(char)

final = "".join(result)
```

join() builds string efficiently in O(n).

This is a very common interview discussion.

---

# 7️⃣ String Interning

Python optimizes small strings.

Example:

```python
a = "hello"
b = "hello"
```

Sometimes both refer to same memory location.

This is called **string interning**.

It improves memory efficiency and speed.

But never rely on it in logic.

---

# 8️⃣ Memory Representation

Strings in Python are Unicode.

Each character:
- Can take different number of bytes
- Optimized internally depending on character set

Unlike C:
Strings are not null-terminated arrays.

Python stores:
- Length
- Hash
- Character data

Length retrieval is O(1).

---

# 9️⃣ Common String Operations

## 1. Slicing

```python
s[1:4]
```

Creates new string.

Time: O(k)

---

## 2. Reverse String

```python
s[::-1]
```

Creates new reversed string.

Time: O(n)

---

## 3. Split

```python
s.split(" ")
```

Returns list of substrings.

Time: O(n)

---

## 4. Replace

```python
s.replace("a", "b")
```

Creates new string.

Time: O(n)

---

# 🔟 String Comparison

```python
"abc" == "abc"
```

Python compares lexicographically.

Worst case complexity: O(n)

Stops early if mismatch found.

---

# 1️⃣1️⃣ String vs List of Characters

| Feature | String | List of Characters |
|----------|---------|------------------|
| Mutable | ❌ | ✅ |
| Indexing | O(1) | O(1) |
| Concatenation | Expensive | Cheap |
| Memory | Efficient | Slightly more |

If frequent modifications needed:
Convert to list.

---

# 1️⃣2️⃣ Important Interview Patterns with Strings

Most string problems fall into patterns:

1. Two pointers
2. Sliding window
3. Frequency counting (hashing)
4. Palindrome checking
5. Substring search
6. Anagram detection
7. Prefix/suffix comparison

Recognizing pattern is critical.

---

# 1️⃣3️⃣ Palindrome Checking

Efficient method:

Two pointers:

```python
left = 0
right = len(s) - 1
```

Move inward.

Time: O(n)
Space: O(1)

Better than reversing string (extra memory).

---

# 1️⃣4️⃣ Substring Search

Basic method:
Linear scan → O(nm)

Optimized algorithms:
- KMP → O(n + m)
- Rabin-Karp
- Boyer-Moore

For senior roles, knowing at least KMP is expected.

---

# 1️⃣5️⃣ Space Complexity Considerations

String of size n:
Space = O(n)

But operations like slicing:
Create additional O(k) memory.

Recursive string problems:
Add stack space.

---

# 1️⃣6️⃣ When NOT To Use Strings Directly

Avoid direct string concatenation in loops.

Avoid string-heavy processing for massive data:
Consider:
- Streaming
- Byte arrays
- Memory-efficient structures

---

# 1️⃣7️⃣ Real-World Usage of Strings

Strings are everywhere:

## 🔹 Web APIs
Requests and responses are strings (JSON).

## 🔹 Logs
Application logs are strings.

## 🔹 Database Queries
SQL queries are strings.

## 🔹 File Processing
Text files are string streams.

## 🔹 Configuration
Environment variables are strings.

Efficient string handling is essential for backend engineering.

---

# 1️⃣8️⃣ Common Developer Mistakes

- Using += in loops
- Forgetting immutability
- Confusing shallow copy behavior
- Ignoring encoding issues
- Not handling edge cases (empty string)

---

# 1️⃣9️⃣ Performance Estimation

If string length = 10⁵:

- O(n²) operations → too slow
- O(n log n) → acceptable
- O(n) → ideal

Always check constraints before choosing approach.

---

# 2️⃣0️⃣ Advanced Topics (For Senior Roles)

- KMP algorithm
- Rolling hash
- Trie-based prefix search
- Suffix arrays (conceptual)
- Memory-efficient streaming parsing

These are expected for high-level product roles.

---

# 📌 Final Summary

Strings are:

- Immutable sequences of characters
- Indexed and iterable
- Backed by contiguous memory
- Optimized for read-heavy operations

They are powerful,
but expensive for repeated modifications.

Understanding immutability,
memory behavior,
and algorithmic patterns
is essential for mastering string problems.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Arrays — Interview Q&A](../02_arrays/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
