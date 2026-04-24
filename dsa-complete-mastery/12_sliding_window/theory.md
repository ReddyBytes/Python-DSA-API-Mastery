# 📘 Sliding Window — The Magic Moving Frame

> Imagine you are looking at the world through a small window.
> You can move the window.
> You can expand it.
> You can shrink it.
>
> But you never rebuild the entire world again.
>
> That is Sliding Window.

Sliding Window is not a data structure.
It is a way of thinking.

It transforms slow O(n²) substring and subarray problems
into fast O(n) solutions.

> 📝 **Practice:** [Q70 · sliding-window-deque](../dsa_practice_questions_100.md#q70--thinking--sliding-window-deque)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
fixed-size window · variable-size window · window expansion and contraction

**Should Learn** — Important for real projects, comes up regularly:
state maintenance in window · longest substring without repeating chars · minimum window substring

**Good to Know** — Useful in specific situations, not always tested:
sliding window maximum (deque optimization) · window vs two pointers distinction

**Reference** — Know it exists, look up syntax when needed:
categorical sliding window · multi-pointer variants

---

# 🏠 1️⃣ Real Life Story — Watching Through a Window

Imagine you are inside a train.

You look outside through your window.

The window shows only part of the scenery.

As train moves:

- The window moves forward.
- Old scenery disappears.
- New scenery appears.

You don’t restart looking from beginning.
You just slide forward.

That is sliding window.

---

# 🍫 2️⃣ Chocolate Bar Story — Maximum Sweetness

Imagine you have chocolates:

```
[2, 1, 5, 1, 3, 2]
```

You want to find:

Maximum sum of 3 consecutive chocolates.

Brute force way:

Check every group of 3.

That means:

(2,1,5)
(1,5,1)
(5,1,3)
(1,3,2)

This is O(nk).

But sliding window says:

Don’t recompute from scratch.

Step 1:
Take first 3 → sum = 8

Step 2:
Remove 2
Add next element (1)

New sum = 8 - 2 + 1 = 7

You reuse previous work.

You slide forward.

That reduces complexity to O(n).

---

# 🧠 3️⃣ Core Idea of Sliding Window

Instead of:

Rebuilding subarray every time,

You:

1. Maintain a window
2. Expand right boundary
3. Shrink left boundary when needed
4. Maintain some property (sum, count, max, etc.)

Window has two pointers:

```
left → start
right → end
```

Window moves intelligently.

---

# 🔵 4️⃣ Two Types of Sliding Window

---

## 🔹 Fixed Size Window

Window size is constant.

Example:
Find max sum of k elements.

Window size always k.

Only slides forward.

> 📝 **Practice:** [Q24 · sliding-window-fixed](../dsa_practice_questions_100.md#q24--code--sliding-window-fixed)

---

## 🔹 Variable Size Window

Window grows and shrinks dynamically.

Example:
Smallest subarray with sum ≥ target.

Window expands until condition satisfied,
then shrinks to optimize.

This is more powerful.

> 📝 **Practice:** [Q25 · sliding-window-variable](../dsa_practice_questions_100.md#q25--thinking--sliding-window-variable)

---

# 📏 5️⃣ Fixed Window — Step by Step

Example:

```
arr = [4, 2, 1, 7, 8, 1, 2, 8]
k = 3
```

Step 1:
Compute first 3 → 4+2+1 = 7

Step 2:
Slide:
Remove 4
Add 7
New sum = 7 - 4 + 7 = 10

Step 3:
Slide:
Remove 2
Add 8
New sum = 10 - 2 + 8 = 16

You never recompute full sum again.

Time:
O(n)

Space:
O(1)

---

# 🌊 6️⃣ Variable Window — Growing and Shrinking

Imagine you are collecting water.

You keep adding water (expand right).

When bucket overflows (condition satisfied),
you start removing water from left.

Example:

Smallest subarray with sum ≥ 7

```
[2, 3, 1, 2, 4, 3]
```

Process:

Add 2 → sum=2  
Add 3 → sum=5  
Add 1 → sum=6  
Add 2 → sum=8 (≥7)

Now shrink:

Remove 2 → sum=6 (stop shrinking)

Continue expanding.

This grow-shrink behavior is sliding window magic.

---

# 🎯 7️⃣ Why Sliding Window Is So Powerful

Without sliding window:

Nested loops:
O(n²)

With sliding window:

Each element:
- Enters window once
- Leaves window once

Total operations:
≤ 2n

Time:
O(n)

That’s massive improvement.

---

# 🔤 8️⃣ Sliding Window in Strings

Example:

Longest substring without repeating characters.

You maintain:

- Set of characters inside window
- Expand right pointer
- If duplicate appears:
  shrink left until duplicate removed

Window always contains unique characters.

This is variable window.

---

# 🧩 9️⃣ Common Sliding Window Problems

- Maximum sum subarray of size k
- Longest substring without repeating characters
- Minimum window substring
- Smallest subarray with given sum
- Permutation in string
- Sliding window maximum (deque based)
- Count occurrences of anagram

Most substring problems use sliding window.

---

# 🏃 1️⃣0️⃣ Sliding Window vs Two Pointers

Two pointers:
Movement without maintaining internal state.

Sliding window:
Two pointers + maintained property (sum, set, map, etc.)

Sliding window is enhanced two-pointer technique.

---

# 🧮 1️⃣1️⃣ Maintaining Window State

Window often maintains:

- Current sum
- Character frequency
- Count of distinct elements
- Maximum value
- Minimum value

Instead of recalculating,
you update incrementally.

That is optimization.

---

# ⚠️ 1️⃣2️⃣ Common Mistakes

- Forgetting to shrink window
- Infinite loops
- Not updating state when shrinking
- Mismanaging duplicate characters
- Incorrect boundary conditions

Sliding window requires careful logic.

---

# 🧠 1️⃣3️⃣ Real Life Applications

- Network packet buffering
- Rate limiting systems
- Data stream processing
- Real-time analytics
- Moving averages in finance
- Monitoring CPU usage over time

Sliding window models real-time systems.

---

# 🧱 1️⃣4️⃣ Mental Model to Remember

Imagine a rubber band.

It stretches (expand).
It contracts (shrink).

But it always stays connected.

You never rebuild entire array.
You just adjust boundaries.

That is sliding window thinking.

---

# 📌 Final Understanding

Sliding window is:

- A dynamic boundary technique
- Built on two pointers
- Used for substring/subarray problems
- Reduces O(n²) to O(n)
- Requires maintaining window property
- Extremely common in interviews

If you master sliding window,
medium-level string problems become easy.

It is one of the most powerful patterns in DSA.

---

# 🔁 Navigation

Previous:  
[11_two_pointers/theory.md](/dsa-complete-mastery/11_two_pointers/theory.md)

Next:  
[12_sliding_window/interview.md](/dsa-complete-mastery/12_sliding_window/interview.md)  
[13_binary_search/theory.md](/dsa-complete-mastery/13_binary_search/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Two Pointers — Interview Q&A](../11_two_pointers/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
