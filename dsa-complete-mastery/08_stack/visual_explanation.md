# Stacks — Visual Explanation

---

## Chapter 1: The Stack of Plates

Walk into any buffet restaurant and look at the plate station. There is a spring-
loaded dispenser with a tall stack of plates. You always take the plate on TOP. When
the staff adds clean plates, they go on TOP. The plate that went in last comes out
first.

This is LIFO: **Last In, First Out.**

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

Simple. But the LIFO property is surprisingly powerful. Let's see why.

---

## Chapter 2: The Call Stack — Your Program's Stack of Plates

When you call a function, your computer creates a "stack frame" — a little box of
memory containing the function's local variables, its return address, and the return
value. This frame gets pushed onto the call stack.

When the function returns, the frame is popped off.

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

### What is a Stack Overflow?

Every computer has a maximum call stack size. If you write infinite recursion (or
very deep recursion), you keep pushing frames onto the stack until there is no room
left. The program crashes with "RecursionError: maximum recursion depth exceeded."

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

---

## Chapter 3: Balanced Brackets — The Stack as Memory

Given a string like `"({[]})"`, are the brackets balanced? This is a classic stack
problem. The insight: every time you see an opening bracket, push it. Every time you
see a closing bracket, check if the top of the stack is its matching opener.

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

**Now trace on `"({[})"` — a mismatch:**

```
Character: (    {    [    }    )

Step 1: '(' → push.  Stack: [ ( ]
Step 2: '{' → push.  Stack: [ (, { ]
Step 3: '[' → push.  Stack: [ (, {, [ ]
Step 4: '}' → pop top
  Popped: '[' — does NOT match '}' ✗
  STOP. Return "NOT BALANCED"
```

The stack remembers the order of opening brackets for you. LIFO ensures the most
recently opened bracket is checked first — exactly what you need for nesting.

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

---

## Chapter 4: Monotonic Stack — Looking for Someone Taller

You are standing in a crowd at a concert. You want to know: for each person, who is
the next person to their right that is taller than them?

Brute force: for each person, scan everyone to their right until you find someone
taller. O(n²).

The smart way: use a **monotonic stack**. Maintain a stack where elements are always
in decreasing order (tallest at the bottom, shortest at the top).

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

**The mental model:** imagine people walking in from the right. Each new person "resolves"
all shorter people ahead of them (they can see over them). Unresolved people stay in the
stack waiting for someone taller.

```
Array:  [2,  1,  4,  3,  7]
Result: [4,  4,  7,  7, -1]

     7      ←← tallest, resolves everyone remaining
   4   3    ←← 4 resolves 2 and 1; 7 later resolves 4 and 3
  2  1
```

```python
def next_greater_element(nums):
    n = len(nums)
    result = [-1] * n
    stack = []                   # stores indices
    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)
    return result
```

---

## Chapter 5: DFS With an Explicit Stack

Recursive DFS uses the call stack implicitly. You can always convert it to an
iterative version using your own explicit stack — and sometimes that is necessary
(deep trees hit Python's recursion limit).

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

The trick: push children in REVERSE order so the left child is processed first
(since the stack reverses the order again on pop).

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

**The key insight:** any recursive algorithm that does "work on the way down" (pre-order
style) can be converted to iterative with a stack. The stack is just making explicit what
recursion was doing implicitly all along.

---

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

---

*Next up: Queues — where everyone waits their turn (mostly).*
