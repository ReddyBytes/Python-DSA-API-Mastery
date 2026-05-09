<a id="top"></a>
# Stack — Understanding It Through Real Life

> A stack is not an abstract computer concept.
> You already use it every day — without realizing it.

Stack follows one strict rule:

**Last In, First Out (LIFO)**

Whoever comes last must leave first.

Let's understand this not through code,
but through life.

## 📖 Table of Contents

1. [Plates in Your Kitchen](#1-plates-in-your-kitchen)
2. [Books on a Study Table](#2-books-on-a-study-table)
3. [Browser Back Button](#3-browser-back-button)
4. [Call Stack — Inside Your Computer](#4-call-stack-inside-your-computer)
5. [Why Stack Is Powerful](#5-why-stack-is-powerful)
6. [What Makes Stack Special?](#6-what-makes-stack-special)
7. [Stack Operations Explained with Daily Logic](#7-stack-operations-explained-with-daily-logic)
8. [Implementing Stack in Python (Reality Check)](#8-implementing-stack-in-python-reality-check)
9. [Parentheses Validation — Real Life Analogy](#9-parentheses-validation-real-life-analogy)
10. [Reversing Order — Why Stack Helps](#10-reversing-order-why-stack-helps)
11. [Monotonic Stack — Daily Scenario](#11-monotonic-stack-daily-scenario)
12. [Stack vs Queue in Daily Life](#12-stack-vs-queue-in-daily-life)
13. [Where You Use Stack Without Knowing](#13-where-you-use-stack-without-knowing)
14. [When Stack Is Dangerous](#14-when-stack-is-dangerous)
15. [The Monotonic Stack Pattern (Deep Dive)](#15-the-monotonic-stack-pattern-deep-dive)
16. [DFS With an Explicit Stack](#16-dfs-with-an-explicit-stack)
17. [Final Understanding](#17-final-understanding)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
LIFO principle · push/pop/peek · monotonic stack pattern

**Should Learn** — Important for real projects, comes up regularly:
next greater/smaller element · parentheses validation · stock span

**Good to Know** — Useful in specific situations, not always tested:
stack-based DFS · undo/redo pattern

**Reference** — Know it exists, look up syntax when needed:
expression evaluation · reverse Polish notation parsing

<a id="1-plates-in-your-kitchen"></a>
# 1. Plates in Your Kitchen

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

## Visual: LIFO Push/Pop in Action

Walk into any buffet restaurant and look at the plate station. There is a spring-loaded dispenser with a tall stack of plates. You always take the plate on TOP. When the staff adds clean plates, they go on TOP. The plate that went in last comes out first.

```
push(A)    push(B)    push(C)    pop()     pop()
  [C]                                      [A]
  [B]        [B]        [C]
  [A]        [A]        [B]       [B]      ← only
             ↑          [A]       [A]         this
           grows                           remains
           upward
```

The only operations you get:
- **push(x)**: add to the top
- **pop()**: remove from the top
- **peek()**: look at the top without removing
- **is_empty()**: is there anything here?

```python
stack = []
stack.append(1)   # push
stack.append(2)   # push
stack.append(3)   # push
stack.pop()       # returns 3 — top comes off first
stack.pop()       # returns 2
```

**Common mistake — pop(0) instead of pop():** Using `stack.pop(0)` removes the first element (FIFO/queue order) and costs O(n) per call because all remaining elements must shift left. Always use `stack.pop()` for LIFO; if you need FIFO, use `collections.deque` with `popleft()`.

> [↑ Back to Top](#top)

<a id="2-books-on-a-study-table"></a>
# 2. Books on a Study Table

You're studying.

You place books one on top of another.

Later, you decide to remove one.
You remove the most recently placed book.

That's LIFO.

Now imagine someone says:

"Take the 2nd book from bottom."

You can't.
You must remove the top ones first.

That limitation is the identity of a stack.

> [↑ Back to Top](#top)

<a id="3-browser-back-button"></a>
# 3. Browser Back Button

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

> [↑ Back to Top](#top)

<a id="4-call-stack-inside-your-computer"></a>
# 4. Call Stack — Inside Your Computer

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

## Visual: Call Stack Frame-by-Frame

When you call a function, your computer creates a "stack frame" — a little box of memory containing the function's local variables, its return address, and the return value. This frame gets pushed onto the call stack. When the function returns, the frame is popped off.

Let's trace `factorial(4)`:

```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
```

**Building up (pushing frames):**

```
Call factorial(4):
┌──────────────────┐
│ factorial(4)     │  ← current frame
│ n = 4            │
│ waiting for f(3) │
└──────────────────┘

Call factorial(3):
┌──────────────────┐
│ factorial(3)     │  ← current frame
│ n = 3            │
│ waiting for f(2) │
├──────────────────┤
│ factorial(4)     │
│ n = 4            │
│ waiting for f(3) │
└──────────────────┘

Call factorial(2):
┌──────────────────┐
│ factorial(2)     │
│ n = 2            │
│ waiting for f(1) │
├──────────────────┤
│ factorial(3)     │
├──────────────────┤
│ factorial(4)     │
└──────────────────┘

Call factorial(1):
┌──────────────────┐
│ factorial(1)     │
│ n = 1            │
│ waiting for f(0) │
├──────────────────┤
│ factorial(2)     │
├──────────────────┤
│ factorial(3)     │
├──────────────────┤
│ factorial(4)     │
└──────────────────┘

Call factorial(0):
┌──────────────────┐
│ factorial(0)     │  ← base case! returns 1
│ n = 0            │
├──────────────────┤
│ factorial(1)     │
├──────────────────┤
│ ...              │
└──────────────────┘
```

**Unwinding (popping frames):**

```
factorial(0) returns 1 → popped
┌──────────────────┐
│ factorial(1)     │  ← now n * 1 = 1 * 1 = 1, returns 1
└──────────────────┘

factorial(1) returns 1 → popped
┌──────────────────┐
│ factorial(2)     │  ← now n * 1 = 2 * 1 = 2, returns 2
└──────────────────┘

factorial(2) returns 2 → popped
┌──────────────────┐
│ factorial(3)     │  ← now 3 * 2 = 6, returns 6
└──────────────────┘

factorial(3) returns 6 → popped
┌──────────────────┐
│ factorial(4)     │  ← now 4 * 6 = 24, returns 24
└──────────────────┘

factorial(4) returns 24. Done.
```

## Visual: Stack Overflow

Every computer has a maximum call stack size. If you write infinite recursion (or very deep recursion), you keep pushing frames onto the stack until there is no room left. The program crashes with "RecursionError: maximum recursion depth exceeded."

```
┌──────────────────┐
│ factorial(999)   │
├──────────────────┤
│ factorial(998)   │
├──────────────────┤
│ ...              │  ← stack keeps growing
├──────────────────┤
│ factorial(1)     │
├──────────────────┤  ← LIMIT REACHED
│ CRASH!           │  ← "RecursionError"
└──────────────────┘
```

> 📝 **Practice:** [Q18 · recursion-call-stack](./practice.md#q18----trace-the-recursion-call-stack-for-factorial4) · [Q24 · fix-stack-overflow](./practice.md#q24----diagnose-and-fix-a-stack-overflow)

> [↑ Back to Top](#top)

<a id="5-why-stack-is-powerful"></a>
# 5. Why Stack Is Powerful

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

> 📝 **Practice:** [Q15 · undo-redo](./practice.md#q15----undoredo-with-a-command-stack) · [Q14 · browser-history](./practice.md#q14----browser-history-with-backforward)

> [↑ Back to Top](#top)

<a id="6-what-makes-stack-special"></a>
# 6. What Makes Stack Special?

Stack has a restriction:

You can only interact with one end — the top.

That restriction makes reasoning easier.

If you allowed removal from anywhere,
it would become something else (like a list).

Stack's limitation is its strength.

> [↑ Back to Top](#top)

<a id="7-stack-operations-explained-with-daily-logic"></a>
# 7. Stack Operations Explained with Daily Logic

## 🔹 Push

You place a new plate on top.

Time: O(1)

Why?
Because you don't touch other plates.

## 🔹 Pop

You remove the top plate.

Time: O(1)

Again,
no shifting,
no searching.

**Common mistake — popping without checking empty:** Calling `.pop()` on an empty list raises `IndexError`. Always guard with `if stack:` before popping. For peek, use `stack[-1] if stack else None` rather than calling `.pop()` and pushing back.

## 🔹 Peek

You look at the top plate without removing it.

Time: O(1)

> 📝 **Practice:** [Q2 · push-pop-peek](./practice.md#q2----implement-push--pop--peek-with-a-python-list) · [Q3 · deque-stack](./practice.md#q3----implement-a-stack-using-collectionsdeque) · [Q4 · safe-peek](./practice.md#q4----safe-peek----handle-empty-stack)

> [↑ Back to Top](#top)

<a id="8-implementing-stack-in-python-reality-check"></a>
# 8. Implementing Stack in Python (Reality Check)

Python already gives stack-like behavior:

```python
stack = []
stack.append(10)  # push
stack.pop()       # pop
```

Why is this efficient?

Because operations happen at end of list.

No shifting required.

> 📝 **Practice:** [Q1 · lifo-demo](./practice.md#q1----what-comes-out-first-from-a-stack) · [Q5 · reverse-with-stack](./practice.md#q5----reverse-a-list-using-a-stack) · [Q8 · stack-vs-queue](./practice.md#q8----stack-vs-queue-spot-the-difference)

> [↑ Back to Top](#top)

<a id="9-parentheses-validation-real-life-analogy"></a>
# 9. Parentheses Validation — Real Life Analogy

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

## Visual: Bracket Matching Step-by-Step

The stack remembers the order of opening brackets for you. LIFO ensures the most recently opened bracket is checked first — exactly what you need for nesting.

**Trace on `"({[]})"`:**

```
Character: (    {    [    ]    }    )
           ↓    ↓    ↓    ↓    ↓    ↓

Step 1: '(' is opening → push
  Stack: [ ( ]

Step 2: '{' is opening → push
  Stack: [ (, { ]

Step 3: '[' is opening → push
  Stack: [ (, {, [ ]

Step 4: ']' is closing → pop top, check match
  Popped: '[' — matches ']' ✓
  Stack: [ (, { ]

Step 5: '}' is closing → pop top, check match
  Popped: '{' — matches '}' ✓
  Stack: [ ( ]

Step 6: ')' is closing → pop top, check match
  Popped: '(' — matches ')' ✓
  Stack: [ ]   (empty)

Stack is empty at the end → BALANCED ✓
```

**Trace on `"({[})"` — a mismatch:**

```
Character: (    {    [    }    )

Step 1: '(' → push.  Stack: [ ( ]
Step 2: '{' → push.  Stack: [ (, { ]
Step 3: '[' → push.  Stack: [ (, {, [ ]
Step 4: '}' → pop top
  Popped: '[' — does NOT match '}' ✗
  STOP. Return "NOT BALANCED"
```

```python
def is_balanced(s):
    stack = []
    match = {')': '(', '}': '{', ']': '['}
    for ch in s:
        if ch in '({[':
            stack.append(ch)
        elif ch in ')}]':
            if not stack or stack[-1] != match[ch]:
                return False
            stack.pop()
    return len(stack) == 0
```

**Common mistake — returning True without checking empty stack:** After processing all characters, the stack may still contain unmatched opening brackets. `return True` at the end means `"((("` passes validation. Always use `return len(stack) == 0` so unmatched openers are caught.

> 📝 **Practice:** [Q32 · valid-parentheses](../dsa_practice_questions_100.md#q32--logical--valid-parentheses)

> [↑ Back to Top](#top)

<a id="10-reversing-order-why-stack-helps"></a>
# 10. Reversing Order — Why Stack Helps

Imagine you want to reverse a sentence:

"I love programming"

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

> [↑ Back to Top](#top)

<a id="11-monotonic-stack-daily-scenario"></a>
# 11. Monotonic Stack — Daily Scenario

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
but it's just structured waiting.

> 📝 **Practice:** [Q12 · daily-temperatures](./practice.md#q12----daily-temperatures) · [Q13 · next-greater-element](./practice.md#q13----next-greater-element) · [Q20 · stock-span](./practice.md#q20----stock-span-problem) · [Q33 · monotonic-stack](../dsa_practice_questions_100.md#q33--thinking--monotonic-stack)

> [↑ Back to Top](#top)

<a id="12-stack-vs-queue-in-daily-life"></a>
# 12. Stack vs Queue in Daily Life

Stack:
Plates

Queue:
Line at a supermarket

In queue,
first person entering leaves first.

In stack,
last plate placed leaves first.

Confusing these leads to wrong algorithm choice.

> 📝 **Practice:** [Q8 · stack-vs-queue](./practice.md#q8----stack-vs-queue-spot-the-difference) · [Q82 · stack-vs-queue](../dsa_practice_questions_100.md#q82--interview--stack-vs-queue)

> [↑ Back to Top](#top)

<a id="13-where-you-use-stack-without-knowing"></a>
# 13. Where You Use Stack Without Knowing

- Undo/Redo
- Browser navigation
- Recursion
- Function calls
- Backtracking
- Expression parsing
- Depth-first search

Stack is everywhere in computing.

> 📝 **Practice:** [Q9 · balanced-parens](./practice.md#q9----balanced-parentheses-single-type) · [Q10 · balanced-brackets](./practice.md#q10----balanced-brackets-multi-type-) · [Q16 · rpn](./practice.md#q16----evaluate-reverse-polish-notation-rpn) · [Q17 · simplify-path](./practice.md#q17----simplify-file-path-ab-c) · [Q31 · stack-lifo-uses](../dsa_practice_questions_100.md#q31--normal--stack-lifo-uses)

> [↑ Back to Top](#top)

<a id="14-when-stack-is-dangerous"></a>
# 14. When Stack Is Dangerous

If you keep pushing plates without removing,
stack grows tall.

In programming:

Too many recursive calls →
Stack overflow.

Memory is limited.

Stack must be managed carefully.

> [↑ Back to Top](#top)

<a id="15-the-monotonic-stack-pattern-deep-dive"></a>
# 15. The Monotonic Stack Pattern (Deep Dive)

A **monotonic stack** is a stack that maintains elements in either strictly increasing or strictly decreasing order. It's one of the most powerful patterns for "next greater/smaller element" problems.

**The core idea:**

Instead of comparing each element against all others (O(n²)), use a stack to efficiently find the next element that "breaks" the current order — O(n) total.

## Visual: Next Greater Element — Crowd Analogy

You are standing in a crowd at a concert. You want to know: for each person, who is the next person to their right that is taller than them?

Brute force: for each person, scan everyone to their right until you find someone taller. O(n²).

The smart way: use a monotonic stack. Maintain a stack where elements are always in decreasing order (tallest at the bottom, shortest at the top).

**Problem:** Find the "Next Greater Element" for each position in `[2, 1, 4, 3, 7]`.

Expected output: `[4, 4, 7, 7, -1]` (-1 means no one taller to the right)

```
We iterate left to right. Stack holds indices of elements we haven't found
a "next greater" for yet.

Process index 0, val=2:
  Stack is empty. Push index 0.
  Stack: [0]  (values: [2])

Process index 1, val=1:
  Stack top = index 0, val=2. Is 1 > 2? No.
  Push index 1.
  Stack: [0, 1]  (values: [2, 1])

Process index 2, val=4:
  Stack top = index 1, val=1. Is 4 > 1? YES!
    result[1] = 4. Pop index 1.
  Stack top = index 0, val=2. Is 4 > 2? YES!
    result[0] = 4. Pop index 0.
  Stack is empty. Push index 2.
  Stack: [2]  (values: [4])

Process index 3, val=3:
  Stack top = index 2, val=4. Is 3 > 4? No.
  Push index 3.
  Stack: [2, 3]  (values: [4, 3])

Process index 4, val=7:
  Stack top = index 3, val=3. Is 7 > 3? YES!
    result[3] = 7. Pop index 3.
  Stack top = index 2, val=4. Is 7 > 4? YES!
    result[2] = 7. Pop index 2.
  Stack is empty. Push index 4.
  Stack: [4]  (values: [7])

End of array. Remaining in stack: [index 4]
  result[4] = -1 (nothing to the right)

Final result: [4, 4, 7, 7, -1]
```

**Why is this O(n)?** Each element is pushed once and popped once. Total work: 2n = O(n).

**The mental model:** imagine people walking in from the right. Each new person "resolves" all shorter people ahead of them (they can see over them). Unresolved people stay in the stack waiting for someone taller.

```
Array:  [2,  1,  4,  3,  7]
Result: [4,  4,  7,  7, -1]

     7      ←← tallest, resolves everyone remaining
   4   3    ←← 4 resolves 2 and 1; 7 later resolves 4 and 3
  2  1
```

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

**Common mistake — ignoring leftover stack after loop:** In circular variants (next greater in a circular array), doing only one pass means wrap-around elements are never resolved. The fix is two passes: `for i in range(2 * n)` with `idx = i % n`, pushing only during the first pass (`if i < n`).

> 📝 **Practice:** [Q69 · monotonic-stack-nge](../dsa_practice_questions_100.md#q69--logical--monotonic-stack-nge)

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

**The recognition signal:** If the problem asks "for each element, find the nearest element satisfying condition X in O(n)", monotonic stack is likely the answer.

> 📝 **Practice:** [Q21 · histogram](./practice.md#q21----largest-rectangle-in-histogram) · [Q22 · circular-nge](./practice.md#q22----next-greater-element-ii-circular-array) · [Q23 · rain-water](./practice.md#q23----trapping-rain-water) · [Q69 · monotonic-stack-nge](../dsa_practice_questions_100.md#q69--logical--monotonic-stack-nge)

> [↑ Back to Top](#top)

<a id="16-dfs-with-an-explicit-stack"></a>
# 16. DFS With an Explicit Stack

Recursive DFS uses the call stack implicitly. You can always convert it to an iterative version using your own explicit stack — and sometimes that is necessary (deep trees hit Python's recursion limit).

**Tree:**

```
        A
       / \
      B   C
     / \
    D   E
```

**Recursive DFS (implicit stack):**

```
visit(A)
  visit(B)
    visit(D) ← leaf, return
    visit(E) ← leaf, return
  visit(C) ← leaf, return

Output: A, B, D, E, C
```

**Iterative DFS (explicit stack):**

```
Start: stack = [A]

Step 1: pop A → visit A
  push A's children: C first, then B (so B is on top — processed first)
  stack = [C, B]
  visited: A

Step 2: pop B → visit B
  push B's children: E first, then D
  stack = [C, E, D]
  visited: A, B

Step 3: pop D → visit D (leaf, no children)
  stack = [C, E]
  visited: A, B, D

Step 4: pop E → visit E (leaf, no children)
  stack = [C]
  visited: A, B, D, E

Step 5: pop C → visit C (leaf, no children)
  stack = []
  visited: A, B, D, E, C

Done. Same order as recursive!
```

The trick: push children in REVERSE order so the left child is processed first (since the stack reverses the order again on pop).

```python
def dfs_iterative(root):
    if not root:
        return
    stack = [root]
    while stack:
        node = stack.pop()
        print(node.val)
        # push right first so left is processed first
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
```

**The key insight:** any recursive algorithm that does "work on the way down" (pre-order style) can be converted to iterative with a stack. The stack is just making explicit what recursion was doing implicitly all along.

**Common mistake — marking visited on pop instead of push:** When doing iterative DFS on a graph, if you mark a node visited only when you pop it, the same node can be pushed multiple times by different neighbours before it is ever popped. Mark nodes visited immediately when pushing, not when popping, to prevent redundant work and cycles.

## Visual: Mark-on-Push vs Mark-on-Pop

```
Graph: A -> B -> D
            C -> D

WRONG (mark on pop):
  Stack: [A]
  Pop A, mark A → push B, push C       stack: [B, C]
  Pop C, mark C → push D               stack: [B, D]
  Pop D, mark D                         stack: [B]
  Pop B, mark B → push D  ← D pushed again! stack: [D]
  Pop D, already visited → skip

CORRECT (mark on push):
  Stack: [A], visited: {A}
  Pop A → push B (mark B), push C (mark C)   stack: [B, C]
  Pop C → D not visited, push D (mark D)      stack: [B, D]
  Pop D → no unvisited neighbours             stack: [B]
  Pop B → D already visited, skip             stack: []
  Done. D was pushed exactly once.
```

> [↑ Back to Top](#top)

<a id="17-final-understanding"></a>
# 17. Final Understanding

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

## Quick Reference

```
Stack: LIFO (Last In, First Out)
Operations: push O(1), pop O(1), peek O(1)

+-------------------------------+----------------------------------+
| Pattern                       | Key Idea                         |
+-------------------------------+----------------------------------+
| Balanced brackets             | Push openers, match closers      |
| Next greater element          | Monotonic decreasing stack       |
| Previous smaller element      | Monotonic increasing stack       |
| DFS iterative                 | Explicit stack replaces call     |
|                               | stack                            |
| Evaluate expression           | Operand stack + operator stack   |
+-------------------------------+----------------------------------+

Call stack:
  Each function call = push a frame
  Each function return = pop a frame
  Stack overflow = too many frames (infinite recursion)

Monotonic stack rules:
  Next Greater: maintain decreasing stack
  Next Smaller: maintain increasing stack
  Pop when current element violates the monotone property
  Whatever triggers the pop BECOMES the answer for the popped element
```

> [↑ Back to Top](#top)

**[🏠 Back to README](../README.md)**

**Prev:** [← Linked List — Interview Q&A](../07_linked_list/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheetsheet.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
