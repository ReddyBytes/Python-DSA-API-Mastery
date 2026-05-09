# Stack — Practice Questions

> 25 questions covering every major stack concept and pattern.
> Work through Basic first — they build the vocabulary for Intermediate and Advanced.

---

## Quick Index

| # | Topic | Level |
|---|-------|-------|
| [Q1](#q1) | LIFO principle — what comes out first? | Basic |
| [Q2](#q2) | Implement push/pop/peek with a Python list | Basic |
| [Q3](#q3) | Implement a stack using `collections.deque` | Basic |
| [Q4](#q4) | Safe peek — handle empty stack | Basic |
| [Q5](#q5) | Reverse a list using a stack | Basic |
| [Q6](#q6) | Check if a string is a palindrome using a stack | Basic |
| [Q7](#q7) | Count elements in a stack without destroying it | Basic |
| [Q8](#q8) | Stack vs Queue — spot the difference | Basic |
| [Q9](#q9) | Balanced parentheses — single bracket type `()` | Intermediate |
| [Q10](#q10) | Balanced brackets — multi-type `(){}[]` | Intermediate |
| [Q11](#q11) | Min Stack — O(1) getMin() | Intermediate |
| [Q12](#q12) | Daily temperatures — days until warmer | Intermediate |
| [Q13](#q13) | Next greater element | Intermediate |
| [Q14](#q14) | Browser history with back/forward | Intermediate |
| [Q15](#q15) | Undo/redo — command stack | Intermediate |
| [Q16](#q16) | Evaluate Reverse Polish Notation (RPN) | Intermediate |
| [Q17](#q17) | Simplify file path (`/a/../b/./c`) | Intermediate |
| [Q18](#q18) | Recursion call stack — trace factorial(4) | Intermediate |
| [Q19](#q19) | Decode nested string `3[a2[b]]` | Intermediate |
| [Q20](#q20) | Stock span problem | Intermediate |
| [Q21](#q21) | Largest rectangle in histogram | Advanced |
| [Q22](#q22) | Next greater element II — circular array | Advanced |
| [Q23](#q23) | Trapping rain water with a stack | Advanced |
| [Q24](#q24) | Stack overflow — diagnose and fix deep recursion | Advanced |
| [Q25](#q25) | Design a stack that supports push, pop, and `get_max()` in O(1) | Advanced |

---

## Basic (Q1–Q8)

---

<a id="q1"></a>
### Q1 — What comes out first from a stack?

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


You push the numbers 10, 20, 30 onto a stack (in that order). You then call pop() three times. What is the output order, and why?

<details>
<summary>Hint</summary>

Think of a stack of plates. Which plate did you put on last?

</details>

<details>
<summary>Answer</summary>

**Output order: 30, 20, 10**

The last item pushed is the first item popped. This is the **LIFO** (Last In, First Out) principle.

```python
stack = []
stack.append(10)
stack.append(20)
stack.append(30)

print(stack.pop())  # 30
print(stack.pop())  # 20
print(stack.pop())  # 10
```

**Why:** Each `append` adds to the end of the list. Each `pop()` removes from the end. The end of the list is the "top" of the stack — so the most recent item is always first out.

**Time:** O(1) per push and pop. **Space:** O(n).

</details>

---

<a id="q2"></a>
### Q2 — Implement push / pop / peek with a Python list

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Write a `Stack` class backed by a Python list. It must support:
- `push(val)` — add to top
- `pop()` — remove and return top (return `None` if empty)
- `peek()` — return top without removing (return `None` if empty)
- `is_empty()` — return `True` if the stack has no elements

<details>
<summary>Hint</summary>

The "top" of the stack lives at index `[-1]`. Guard every pop/peek with an empty check.

</details>

<details>
<summary>Answer</summary>

```python
class Stack:
    def __init__(self):
        self._data = []

    def push(self, val):
        self._data.append(val)

    def pop(self):
        if self.is_empty():
            return None
        return self._data.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0


s = Stack()
s.push(1)
s.push(2)
s.push(3)
print(s.peek())   # 3 — top without removing
print(s.pop())    # 3
print(s.pop())    # 2
print(s.pop())    # 1
print(s.pop())    # None — empty, no IndexError
```

**Why:** `list.append` and `list.pop()` both operate on the tail of the list in O(1) (amortized). Guarding pop/peek prevents `IndexError` on empty input — a common interview stumble.

**Time:** O(1) all operations. **Space:** O(n).

</details>

---

<a id="q3"></a>
### Q3 — Implement a stack using `collections.deque`

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Rewrite the same push/pop/peek interface using `collections.deque` instead of a plain list. Why might you choose `deque` over a list for a stack?

<details>
<summary>Hint</summary>

`deque` is a doubly-linked list under the hood. Use `append` and `pop` (right end) — same as list. The difference shows up only when you also need `appendleft`/`popleft`.

</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

class DequeStack:
    def __init__(self):
        self._data = deque()

    def push(self, val):
        self._data.append(val)       # right end = top of stack

    def pop(self):
        if not self._data:
            return None
        return self._data.pop()      # O(1), no memory reallocation

    def peek(self):
        if not self._data:
            return None
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0


s = DequeStack()
s.push("a")
s.push("b")
print(s.peek())   # b
print(s.pop())    # b
print(s.pop())    # a
```

**Why:** A plain Python list occasionally triggers an O(n) memory reallocation when it grows beyond its capacity. `deque` has O(1) guaranteed (not just amortized) appends and pops from both ends. For pure stack use (one end only), either works. Prefer `deque` when you need both-end access too.

**Time:** O(1) guaranteed. **Space:** O(n).

</details>

---

<a id="q4"></a>
### Q4 — Safe peek — handle empty stack

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Write a standalone `safe_peek(stack)` function that returns the top element or raises a custom `StackUnderflowError` with a meaningful message instead of a generic `IndexError`.

<details>
<summary>Hint</summary>

Define a custom exception class that inherits from `Exception`.

</details>

<details>
<summary>Answer</summary>

```python
class StackUnderflowError(Exception):
    pass


def safe_peek(stack: list):
    if not stack:
        raise StackUnderflowError("peek() called on an empty stack")
    return stack[-1]


# Usage
s = [10, 20, 30]
print(safe_peek(s))   # 30

empty = []
try:
    safe_peek(empty)
except StackUnderflowError as e:
    print(f"Caught: {e}")   # Caught: peek() called on an empty stack
```

**Why:** Generic `IndexError: list index out of range` tells the caller nothing about what went wrong. A named exception (`StackUnderflowError`) makes debugging instant — the traceback says exactly what happened. Production code always wraps low-level errors in domain-specific exceptions.

**Time:** O(1). **Space:** O(1).

</details>

---

<a id="q5"></a>
### Q5 — Reverse a list using a stack

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Given a list `[1, 2, 3, 4, 5]`, use a stack to produce `[5, 4, 3, 2, 1]`. Do not use Python's built-in `reversed()` or list slicing.

<details>
<summary>Hint</summary>

Push every element, then pop every element. The LIFO property reverses the order automatically.

</details>

<details>
<summary>Answer</summary>

```python
def reverse_with_stack(items: list) -> list:
    stack = []
    for item in items:
        stack.append(item)       # push

    result = []
    while stack:
        result.append(stack.pop())   # pop — LIFO reverses order

    return result


print(reverse_with_stack([1, 2, 3, 4, 5]))  # [5, 4, 3, 2, 1]
print(reverse_with_stack([]))               # []
print(reverse_with_stack([42]))             # [42]
```

**Why:** Pushing all elements and then popping is the manual equivalent of reversing. This is a fundamental demonstration of LIFO — the same principle that makes recursive functions unwind in reverse order. It also appears inside expression evaluators and string parsers.

**Time:** O(n). **Space:** O(n) for the stack.

</details>

---

<a id="q6"></a>
### Q6 — Palindrome check using a stack

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Write `is_palindrome(s)` that uses a stack to determine whether a string is a palindrome (reads the same forwards and backwards). Ignore case and spaces.

<details>
<summary>Hint</summary>

Push all characters, then pop them and compare to the original left-to-right.

</details>

<details>
<summary>Answer</summary>

```python
def is_palindrome(s: str) -> bool:
    cleaned = s.lower().replace(" ", "")
    stack = list(cleaned)        # push all characters

    for ch in cleaned:
        if stack.pop() != ch:    # compare from back to front
            return False
    return True


print(is_palindrome("racecar"))     # True
print(is_palindrome("Race Car"))    # True  (case + space ignored)
print(is_palindrome("hello"))       # False
print(is_palindrome("A"))           # True
print(is_palindrome(""))            # True
```

**Why:** A palindrome reads the same forwards and backwards. Popping a stack of the characters gives you the reverse. Comparing each popped character against the forward scan detects any mismatch in O(n). This is a clean illustration of LIFO as a reversal tool.

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q7"></a>
### Q7 — Count elements without destroying the stack

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Given a stack (Python list), return the number of elements without calling `len()` on the list directly — use only `push`, `pop`, and `is_empty` operations. The original stack must be intact after the call.

<details>
<summary>Hint</summary>

Pop everything into a temporary stack while counting, then restore.

</details>

<details>
<summary>Answer</summary>

```python
def count_elements(stack: list) -> int:
    temp = []
    count = 0

    # Pop everything, count as we go
    while stack:
        temp.append(stack.pop())
        count += 1

    # Restore original order
    while temp:
        stack.append(temp.pop())

    return count


s = [10, 20, 30, 40]
print(count_elements(s))   # 4
print(s)                   # [10, 20, 30, 40] — unchanged
```

**Why:** This tests that you understand the constraint of stack-only access: no random indexing. The two-stack restore trick is a common interview pattern (also used in sorting a stack). It shows you can work within a limited interface.

**Time:** O(n). **Space:** O(n) for the temp stack.

</details>

---

<a id="q8"></a>
### Q8 — Stack vs Queue: spot the difference

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


You have two data structures. Structure A processes tasks in the order: `[job1, job2, job3]` — job1 is processed first. Structure B processes tasks in the order: `[job3, job2, job1]` — job3 (last added) is processed first.

Which is which? Give a real-world analogy for each and write 3-line Python code to demonstrate each.

<details>
<summary>Hint</summary>

Queue = line at a coffee shop. Stack = stack of unread emails.

</details>

<details>
<summary>Answer</summary>

**Structure A is a Queue (FIFO). Structure B is a Stack (LIFO).**

```python
from collections import deque

# Queue — FIFO: first in, first out
q = deque(["job1", "job2", "job3"])
print(q.popleft())   # job1 — first added, first served

# Stack — LIFO: last in, first out
s = ["job1", "job2", "job3"]
print(s.pop())       # job3 — last added, first served
```

**Real-world analogies:**
- Queue: supermarket checkout line — the first customer in line is served first.
- Stack: browser history — the last page you visited is the first you go back to.

**Why this matters:** Choosing the wrong structure is a hard-to-find bug. If you use a stack for a task scheduler that must respect submission order, later jobs will execute first — exactly the wrong behavior.

**Time:** O(1) both. **Space:** O(n).

</details>

---

## Intermediate (Q9–Q20)

---

<a id="q9"></a>
### Q9 — Balanced parentheses (single type)

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Write `is_balanced(s)` that returns `True` if every `(` has a matching `)` in the correct order. Input contains only `(` and `)`.

<details>
<summary>Hint</summary>

Push `(`, pop on `)`. If stack is empty when you see `)`, it's invalid. At the end, the stack must be empty.

</details>

<details>
<summary>Answer</summary>

```python
def is_balanced(s: str) -> bool:
    stack = []
    for ch in s:
        if ch == '(':
            stack.append(ch)
        elif ch == ')':
            if not stack:
                return False        # closing with nothing open
            stack.pop()
    return len(stack) == 0          # unmatched opens remain?


assert is_balanced("(())")      == True
assert is_balanced("()()")      == True
assert is_balanced("(()")       == False   # unmatched open
assert is_balanced(")(")        == False   # wrong order
assert is_balanced("")          == True
```

**Why:** The most-recently opened bracket must close first — that is LIFO. A stack naturally enforces this. The two failure modes are: (1) a closing bracket arrives with no open partner — caught mid-loop; (2) opens are never closed — caught by checking `len(stack) == 0` at the end. Missing the end-check is the #1 interview mistake on this problem.

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q10"></a>
### Q10 — Balanced brackets (multi-type `(){}[]`)

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Extend the solution to handle `(`, `)`, `{`, `}`, `[`, `]`. Each opener must be closed by its exact partner.

<details>
<summary>Hint</summary>

Use a dictionary mapping each closer to its opener. On a closing bracket, pop and check against the map.

</details>

<details>
<summary>Answer</summary>

```python
def is_valid(s: str) -> bool:
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


assert is_valid("([]{})")   == True
assert is_valid("({[]})")   == True
assert is_valid("({[}])")   == False   # wrong nesting order
assert is_valid("{")        == False   # unclosed
assert is_valid("]")        == False   # closer with nothing open
assert is_valid("")         == True
```

**Why:** The dictionary lookup `match[ch]` maps each closing bracket to the opener it expects. Comparing against `stack[-1]` checks the most-recently-opened bracket — which, by LIFO, must be the one to close first. This single pattern solves LeetCode #20 (Valid Parentheses) verbatim.

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q11"></a>
### Q11 — Min Stack: O(1) getMin()

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Design a stack that supports `push`, `pop`, `top`, and `get_min` — all in O(1) time. `get_min` returns the minimum element currently in the stack.

<details>
<summary>Hint</summary>

Maintain a second "min stack" that tracks the minimum at each level. Push to min stack whenever the new value is ≤ the current min.

</details>

<details>
<summary>Answer</summary>

```python
class MinStack:
    def __init__(self):
        self._stack = []
        self._min_stack = []    # top always holds current minimum

    def push(self, val: int) -> None:
        self._stack.append(val)
        # Push to min_stack if it's empty or new val <= current min
        if not self._min_stack or val <= self._min_stack[-1]:
            self._min_stack.append(val)

    def pop(self) -> None:
        top = self._stack.pop()
        if top == self._min_stack[-1]:
            self._min_stack.pop()   # removed element was the min

    def top(self) -> int:
        return self._stack[-1]

    def get_min(self) -> int:
        return self._min_stack[-1]


ms = MinStack()
ms.push(5)
ms.push(3)
ms.push(7)
ms.push(3)
print(ms.get_min())   # 3
ms.pop()              # remove 3 (duplicate min)
print(ms.get_min())   # 3 (still min — the other 3 is still there)
ms.pop()              # remove 7
print(ms.get_min())   # 3
ms.pop()              # remove 3
print(ms.get_min())   # 5
```

**Why:** Without the auxiliary min stack, `get_min` would require scanning the whole stack — O(n). By maintaining a parallel stack of "minimums seen so far", each push/pop also updates the minimum in O(1). The key: only pop from `_min_stack` when the element being removed equals the current min — that element was the one setting the minimum floor.

**Time:** O(1) all operations. **Space:** O(n).

</details>

---

<a id="q12"></a>
### Q12 — Daily temperatures

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Given a list of daily temperatures, return a list where `result[i]` is the number of days you have to wait after day `i` to get a warmer temperature. If no future day is warmer, use `0`.

Example: `[73, 74, 75, 71, 69, 72, 76, 73]` → `[1, 1, 4, 2, 1, 1, 0, 0]`

<details>
<summary>Hint</summary>

Use a monotonic decreasing stack of indices. When a warmer day arrives, pop all cooler unresolved days — the answer for each is `current_index - popped_index`.

</details>

<details>
<summary>Answer</summary>

```python
def daily_temperatures(temps: list[int]) -> list[int]:
    result = [0] * len(temps)
    stack = []   # indices of days waiting for a warmer day

    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            result[j] = i - j     # days waited = distance between indices
        stack.append(i)

    return result   # remaining indices stay 0 — no warmer day found


print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))
# [1, 1, 4, 2, 1, 1, 0, 0]

print(daily_temperatures([30, 40, 50, 60]))
# [1, 1, 1, 0]

print(daily_temperatures([30, 20, 10]))
# [0, 0, 0]
```

**Why:** The brute-force approach checks every future day for each index — O(n²). The monotonic stack stores "unresolved" days. Each time a warmer day arrives, it resolves all cooler days in the stack at once. Every index is pushed once and popped at most once → O(n) total. Store indices (not values) because you need `i - j` to compute the wait.

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q13"></a>
### Q13 — Next greater element

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Given an array, return an array where `result[i]` is the next element to the right that is strictly greater than `nums[i]`. If none exists, use `-1`.

Example: `[2, 1, 5, 3, 6]` → `[5, 5, 6, 6, -1]`

<details>
<summary>Hint</summary>

Monotonic decreasing stack of indices. When `nums[i] > nums[stack[-1]]`, pop and record the answer.

</details>

<details>
<summary>Answer</summary>

```python
def next_greater_element(nums: list[int]) -> list[int]:
    n = len(nums)
    result = [-1] * n
    stack = []   # indices, monotonically decreasing by value

    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]   # nums[i] is the next greater for idx
        stack.append(i)

    return result   # remaining indices keep -1 (no next greater)


print(next_greater_element([2, 1, 5, 3, 6]))  # [5, 5, 6, 6, -1]
print(next_greater_element([4, 3, 2, 1]))      # [-1, -1, -1, -1]
print(next_greater_element([1, 3, 2, 4]))      # [3, 4, 4, -1]
```

**Why:** Each element enters the stack once (when we reach it) and exits at most once (when a larger element resolves it). Total: 2n operations → O(n). This is the canonical monotonic stack template — understand it once and you can solve daily temperatures, stock span, trapping rain water, and histogram problems by variation.

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q14"></a>
### Q14 — Browser history with back/forward

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


Implement a `Browser` class with:
- `navigate(url)` — go to a new page (clears forward history)
- `back()` — go to the previous page (returns current page if no history)
- `forward()` — go to next page (returns current page if none)
- `current_page()` — return current URL

<details>
<summary>Hint</summary>

Use two stacks: `back_stack` and `forward_stack`. `navigate` clears the forward stack. `back` pops from back, pushes to forward. `forward` does the reverse.

</details>

<details>
<summary>Answer</summary>

```python
class Browser:
    def __init__(self, homepage: str):
        self._current = homepage
        self._back = []
        self._forward = []

    def navigate(self, url: str) -> None:
        self._back.append(self._current)
        self._current = url
        self._forward.clear()   # new navigation invalidates forward history

    def back(self) -> str:
        if not self._back:
            return self._current
        self._forward.append(self._current)
        self._current = self._back.pop()
        return self._current

    def forward(self) -> str:
        if not self._forward:
            return self._current
        self._back.append(self._current)
        self._current = self._forward.pop()
        return self._current

    def current_page(self) -> str:
        return self._current


b = Browser("google.com")
b.navigate("github.com")
b.navigate("docs.python.org")
print(b.back())          # github.com
print(b.back())          # google.com
print(b.forward())       # github.com
b.navigate("openai.com") # clears forward stack
print(b.forward())       # openai.com (no forward — stays)
```

**Why:** Browser back/forward is a classic two-stack problem. Back presses consume from `back_stack` (LIFO — most recent visit first). Forward presses consume from `forward_stack`. When you navigate to a new page, any "future" history is invalid — hence `forward.clear()`. This exact model is used in browser tab implementations.

**Time:** O(1) all operations. **Space:** O(n).

</details>

---

<a id="q15"></a>
### Q15 — Undo/redo with a command stack

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


Implement a simple text buffer with `write(text)`, `undo()`, and `redo()`. Each write is undoable. After an undo, redo restores it. Writing new text clears the redo history.

<details>
<summary>Hint</summary>

Same two-stack pattern as browser history. Store the previous state (or the inverse operation) in the undo stack.

</details>

<details>
<summary>Answer</summary>

```python
class TextBuffer:
    def __init__(self):
        self.text = ""
        self._undo_stack = []   # each item = text state before that write
        self._redo_stack = []

    def write(self, new_text: str) -> None:
        self._undo_stack.append(self.text)   # save current state
        self.text += new_text
        self._redo_stack.clear()             # new write cancels redo history

    def undo(self) -> None:
        if not self._undo_stack:
            return
        self._redo_stack.append(self.text)
        self.text = self._undo_stack.pop()

    def redo(self) -> None:
        if not self._redo_stack:
            return
        self._undo_stack.append(self.text)
        self.text = self._redo_stack.pop()


buf = TextBuffer()
buf.write("Hello")
buf.write(", World")
print(buf.text)    # Hello, World
buf.undo()
print(buf.text)    # Hello
buf.redo()
print(buf.text)    # Hello, World
buf.write("!")
buf.undo()
print(buf.text)    # Hello, World
buf.redo()         # no-op — redo cleared by the write("!")
print(buf.text)    # Hello, World
```

**Why:** Undo systems are LIFO by nature — the most recent action is undone first. Storing snapshots (or inverse operations) in a stack makes undo O(1). The redo stack captures "undone states" so they can be reapplied. Writing new content always clears the redo stack — you can't redo something that was overwritten. This is the Command pattern backed by two stacks.

**Time:** O(1) per operation (snapshot approach). **Space:** O(n * avg_text_length).

</details>

---

<a id="q16"></a>
### Q16 — Evaluate Reverse Polish Notation (RPN)

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Evaluate an arithmetic expression in Reverse Polish Notation. Tokens are integers or one of `+`, `-`, `*`, `/` (truncate toward zero on division).

Example: `["2","1","+","3","*"]` → `9` because `(2 + 1) * 3 = 9`

<details>
<summary>Hint</summary>

Push numbers. When you see an operator, pop two numbers, apply the operator, push the result. The second pop is the LEFT operand.

</details>

<details>
<summary>Answer</summary>

```python
def eval_rpn(tokens: list[str]) -> int:
    stack = []

    for token in tokens:
        if token not in ('+', '-', '*', '/'):
            stack.append(int(token))
        else:
            b = stack.pop()   # right operand
            a = stack.pop()   # left operand — second pop is first operand!
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                stack.append(int(a / b))   # truncate toward zero

    return stack[0]


print(eval_rpn(["2", "1", "+", "3", "*"]))          # 9  → (2+1)*3
print(eval_rpn(["4", "13", "5", "/", "+"]))          # 6  → 4+(13/5)
print(eval_rpn(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]))  # 22
```

**Why:** RPN eliminates the need for operator precedence rules and parentheses — compilers convert infix to postfix (RPN) internally before evaluating. The stack acts as a scratchpad: operands wait until their operator arrives. The operand order bug (`a` and `b` reversed) is the most common RPN mistake in interviews — `b` is popped first but is the right-hand side.

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q17"></a>
### Q17 — Simplify file path

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


Given a Unix file path like `"/a/./b/../c/"`, return the simplified canonical path `"/a/c"`. Rules: `.` means current dir, `..` means parent dir, multiple slashes are ignored.

<details>
<summary>Hint</summary>

Split on `/`. Push directory names. On `..`, pop. On `.` or empty string, skip. Rejoin with `/`.

</details>

<details>
<summary>Answer</summary>

```python
def simplify_path(path: str) -> str:
    stack = []

    for part in path.split('/'):
        if part == '..':
            if stack:
                stack.pop()           # go up one directory
        elif part and part != '.':
            stack.append(part)        # normal directory name

    return '/' + '/'.join(stack)


print(simplify_path("/home/"))              # /home
print(simplify_path("/../"))               # /  (can't go above root)
print(simplify_path("/home//foo/"))        # /home/foo
print(simplify_path("/a/./b/../c/"))       # /a/c
print(simplify_path("/a/b/c/../../../"))   # /
```

**Why:** File system navigation is a stack problem: entering a directory = push, `..` = pop, `.` = no-op. The stack preserves the sequence of real directory names at each level. After processing, rejoining the stack with `/` gives the canonical path. This is how shell built-ins like `cd` and `pwd` work internally.

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q18"></a>
### Q18 — Trace the recursion call stack for `factorial(4)`

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Without running code, draw the call stack when `factorial(4)` is executing at its deepest point. Then describe how it unwinds.

<details>
<summary>Hint</summary>

Each function call pushes a frame. Base case is reached when `n == 0`. Then frames pop one by one.

</details>

<details>
<summary>Answer</summary>

**Call stack at maximum depth (when `factorial(0)` is on top):**

```
TOP
┌─────────────────┐
│ factorial(0)    │  ← base case, returns 1
├─────────────────┤
│ factorial(1)    │  ← waiting for factorial(0)
├─────────────────┤
│ factorial(2)    │  ← waiting for factorial(1)
├─────────────────┤
│ factorial(3)    │  ← waiting for factorial(2)
├─────────────────┤
│ factorial(4)    │  ← original call
└─────────────────┘
BOTTOM
```

**Unwinding:**
- `factorial(0)` returns `1` → popped
- `factorial(1)` computes `1 * 1 = 1` → returns 1, popped
- `factorial(2)` computes `2 * 1 = 2` → returns 2, popped
- `factorial(3)` computes `3 * 2 = 6` → returns 6, popped
- `factorial(4)` computes `4 * 6 = 24` → returns 24, popped

**Stack overflow risk:** Python's default limit is 1000 frames. `factorial(1001)` would crash with `RecursionError`.

```python
import sys
print(sys.getrecursionlimit())   # 1000
```

**Why:** Understanding the call stack is critical for debugging. Every `RecursionError` in production is a stack overflow — the call stack ran out of space. Converting deep recursion to iteration (using an explicit stack on the heap) is the standard fix for production code handling unbounded input.

**Time:** O(n) calls. **Space:** O(n) stack frames.

</details>

---

<a id="q19"></a>
### Q19 — Decode nested string `3[a2[b]]`

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Given an encoded string like `"3[a2[b]]"`, return its decoded form. The rule: `k[encoded_string]` means `encoded_string` repeated `k` times.

<details>
<summary>Hint</summary>

Use a stack. When you see `[`, push the current string and current count. When you see `]`, pop and multiply.

</details>

<details>
<summary>Answer</summary>

```python
def decode_string(s: str) -> str:
    stack = []        # stores (current_string, repeat_count) before each '['
    current = ""
    num = 0

    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)   # handle multi-digit numbers
        elif ch == '[':
            stack.append((current, num))
            current = ""
            num = 0
        elif ch == ']':
            prev_string, count = stack.pop()
            current = prev_string + current * count
        else:
            current += ch

    return current


print(decode_string("3[a]2[bc]"))    # aaabcbc
print(decode_string("3[a2[c]]"))     # accaccacc
print(decode_string("2[abc]3[cd]e")) # abcabccdcdcde
```

**Why:** Nested brackets are a push-on-`[`, pop-on-`]` pattern. The stack preserves the outer context while you process the inner bracket. This is the same mechanism a parser uses for nested function calls, HTML tags, and JSON. The trick with `num = num * 10 + int(ch)` handles multi-digit repeat counts like `12[a]`.

**Time:** O(n * max_k) where max_k is the largest repeat count. **Space:** O(n).

</details>

---

<a id="q20"></a>
### Q20 — Stock span problem

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


For each day's stock price, compute the "span": the number of consecutive days immediately before (and including) today where the price was less than or equal to today's price.

Example: `[100, 80, 60, 70, 60, 75, 85]` → `[1, 1, 1, 2, 1, 4, 6]`

<details>
<summary>Hint</summary>

Maintain a monotonic decreasing stack of `(price, span)` pairs. When today's price is ≥ the stack top, pop and accumulate the span.

</details>

<details>
<summary>Answer</summary>

```python
def stock_span(prices: list[int]) -> list[int]:
    stack = []    # (price, span) pairs — monotonically decreasing by price
    result = []

    for price in prices:
        span = 1
        while stack and stack[-1][0] <= price:
            _, prev_span = stack.pop()
            span += prev_span          # absorb the span of the smaller day
        stack.append((price, span))
        result.append(span)

    return result


print(stock_span([100, 80, 60, 70, 60, 75, 85]))
# [1, 1, 1, 2, 1, 4, 6]
print(stock_span([10, 4, 5, 90, 120, 80]))
# [1, 1, 2, 4, 5, 1]
```

**Why:** The brute-force approach scans backward from each day — O(n²). The monotonic stack compresses consecutive lower prices into a single span value. When a new price resolves older ones, their spans are accumulated. Each element is pushed and popped at most once → O(n). This pattern powers "new N-day high" highlights in financial dashboards.

**Time:** O(n) amortized. **Space:** O(n).

</details>

---

## Advanced (Q21–Q25)

---

<a id="q21"></a>
### Q21 — Largest rectangle in histogram

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Given an array of bar heights representing a histogram, find the area of the largest rectangle that can be formed within the histogram.

Example: `[2, 1, 5, 6, 2, 3]` → `10` (bars of height 5 and 6, width 2)

<details>
<summary>Hint</summary>

Use a monotonic increasing stack of indices. When a shorter bar arrives, pop taller bars and calculate the rectangle width using the current index and the new stack top.

</details>

<details>
<summary>Answer</summary>

```python
def largest_rectangle(heights: list[int]) -> int:
    stack = []   # indices, monotonically increasing by height
    max_area = 0
    heights = heights + [0]   # sentinel: forces all remaining bars to be popped

    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            # width: from stack top (new left boundary) to current i
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)

    return max_area


print(largest_rectangle([2, 1, 5, 6, 2, 3]))   # 10
print(largest_rectangle([2, 4]))                # 4
print(largest_rectangle([6, 2, 5, 4, 5, 1, 6]))# 12
```

**Why:** When a shorter bar arrives, every taller bar to its left that it is "blocking" can now be resolved. The stack maintains bars in increasing order — each bar is the shortest in the range from the stack's previous entry to the current position. The sentinel `[0]` at the end forces all bars to be processed without a separate post-loop cleanup. This is a classic hard-level stack problem (LeetCode #84).

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q22"></a>
### Q22 — Next greater element II (circular array)

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


Same as Q13, but the array is circular — after the last element, wrap around to the first. Return `-1` only if no greater element exists anywhere in the array.

Example: `[1, 2, 1]` → `[2, -1, 2]`

<details>
<summary>Hint</summary>

Simulate two passes over the array using `range(2 * n)` and `i % n`. Only push indices during the first pass.

</details>

<details>
<summary>Answer</summary>

```python
def next_greater_circular(nums: list[int]) -> list[int]:
    n = len(nums)
    result = [-1] * n
    stack = []   # indices

    for i in range(2 * n):      # two passes simulate the circular wrap
        idx = i % n
        while stack and nums[stack[-1]] < nums[idx]:
            result[stack.pop()] = nums[idx]
        if i < n:
            stack.append(idx)   # only push in the first pass

    return result


print(next_greater_circular([1, 2, 1]))         # [2, -1, 2]
print(next_greater_circular([1, 2, 3, 4, 3]))   # [2, 3, 4, -1, 4]
print(next_greater_circular([5, 4, 3, 2, 1]))   # [-1, 5, 5, 5, 5]
```

**Why:** The circular variant can't be solved with a single left-to-right pass because an element near the end might have its next greater at the beginning. The two-pass trick (`2 * n` with `i % n`) makes the array appear to loop once. Crucially, you only push indices in the first pass — otherwise you'd push duplicates and double-count. This is LeetCode #503.

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q23"></a>
### Q23 — Trapping rain water

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Given an elevation map as an array of non-negative integers, compute how much water can be trapped after a rain.

Example: `[0,1,0,2,1,0,1,3,2,1,2,1]` → `6`

<details>
<summary>Hint</summary>

Use a monotonic stack. When a taller wall arrives, the top of the stack is the "floor" of the trapped water and the new wall is the right boundary. The element just below the floor is the left boundary.

</details>

<details>
<summary>Answer</summary>

```python
def trap(height: list[int]) -> int:
    stack = []   # indices, monotonically decreasing by height
    water = 0

    for i, h in enumerate(height):
        while stack and height[stack[-1]] < h:
            floor_idx = stack.pop()
            if not stack:
                break
            left_idx = stack[-1]
            width = i - left_idx - 1
            bounded_height = min(height[left_idx], h) - height[floor_idx]
            water += width * bounded_height

        stack.append(i)

    return water


print(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))   # 6
print(trap([4, 2, 0, 3, 2, 5]))                       # 9
print(trap([3, 0, 2, 0, 4]))                           # 7
```

**Why:** The stack approach processes water layer by layer. When a taller wall arrives, it can form a container with the left wall still in the stack. The "floor" is the popped element (the dip), the left boundary is the new stack top, and the right boundary is the current index. Width × bounded height gives the water in that section. Each element is pushed/popped once → O(n). This is LeetCode #42, a classic interview problem.

**Time:** O(n). **Space:** O(n).

</details>

---

<a id="q24"></a>
### Q24 — Diagnose and fix a stack overflow

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


The following code crashes with `RecursionError` for large inputs. Explain why, then rewrite it iteratively using an explicit stack.

```python
def sum_nested(data):
    """Sum all integers in arbitrarily nested lists."""
    total = 0
    for item in data:
        if isinstance(item, list):
            total += sum_nested(item)   # recursive
        else:
            total += item
    return total
```

<details>
<summary>Hint</summary>

Each recursive call pushes a frame onto the call stack. Replace the call stack with your own explicit stack on the heap — it can grow to any size without hitting Python's recursion limit.

</details>

<details>
<summary>Answer</summary>

**Root cause:** Each nested list triggers a recursive call, pushing a new frame onto Python's call stack. Python's default recursion limit is 1000. A list nested 1001 levels deep crashes with `RecursionError: maximum recursion depth exceeded`.

```python
def sum_nested_iterative(data) -> int:
    """
    Same logic as sum_nested, but uses an explicit stack on the heap.
    Safe for any nesting depth — no recursion limit applies.
    """
    total = 0
    stack = [data]   # start by pushing the outermost list

    while stack:
        item = stack.pop()
        if isinstance(item, list):
            for element in item:
                stack.append(element)   # push all children for later processing
        else:
            total += item

    return total


# Test: deeply nested list that would crash the recursive version
deep = [1]
for _ in range(2000):
    deep = [deep, 1]   # nesting depth 2000

print(sum_nested_iterative(deep))   # 2001 — works fine


# Verify correctness on simple cases
assert sum_nested_iterative([1, [2, [3, [4]]]]) == 10
assert sum_nested_iterative([])                  == 0
assert sum_nested_iterative([1, 2, 3])           == 6
```

**Why:** Moving the stack from the call stack (a fixed-size OS resource) to the heap (limited only by available RAM) is the standard production fix for deep recursion. JSON parsers, XML parsers, and file system walkers all use this pattern. The explicit stack holds items to process — when an item is a list, push its children; when it is a value, add to total.

**Time:** O(n) where n = total number of elements. **Space:** O(depth) for the stack.

</details>

---

<a id="q25"></a>
### Q25 — Design a stack with O(1) push, pop, and `get_max()`

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


Design a stack supporting `push`, `pop`, `top`, and `get_max()` — all O(1). `get_max` returns the maximum element currently in the stack.

<details>
<summary>Hint</summary>

Same two-stack strategy as Min Stack (Q11), but track maximum instead. Push to the max stack whenever the new value is ≥ the current max.

</details>

<details>
<summary>Answer</summary>

```python
class MaxStack:
    def __init__(self):
        self._stack = []
        self._max_stack = []   # top is always the current maximum

    def push(self, val: int) -> None:
        self._stack.append(val)
        if not self._max_stack or val >= self._max_stack[-1]:
            self._max_stack.append(val)

    def pop(self) -> int | None:
        if not self._stack:
            return None
        val = self._stack.pop()
        if val == self._max_stack[-1]:
            self._max_stack.pop()   # max was removed
        return val

    def top(self) -> int | None:
        return self._stack[-1] if self._stack else None

    def get_max(self) -> int | None:
        return self._max_stack[-1] if self._max_stack else None


ms = MaxStack()
ms.push(3)
ms.push(1)
ms.push(5)
ms.push(5)
ms.push(2)
print(ms.get_max())   # 5
ms.pop()              # removes 2
print(ms.get_max())   # 5
ms.pop()              # removes 5 (one of the two 5s)
print(ms.get_max())   # 5 (the other 5 is still there)
ms.pop()              # removes 5
print(ms.get_max())   # 3
ms.pop()              # removes 1
print(ms.get_max())   # 3
```

**Why:** Without the auxiliary max stack, `get_max` scans the whole stack — O(n). The parallel max stack maintains the running maximum at each depth level. The `>=` comparison (not `>`) is critical: if you push two equal maximums, both must be tracked — otherwise popping one would incorrectly remove the max from `_max_stack` even though another copy still exists. Compare and contrast with Q11 (Min Stack) — the logic is symmetric.

**Time:** O(1) all operations. **Space:** O(n).

</details>

---

**[Back to README](../README.md)**

**Prev:** [← Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Queue — Theory →](../09_queue/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
