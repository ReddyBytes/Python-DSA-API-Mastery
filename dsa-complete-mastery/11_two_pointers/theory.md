# 📘 Two Pointers — Thinking With Two Moving Hands

> 📝 **Practice:** [Q4 · two-pointer-opposite-ends](../dsa_practice_questions_100.md#q4--code--two-pointer-opposite-ends) · [Q92 · predict-two-pointer-trace](../dsa_practice_questions_100.md#q92--logical--predict-two-pointer-trace)

> Two pointers is not a data structure.
> It is a technique.
>
> It transforms brute-force O(n²) solutions
> into efficient O(n) or O(n log n).

Two pointers is about controlled movement.

Instead of scanning everything repeatedly,
you move intelligently.

> 📝 **Practice:** [Q21 · two-pointer-fast-slow](../dsa_practice_questions_100.md#q21--code--two-pointer-fast-slow)

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
opposite-direction pointers · same-direction pointers · two sum sorted

**Should Learn** — Important for real projects, comes up regularly:
when to use two pointers vs hashmap · removing duplicates · palindrome check

**Good to Know** — Useful in specific situations, not always tested:
container with most water · partition pattern

**Reference** — Know it exists, look up syntax when needed:
two pointers on different arrays · three-pointer variants

---

# 1️⃣ Real-Life Analogy — Finding a Book Between Two People

Imagine two people standing at opposite ends of a long shelf.

One starts from left.
One starts from right.

They move toward each other,
checking books until they meet.

Instead of one person checking entire shelf,
two people divide work efficiently.

That is two pointers.

---

# 2️⃣ The Core Idea

Instead of using nested loops:

```
for i in range(n):
    for j in range(n):
```

We use:

```
left = 0
right = n - 1
```

And move them based on condition.

Two pointers reduces redundant work.

---

# 3️⃣ When Two Pointers Is Applicable

Look for:

- Sorted arrays
- Pairs or triplets
- Subarray problems
- Reversing problems
- Partitioning problems
- Removing duplicates
- Palindrome checking

If you see “pair”, “sum”, “opposite ends”,
consider two pointers.

---

# 4️⃣ Two Main Types of Two Pointer Techniques

---

## 🔹 Opposite Direction

One pointer at start,
one at end.

Move inward.

Used in:

- Two Sum (sorted)
- Palindrome
- Container with most water

---

## 🔹 Same Direction

Both pointers move forward.

Used in:

- Removing duplicates
- Partitioning
- Slow-fast pointer problems
- Sliding window foundation

---

# 5️⃣ Example — Two Sum in Sorted Array

Given sorted array:

```
[1, 2, 4, 6, 10]
```

Target = 8

Initialize:

left = 0 (1)
right = 4 (10)

Check:
1 + 10 = 11 → too big → move right left

Now:
1 + 6 = 7 → too small → move left right

Now:
2 + 6 = 8 → found

Time:
O(n)

Instead of O(n²).

> 📝 **Practice:** [Q22 · two-pointer-3sum](../dsa_practice_questions_100.md#q22--code--two-pointer-3sum)

---

# 6️⃣ Why It Works

Because array is sorted.

If sum too large:
Moving right pointer left reduces sum.

If sum too small:
Moving left pointer right increases sum.

Sorted order enables directional movement.

---

# 7️⃣ Removing Duplicates from Sorted Array

Given:

```
[1, 1, 2, 2, 3]
```

Use:

- slow pointer
- fast pointer

Fast scans.
Slow updates unique elements.

Result:
[1, 2, 3]

Time:
O(n)
Space:
O(1)

Efficient in-place solution.

---

# 8️⃣ Palindrome Checking

Given string:

```
"racecar"
```

left = 0
right = len(s) - 1

Compare s[left] and s[right].

If equal → move inward.

If mismatch → not palindrome.

Time:
O(n)

This is classic opposite-direction two pointers.

---

# 9️⃣ Container With Most Water

Given heights array.

Use two pointers at ends.

Area determined by:

min(height[left], height[right]) × width

Move pointer pointing to smaller height.

Why?

Because area limited by smaller height.

Moving taller one won’t increase area.

This is logic-based movement.

---

# 🔟 Partitioning Problems

Example:
Move all zeros to end.

Use:

- slow pointer for placement
- fast pointer for scanning

When non-zero found:
Swap with slow pointer.

Time:
O(n)

Two pointers helps rearrange in-place.

> 📝 **Practice:** [Q23 · two-pointer-partition](../dsa_practice_questions_100.md#q23--thinking--two-pointer-partition)

---

# 1️⃣1️⃣ Two Pointers vs Hashing

Two pointers requires sorted data.

Hashing works on unsorted data.

Example:

Two Sum:

Sorted:
Use two pointers → O(n)

Unsorted:
Use hashmap → O(n)

Choose technique based on input condition.

---

# 1️⃣2️⃣ Two Pointers in Linked List

Fast and slow pointer pattern:

- Detect cycle
- Find middle
- Remove nth node

Two pointers applies beyond arrays.

---

# 1️⃣3️⃣ Common Mistakes

- Moving wrong pointer
- Infinite loops
- Forgetting sorted requirement
- Not handling duplicates properly
- Incorrect boundary conditions

Two pointer logic must be precise.

---

# 1️⃣4️⃣ Performance Advantage

Without two pointers:
O(n²)

With two pointers:
O(n)

Massive improvement for large inputs.

Example:
n = 10⁵

O(n²) → impossible
O(n) → feasible

Two pointers is optimization mindset.

---

# 📌 Final Understanding

Two pointers is:

- A movement strategy
- A pattern recognition skill
- Based on direction control
- Often requires sorted data
- Reduces nested loops

It prepares you for:

- Sliding window
- Greedy problems
- Binary search variations
- Advanced optimization patterns

Two pointers is where problem-solving becomes elegant.

---

# 🔁 Navigation

Previous:  
[10_hashing/theory.md](/dsa-complete-mastery/10_hashing/theory.md)

Next:  
[11_two_pointers/interview.md](/dsa-complete-mastery/11_two_pointers/interview.md)  
[12_sliding_window/theory.md](/dsa-complete-mastery/12_sliding_window/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Hashing — Interview Q&A](../10_hashing/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
