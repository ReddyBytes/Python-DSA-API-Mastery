# 📘 Stack — Understanding It Through Real Life

> A stack is not an abstract computer concept.
> You already use it every day — without realizing it.

Stack follows one strict rule:

**Last In, First Out (LIFO)**

Whoever comes last must leave first.

Let’s understand this not through code,
but through life.

---

# 1️⃣ Plates in Your Kitchen

Imagine you wash 5 plates.

You stack them like this:

```
Top
  ↑
Plate 5
Plate 4
Plate 3
Plate 2
Plate 1
```

Now when you need a plate,
which one do you take?

The top one.

You cannot remove Plate 3 directly.
You must remove 5 and 4 first.

That restriction defines a stack.

Operations happening here:

- Put plate → Push
- Take plate → Pop
- See top plate → Peek

You just implemented a stack in your kitchen.

---

# 2️⃣ Books on a Study Table

You’re studying.

You place books one on top of another.

Later, you decide to remove one.
You remove the most recently placed book.

That’s LIFO.

Now imagine someone says:

“Take the 2nd book from bottom.”

You can't.
You must remove the top ones first.

That limitation is the identity of a stack.

---

# 3️⃣ Browser Back Button

You open:

1. Google
2. YouTube
3. LinkedIn

Your browsing history behaves like:

```
Top
LinkedIn
YouTube
Google
```

When you press back:

You go to YouTube.
Then Google.

The last visited page comes first when going back.

That is stack behavior.

---

# 4️⃣ Call Stack — Inside Your Computer

Now imagine function calls.

You call:

main()
   calls process()
       calls calculate()

In memory:

```
Top
calculate()
process()
main()
```

When calculate() finishes,
it returns first.

Then process() returns.
Then main() returns.

Exactly like plates.

That structure is called the **call stack**.

Every program you write uses stack internally.

---

# 5️⃣ Why Stack Is Powerful

Stacks control execution order.

Think about undo functionality in an editor.

You type:
- Word A
- Word B
- Word C

Undo removes C first.

Then B.
Then A.

Undo is LIFO.

Without stack,
undo feature would be complex.

---

# 6️⃣ What Makes Stack Special?

Stack has a restriction:

You can only interact with one end — the top.

That restriction makes reasoning easier.

If you allowed removal from anywhere,
it would become something else (like a list).

Stack’s limitation is its strength.

---

# 7️⃣ Stack Operations Explained with Daily Logic

## 🔹 Push

You place a new plate on top.

Time: O(1)

Why?
Because you don’t touch other plates.

---

## 🔹 Pop

You remove the top plate.

Time: O(1)

Again,
no shifting,
no searching.

---

## 🔹 Peek

You look at the top plate without removing it.

Time: O(1)

---

# 8️⃣ Implementing Stack in Python (Reality Check)

Python already gives stack-like behavior:

```python
stack = []
stack.append(10)  # push
stack.pop()       # pop
```

Why is this efficient?

Because operations happen at end of list.

No shifting required.

---

# 9️⃣ Parentheses Validation — Real Life Analogy

Imagine you are packing boxes.

You open a box:

```
(
```

You must close it properly:

```
)
```

If you open:

```
( {
```

You must close:

```
} )
```

The most recently opened must close first.

That is stack logic.

Validation process:

1. Push opening bracket.
2. On closing bracket:
   - Check top.
   - If matches → pop.
   - If not → invalid.

Stack ensures proper nesting.

---

# 🔟 Reversing Order — Why Stack Helps

Imagine you want to reverse a sentence:

“I love programming”

If you push each word into stack:

Push: I  
Push: love  
Push: programming  

Then pop:

programming  
love  
I  

Stack automatically reverses order.

This is why stack is used in reversing problems.

---

# 1️⃣1️⃣ Monotonic Stack — Daily Scenario

Imagine daily temperatures.

You want to know:
When will next hotter day come?

If today is 30°C,
and tomorrow is 28°C,
you wait.

But when a hotter day arrives,
you resolve previous waiting days.

Monotonic stack stores unresolved days.

Once hotter day comes,
you clear stack elements that are smaller.

Each day enters stack once,
leaves once.

Time:
O(n)

This pattern appears complex,
but it’s just structured waiting.

---

