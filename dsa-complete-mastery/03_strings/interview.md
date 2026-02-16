# 🎯 Strings — Interview Preparation Guide

> This file prepares you to handle string-related interview discussions
> from entry-level clarity to senior-level optimization and system reasoning.
>  
> Focus: immutability, performance, algorithmic patterns, and production impact.

---

# 🔹 Basic Level Questions (0–2 Years)

## 1️⃣ What is a String in Python?

A string is an immutable sequence of characters.

Key properties:
- Ordered
- Indexed
- Iterable
- Immutable

Immutability means once created, it cannot be modified in place.

---

## 2️⃣ Why Are Strings Immutable?

Reasons:

1. Safe to use as dictionary keys (hash stability)
2. Thread safety
3. Memory optimization (interning)
4. Predictable behavior

Interview Tip:
Mention hashing stability — it shows deeper understanding.

---

## 3️⃣ What Is the Time Complexity of String Operations?

| Operation | Complexity |
|------------|------------|
| Indexing | O(1) |
| Slicing | O(k) |
| Concatenation | O(n + m) |
| Length | O(1) |
| Iteration | O(n) |
| Comparison | O(n) worst case |

You must explain that slicing creates a new string.

---

## 4️⃣ Why Is Repeated String Concatenation Slow?

Example:

```python
result = ""
for char in data:
    result += char
```

Each concatenation creates a new string and copies previous content.

If n characters → O(n²)

Optimized version:

```python
chars = []
for char in data:
    chars.append(char)

result = "".join(chars)
```

Time → O(n)

This is a common interview discussion.

---

## 5️⃣ What Is String Interning?

Python may store identical strings in the same memory location.

Example:

```python
a = "hello"
b = "hello"
```

Sometimes `a is b` → True

Used for optimization.

Never rely on it in business logic.

---

# 🔹 Intermediate Level Questions (2–5 Years)

## 6️⃣ How Do You Check If a String Is a Palindrome?

Approach 1:

Reverse string:

```python
s == s[::-1]
```

Time: O(n)
Space: O(n)

Approach 2 (better):

Two pointers:

```python
left = 0
right = len(s) - 1
```

Move inward.

Time: O(n)
Space: O(1)

Interviewers prefer in-place logic (two pointers).

---

## 7️⃣ How Do You Detect Anagrams?

Approach 1:
Sort both strings → O(n log n)

Approach 2:
Use frequency count (hash map) → O(n)

Better solution:
Use frequency map for linear time.

Discuss space-time trade-off.

---

## 8️⃣ How Do You Find First Non-Repeating Character?

Approach:

1. Count frequency using dictionary.
2. Scan again to find frequency = 1.

Time: O(n)
Space: O(n)

Must mention two-pass strategy.

---

## 9️⃣ What Is the Complexity of `"substring" in string`?

Python uses optimized search algorithm internally.

Worst case: O(nm)

For large-scale systems, discuss KMP for guaranteed O(n + m).

---

## 🔟 What Are Common String Patterns in Interviews?

Most string problems fall into:

1. Two pointers
2. Sliding window
3. Frequency counting
4. Substring search
5. Prefix/suffix problems
6. Stack-based validation (parentheses)

Recognizing pattern quickly is crucial.

---

# 🔹 Advanced Level Questions (5–10 Years)

## 1️⃣1️⃣ How Would You Optimize Substring Search?

Naive approach:
O(nm)

Optimized:
- KMP → O(n + m)
- Rabin-Karp (rolling hash)
- Boyer-Moore (practical performance)

Senior candidates should at least explain KMP conceptually.

---

## 1️⃣2️⃣ How Do You Handle Very Large Strings (GB-level)?

Consider:

- Streaming instead of loading fully
- Processing in chunks
- Memory-mapped files
- Avoiding unnecessary copies

Senior-level interviews test scalability thinking.

---

## 1️⃣3️⃣ What Happens Internally When You Slice a String?

```python
s[2:5]
```

Python:
- Allocates new string
- Copies substring

Time: O(k)
Space: O(k)

Large repeated slicing can cause memory pressure.

---

## 1️⃣4️⃣ Compare String vs Bytearray

String:
- Immutable
- Unicode
- Safer

Bytearray:
- Mutable
- Efficient for binary manipulation

Use bytearray in:
- Networking
- File processing
- Binary protocols

Shows production awareness.

---

## 1️⃣5️⃣ What Are Trade-offs Between Different Approaches?

Example:
Check if two strings are anagrams.

Method 1:
Sort → O(n log n), low extra space

Method 2:
Hash map → O(n), extra memory

Decision depends on:
- Memory constraints
- Input size
- System performance goals

---

# 🔥 Scenario-Based Questions

---

## Scenario 1:
You need to process 50 million log entries (strings).

What should you avoid?

Avoid:
- Repeated concatenation
- Unnecessary slicing
- Loading entire file into memory

Prefer:
- Streaming
- Iterative processing
- Generators

---

## Scenario 2:
A service slows down when building a large response string.

Possible issue:
Using += in loop.

Fix:
Use list + join().

---

## Scenario 3:
You must check if a very large string contains a pattern repeatedly.

Brute force search too slow.

Solution:
Use KMP or rolling hash.

Discuss complexity improvement.

---

## Scenario 4:
Memory usage spikes during substring operations.

Possible cause:
Creating too many intermediate strings.

Solution:
Use indices instead of slicing repeatedly.

---

## Scenario 5:
Your system processes user inputs in multiple languages.

What should you consider?

- Unicode normalization
- Encoding issues
- Case folding vs lower()
- Multibyte character behavior

Senior engineers discuss internationalization.

---

# 🧠 Senior-Level Structured Answer Example

If interviewer asks:

“How do you approach string problems?”

Professional answer:

I first analyze constraints and expected input size. I check whether the problem involves substring search, frequency counting, or window-based constraints. Based on that, I select appropriate patterns like sliding window or hashing. I avoid repeated string concatenation due to immutability and ensure space optimization where required. For large-scale inputs, I consider streaming or chunk-based processing to avoid memory overhead.

This shows clarity and system awareness.

---

# 🎯 Rapid-Fire Revision Points

- Strings are immutable.
- Indexing is O(1).
- Slicing creates new string.
- Avoid += in loops.
- Use join() for efficient concatenation.
- Sliding window solves many substring problems.
- Hash maps optimize frequency problems.
- KMP provides guaranteed linear search.
- Consider encoding and memory at scale.

If you can confidently explain these topics with optimization reasoning and trade-offs, you are well-prepared for string discussions in product-based and senior-level interviews.

