<a id="top"></a>
# 📘 08 – Stack in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is a Stack?](#1-what-is-a-stack)
  - [Plates in the Kitchen](#plates)
  - [Books on the Table](#books)
  - [Browser Back Button](#browser)
  - [Call Stack Inside Your Computer](#call-stack)
  - [Visual: LIFO Push/Pop](#visual-lifo)
  - [Visual: Call Stack and Stack Overflow](#visual-call-stack)
- [2. Why Stacks Are Powerful](#2-why-powerful)
- [3. Stack Operations and Implementation](#3-operations)
  - [Push, Pop, Peek](#push-pop-peek)
  - [Implementing in Python](#implementing)
- [4. Classic Stack Problems](#4-classic-problems)
  - [Parentheses Validation](#parentheses)
  - [Reversing Order](#reversing)
- [5. Monotonic Stack](#5-monotonic-stack)
  - [Visual: Next Greater Element](#visual-nge)
  - [Next Greater Element Pattern](#nge-pattern)
  - [Stock Span Problem](#stock-span)
  - [When to Use Monotonic Stack](#when-monotonic)
- [6. DFS With Explicit Stack](#6-dfs-stack)
  - [Visual: Mark-on-Push vs Mark-on-Pop](#visual-mark)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
LIFO principle · push/pop/peek · monotonic stack pattern

**Should Learn** — Important for real projects, comes up regularly:
next greater/smaller element · parentheses validation · stock span

**Good to Know** — Useful in specific situations, not always tested:
stack-based DFS · undo/redo pattern

**Reference** — Know it exists, look up syntax when needed:
expression evaluation · reverse Polish notation parsing

Zara works in a busy cafeteria. Every day she stacks clean plates, manages order tickets, and tracks which task to undo when something goes wrong. Without realizing it, she uses stacks constantly. A stack follows one strict rule: **Last In, First Out (LIFO)** — whoever comes last must leave first. Today Zara will discover that this simple rule powers everything from browser history to function calls to some of the trickiest interview problems.

<a id="1-what-is-a-stack"></a>
# 1. What Is a Stack?

Zara encounters stacks everywhere in her daily life — plates, books, browser tabs, even the way her computer runs programs. Every example follows the same LIFO rule.

<a id="plates"></a>
## Plates in the Kitchen

Zara washes 5 plates and stacks them:

```
Top →  [Plate 5]
       [Plate 4]
       [Plate 3]
       [Plate 2]
Bottom [Plate 1]
```

When she needs a plate, she takes from the top. She cannot reach Plate 1 without removing Plate 5 first. Last washed = first used. That is LIFO.

<a id="books"></a>
## Books on the Table

Zara studies after work. She stacks textbooks on her desk:

```
Top →  [Python DSA]
       [System Design]
       [SQL Mastery]
Bottom [Linux Guide]
```

She picks up the top book first. To reach the Linux Guide, she must remove everything above it. The most recently placed book is the first one she reads.

<a id="browser"></a>
## Browser Back Button

Zara browses the web: Home → Products → Item → Cart. Each page is pushed onto a stack. When she clicks Back, the most recent page is popped:

```
Push: Home → Products → Item → Cart

Stack:  [Cart]      ← current page
        [Item]
        [Products]
        [Home]

Click Back → pop Cart → now on Item
Click Back → pop Item → now on Products
```

The browser's back button is a stack.

<a id="call-stack"></a>
## Call Stack Inside Your Computer

When Python calls a function, it pushes a frame onto the call stack. When the function returns, the frame is popped. Recursion = pushing many frames before any pop.

```python
def a():
    b()

def b():
    c()

def c():
    print("hello")
```

<a id="visual-call-stack"></a>
## Visual: Call Stack and Stack Overflow

```
PHASE 1: Calls are pushed

  [c()]    ← top (most recent)
  [b()]
  [a()]
  [main]   ← bottom

PHASE 2: Returns are popped

  c() prints "hello", returns → popped
  b() returns → popped
  a() returns → popped
  main continues
```

**Stack Overflow** — what happens when the stack gets too deep:

```
def infinite():
    infinite()    # never stops → stack grows forever

[infinite()]
[infinite()]
[infinite()]
[infinite()]
... 1000 frames later ...
→ RecursionError: maximum recursion depth exceeded
```

Python's default recursion limit is ~1000 frames. Each frame consumes memory. An infinite recursion fills the stack until the system kills it.

<a id="visual-lifo"></a>
## Visual: LIFO Push/Pop in Action

```
PUSH operations (add to top):

push(10):  [10]
push(20):  [20]
           [10]
push(30):  [30]
           [20]
           [10]

POP operations (remove from top):

pop():     returns 30    stack: [20]
                                [10]
pop():     returns 20    stack: [10]
pop():     returns 10    stack: []  (empty)

LIFO: 30 was pushed last, popped first.
```

> [↑ Back to Top](#top)

<a id="2-why-powerful"></a>
# 2. Why Stacks Are Powerful

Zara realizes the stack is not just about plates — it is a pattern for controlling order. Any time you need to process the most recent item first, reverse a sequence, or match opening/closing pairs, a stack is the right tool.

Stacks shine when:
- **Order matters** — you must process the most recent item first
- **Nesting matters** — matching brackets, tags, parentheses
- **Undo/redo** — reverse the last action
- **Depth-first exploration** — explore one path completely before backtracking
- **Expression evaluation** — operator precedence

What makes a stack special: it restricts access to ONE end. You cannot reach the bottom without removing everything above it. This constraint is the source of its power — it enforces a strict processing order.

```
Stack vs unrestricted access:

Stack:     can only touch TOP → enforces LIFO order
Array:     can touch ANY index → no order enforcement
```

> [↑ Back to Top](#top)

<a id="3-operations"></a>
# 3. Stack Operations and Implementation

Zara learns the three fundamental moves she can make with her plate stack. Each one is O(1) — constant time, regardless of how tall the stack is.

<a id="push-pop-peek"></a>
## Push, Pop, Peek

| Operation | What it does | Time |
|---|---|---|
| `push(x)` | Add x to the top | O(1) |
| `pop()` | Remove and return the top | O(1) |
| `peek()` / `top()` | Look at the top without removing | O(1) |
| `is_empty()` | Check if stack is empty | O(1) |

**Common mistake — popping from an empty stack:** Always check `if stack:` before `stack.pop()`. Popping from an empty list raises `IndexError`.

<a id="implementing"></a>
## Implementing in Python

Python's `list` is a perfect stack — `append()` is push, `pop()` is pop. Both are O(1) amortized.

```python
stack = []

stack.append(10)    # push
stack.append(20)
stack.append(30)

top = stack[-1]     # peek → 30
val = stack.pop()   # pop → 30
print(stack)        # [10, 20]
```

Do NOT use `collections.deque` for a stack — it works but sends the wrong signal to readers. `list` is the idiomatic Python stack. Use `deque` for queues.

> [↑ Back to Top](#top)

<a id="4-classic-problems"></a>
# 4. Classic Stack Problems

Zara discovers that two of the most common interview problems are built entirely on the stack principle: matching pairs and reversing order.

<a id="parentheses"></a>
## Parentheses Validation

Zara checks if every opening bracket has a matching closer in the right order. She pushes openers onto the stack. When she sees a closer, she pops and checks if it matches.

```
Input: "({[]})"

Step 1: '(' → push       stack: ['(']
Step 2: '{' → push       stack: ['(', '{']
Step 3: '[' → push       stack: ['(', '{', '[']
Step 4: ']' → pop '[' ✓  stack: ['(', '{']
Step 5: '}' → pop '{' ✓  stack: ['(']
Step 6: ')' → pop '(' ✓  stack: []

Stack empty at end → VALID ✓
```

```
Input: "({[}])"

Step 1: '(' → push       stack: ['(']
Step 2: '{' → push       stack: ['(', '{']
Step 3: '[' → push       stack: ['(', '{', '[']
Step 4: '}' → pop '[' ✗  MISMATCH! '[' ≠ '}'

→ INVALID ✗
```

```python
def is_valid(s):
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}

    for ch in s:
        if ch in '({[':
            stack.append(ch)
        elif ch in ')}]':
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()

    return len(stack) == 0
```

**Common mistake — forgetting to check stack is empty at end:** `"((("` has no mismatches during traversal, but 3 unmatched openers remain. Always verify `len(stack) == 0` after the loop.

<a id="reversing"></a>
## Reversing Order

Zara needs to reverse a sequence. She pushes everything onto the stack, then pops — items come out in reverse order.

```
Input:  [1, 2, 3, 4, 5]

Push all:  stack = [1, 2, 3, 4, 5]  (5 on top)

Pop all:   5, 4, 3, 2, 1

Output: [5, 4, 3, 2, 1]
```

This is why stacks naturally reverse things — LIFO inverts the input order.

> [↑ Back to Top](#top)

<a id="5-monotonic-stack"></a>
# 5. Monotonic Stack

Zara stands in a crowd at a concert. She looks to her right — who is the next person taller than her? That is the **Next Greater Element** problem, and the monotonic stack solves it in O(n).

A **monotonic stack** maintains elements in sorted order (either increasing or decreasing). When a new element violates the monotone property, it pops elements — and whatever triggers the pop BECOMES the answer for the popped element.

<a id="visual-nge"></a>
## Visual: Next Greater Element — Crowd Analogy

Zara is in a line of people with different heights. Each person looks to their right for the first person taller than them.

```
Heights: [2, 1, 4, 3, 5]

Person 2 looks right → sees 1 (shorter), then 4 (TALLER!) → answer is 4
Person 1 looks right → sees 4 (TALLER!) → answer is 4
Person 4 looks right → sees 3 (shorter), then 5 (TALLER!) → answer is 5
Person 3 looks right → sees 5 (TALLER!) → answer is 5
Person 5 looks right → nobody taller → answer is -1

Result: [4, 4, 5, 5, -1]
```

The brute force is O(n²) — for each person, scan right. The monotonic stack does it in O(n).

```
Stack trace (decreasing stack — stores indices):

i=0, val=2: stack empty, push 0         stack: [0]
i=1, val=1: 1 < 2, push 1              stack: [0, 1]
i=2, val=4: 4 > 1, pop 1 → ans[1]=4
             4 > 2, pop 0 → ans[0]=4
             push 2                     stack: [2]
i=3, val=3: 3 < 4, push 3              stack: [2, 3]
i=4, val=5: 5 > 3, pop 3 → ans[3]=5
             5 > 4, pop 2 → ans[2]=5
             push 4                     stack: [4]

Remaining in stack: [4] → ans[4]=-1

Result: [4, 4, 5, 5, -1]  ✓
```

<a id="nge-pattern"></a>
## Next Greater Element Pattern

```python
def next_greater_element(arr):
    n = len(arr)
    result = [-1] * n
    stack = []  # stores indices

    for i in range(n):
        while stack and arr[i] > arr[stack[-1]]:
            idx = stack.pop()
            result[idx] = arr[i]
        stack.append(i)

    return result
```

Time: O(n) — each element is pushed and popped at most once.

<a id="stock-span"></a>
## Stock Span Problem

For each day, find how many consecutive previous days had a price less than or equal to today's price. Same monotonic stack idea — maintain a decreasing stack of prices.

```python
def stock_span(prices):
    n = len(prices)
    spans = [0] * n
    stack = []  # stores indices

    for i in range(n):
        while stack and prices[i] >= prices[stack[-1]]:
            stack.pop()
        spans[i] = i + 1 if not stack else i - stack[-1]
        stack.append(i)

    return spans
```

<a id="when-monotonic"></a>
## When to Use Monotonic Stack

| Problem type | Stack type | Pop condition |
|---|---|---|
| Next Greater Element | Decreasing | Current > top |
| Next Smaller Element | Increasing | Current < top |
| Previous Greater | Decreasing | Current >= top |
| Stock Span | Decreasing | Current >= top |

Rule: whatever triggers the pop BECOMES the answer for the popped element.

> [↑ Back to Top](#top)

<a id="6-dfs-stack"></a>
# 6. DFS With Explicit Stack

Zara learns that recursion uses the call stack implicitly. For iterative DFS, she builds her own stack explicitly — same logic, but she controls the memory.

```python
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        print(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                stack.append(neighbor)
```

<a id="visual-mark"></a>
## Visual: Mark-on-Push vs Mark-on-Pop

Two strategies for tracking visited nodes. Mark-on-push avoids duplicate pushes. Mark-on-pop is simpler but may push duplicates.

```
Mark-on-Push:
  Push A (mark A immediately)            stack: [A]
  Pop A → push B, C (mark B, C on push) stack: [B, C]
  Pop C → push D (mark D on push)       stack: [B, D]
  Pop D → no unvisited neighbours        stack: [B]
  Pop B → D already visited              stack: []

Mark-on-Pop:
  Push A                                  stack: [A]
  Pop A (mark A) → push B, C             stack: [B, C]
  Pop C (mark C) → push D                stack: [B, D]
  Pop D (mark D) → no unvisited          stack: [B]
  Pop B (mark B) → D already visited     stack: []
```

Mark-on-push is more efficient — prevents duplicate entries on the stack.

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

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

Monotonic stack rules:
  Next Greater: maintain decreasing stack
  Next Smaller: maintain increasing stack
  Pop when current element violates the monotone property
  Whatever triggers the pop BECOMES the answer for the popped element
```

| Concept | Key Takeaway |
|---------|-------------|
| LIFO | Last in, first out — enforces strict processing order |
| Operations | push/pop/peek all O(1) |
| Brackets | Push openers, pop and match on closers |
| Monotonic stack | O(n) solution for next greater/smaller element |
| DFS | Explicit stack replaces recursion's implicit call stack |
| Call stack | Function calls = push, returns = pop |

**Stack vs Queue:**
- Stack: LIFO — plates, undo, DFS, recursion
- Queue: FIFO — waiting line, BFS, task scheduling

**Where you use stacks without knowing:** browser back button, Ctrl+Z undo, compiler expression parsing, call stack in every program, XML/HTML tag matching.

**When stacks are dangerous:** infinite recursion → stack overflow. Always ensure base case exists. Python limit ~1000 frames.

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [07_linked_list → theory.md](../07_linked_list/theory.md) |
| ➡ Next Module | [09_queue → theory.md](../09_queue/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[07 Linked List →](../07_linked_list/theory.md) · [09 Queue →](../09_queue/theory.md) · [04 Recursion →](../04_recursion/theory.md) · [18 Graphs →](../18_graphs/theory.md)

**Jump to specific topics in other files:**
- Recursion and call stack → [04_recursion § The Call Stack](../04_recursion/theory.md#3-the-call-stack)
- DFS in graphs → [18_graphs § theory.md](../18_graphs/theory.md)
- Queue (FIFO counterpart) → [09_queue § theory.md](../09_queue/theory.md)
- Monotonic stack in sliding window → [12_sliding_window § theory.md](../12_sliding_window/theory.md)

> [↑ Back to Top](#top)