# 1️⃣2️⃣ Stack vs Queue in Daily Life

Stack:
Plates

Queue:
Line at a supermarket

In queue,
first person entering leaves first.

In stack,
last plate placed leaves first.

Confusing these leads to wrong algorithm choice.

---

# 1️⃣3️⃣ Where You Use Stack Without Knowing

- Undo/Redo
- Browser navigation
- Recursion
- Function calls
- Backtracking
- Expression parsing
- Depth-first search

Stack is everywhere in computing.

---

# 1️⃣4️⃣ When Stack Is Dangerous

If you keep pushing plates without removing,
stack grows tall.

In programming:

Too many recursive calls →
Stack overflow.

Memory is limited.

Stack must be managed carefully.

---

---

## The Monotonic Stack Pattern

A **monotonic stack** is a stack that maintains elements in either strictly increasing or strictly decreasing order. It's one of the most powerful patterns for "next greater/smaller element" problems.

**The core idea:**

Instead of comparing each element against all others (O(n²)), use a stack to efficiently find the next element that "breaks" the current order — O(n) total.

---

### Pattern 1: Next Greater Element

**Problem:** For each element in an array, find the next element to its right that is greater.

```
Input:  [2, 1, 5, 3, 6]
Output: [5, 5, 6, 6, -1]
         ↑  ↑  ↑  ↑   ↑
         2→5  1→5  5→6  3→6  6→none
```

**Stack state walkthrough:**

```
i=0: stack=[]      → push 2      → stack=[2]
i=1: stack=[2]     → 1<2, push   → stack=[2,1]
i=2: stack=[2,1]   → 5>1, pop 1  → answer[1]=5  → stack=[2]
                   → 5>2, pop 2  → answer[0]=5  → stack=[]
                   → push 5      → stack=[5]
i=3: stack=[5]     → 3<5, push   → stack=[5,3]
i=4: stack=[5,3]   → 6>3, pop 3  → answer[3]=6  → stack=[5]
                   → 6>5, pop 5  → answer[2]=6  → stack=[]
                   → push 6      → stack=[6]
end: stack=[6]     → 6 has no next greater → answer[4]=-1
```

```python
def next_greater(nums):
    n = len(nums)
    answer = [-1] * n
    stack = []                      # stores indices

    for i in range(n):
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            answer[idx] = nums[i]   # nums[i] is the next greater for idx
        stack.append(i)

    return answer
```

**Time:** O(n) — each element pushed and popped at most once.
**Space:** O(n) — stack.

---

### Pattern 2: Stock Span Problem

**Problem:** For each day's stock price, find how many consecutive days before it had a price ≤ today's price (including today itself).

```
Prices: [100, 80, 60, 70, 60, 75, 85]
Spans:  [  1,  1,  1,  2,  1,  4,  6]

Day 6: price=75 → look back: 60≤75, 70≤75, 60≤75, then 80>75 → span=4
```

```python
def stock_span(prices):
    stack = []   # stores (price, span)
    result = []

    for price in prices:
        span = 1
        while stack and stack[-1][0] <= price:
            span += stack.pop()[1]   # accumulate spans of popped elements
        stack.append((price, span))
        result.append(span)

    return result
```

---

### When to Use Monotonic Stack

```
Problem pattern                          → Use monotonic stack
─────────────────────────────────────────────────────────────
"Next greater/smaller element"           → decreasing/increasing stack
"Previous greater/smaller element"       → process left to right
"Largest rectangle in histogram"         → maintain increasing stack
"Trapping rain water"                    → maintain decreasing stack
"Daily temperatures"                     → next greater (decreasing)
```

**The recognition signal:** If the problem asks "for each element, find the nearest element
satisfying condition X in O(n)", monotonic stack is likely the answer.

---

# 📌 Final Understanding

Stack is:

- A strict behavioral structure
- Based on LIFO
- Simple in design
- Extremely powerful in control flow

It is not about storing data.
It is about controlling order.

If you understand stack deeply,
you understand recursion,
DFS,
expression evaluation,
and many advanced algorithms.

Next time you stack plates,
remember —
you are using a data structure.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Linked List — Interview Q&A](../07_linked_list/interview.md) &nbsp;|&nbsp; **Next:** [Visual Explanation →](./visual_explanation.md)

**Related Topics:** [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
