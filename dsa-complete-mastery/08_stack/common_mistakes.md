# Stack — Common Mistakes & Error Prevention

A focused guide on the bugs that appear most often when using stacks in interviews and real code. Each mistake includes a broken implementation, an explanation of why it fails, and a corrected version with test cases that expose the bug.

---

## Mistake 1: `pop(0)` Instead of `pop()` — Queue Behaviour on a Stack

### The Confusion

A stack is **Last-In-First-Out (LIFO)**. When you use a Python `list` as a stack:
- `.append(x)` pushes to the **end** — O(1)
- `.pop()` pops from the **end** — O(1) — this is the correct stack operation

`.pop(0)` removes the **first** element (FIFO), making it a queue. It is also **O(n)** because every remaining element must shift left.

### Wrong Code

```python
# WRONG: pop(0) gives FIFO order (queue), not LIFO order (stack)
def process_stack_wrong(items):
    stack = []
    for item in items:
        stack.append(item)

    result = []
    while stack:
        result.append(stack.pop(0))   # BUG: pops from front — this is a queue!
    return result

# --- Test that exposes the bug ---
print(process_stack_wrong([1, 2, 3]))
# Expected (LIFO): [3, 2, 1]
# Actual (FIFO):   [1, 2, 3]  <-- BUG
```

### Correct Code

```python
def process_stack_correct(items):
    stack = []
    for item in items:
        stack.append(item)

    result = []
    while stack:
        result.append(stack.pop())    # pops from end — LIFO, O(1)
    return result

# If you actually need a queue, use collections.deque:
from collections import deque

def process_queue_correct(items):
    q = deque()
    for item in items:
        q.append(item)

    result = []
    while q:
        result.append(q.popleft())   # O(1) dequeue from front
    return result

# --- Tests ---
assert process_stack_correct([1, 2, 3]) == [3, 2, 1]   # LIFO
assert process_queue_correct([1, 2, 3]) == [1, 2, 3]   # FIFO
print("Stack vs queue order tests passed.")
```

### Performance Comparison

```
list.pop(0)   → O(n) per call — all elements shift left
list.pop()    → O(1) per call — no shifting needed
deque.popleft() → O(1) per call — doubly linked list, no shifting
```

---

## Mistake 2: Popping Without Checking Empty

### The Confusion

Calling `.pop()` on an empty list raises `IndexError`. In complex stack-based algorithms (bracket matching, expression evaluation, undo systems), it is easy to pop more times than you push.

### Wrong Code

```python
# WRONG: no empty check before pop
def top_of_stack_wrong(stack):
    return stack.pop()   # IndexError if stack is empty

def calculate_wrong(tokens):
    stack = []
    for token in tokens:
        if token.lstrip("-").isdigit():
            stack.append(int(token))
        else:
            b = stack.pop()
            a = stack.pop()   # BUG: crashes if fewer than 2 elements remain
            if token == "+": stack.append(a + b)
            elif token == "-": stack.append(a - b)
    return stack.pop()

# --- Test that exposes the bug ---
try:
    top_of_stack_wrong([])   # IndexError!
except IndexError as e:
    print(f"BUG caught: {e}")   # list index out of range
```

### Correct Code

```python
# CORRECT: always guard before pop
def top_of_stack_correct(stack):
    if not stack:
        return None   # or raise a custom exception with a meaningful message
    return stack.pop()

def calculate_correct(tokens):
    stack = []
    for token in tokens:
        if token.lstrip("-").isdigit():
            stack.append(int(token))
        else:
            if len(stack) < 2:
                raise ValueError(f"Invalid expression: not enough operands for '{token}'")
            b = stack.pop()
            a = stack.pop()
            if token == "+": stack.append(a + b)
            elif token == "-": stack.append(a - b)
            elif token == "*": stack.append(a * b)
            elif token == "/": stack.append(int(a / b))

    if len(stack) != 1:
        raise ValueError("Invalid expression: leftover operands")
    return stack.pop()

# Peek helper (look without popping)
def peek(stack):
    return stack[-1] if stack else None

# --- Tests ---
assert top_of_stack_correct([]) is None
assert top_of_stack_correct([1, 2, 3]) == 3

assert calculate_correct(["2", "1", "+", "3", "*"]) == 9   # (2+1)*3
assert calculate_correct(["4", "13", "5", "/", "+"]) == 6  # 4+(13/5)

assert peek([]) is None
assert peek([10, 20]) == 20   # peeks without removing

print("Empty-check tests passed.")
```

---

## Mistake 3: Monotonic Stack — Forgetting to Process Remaining Elements

### The Confusion

In "next greater element" and similar problems, the stack accumulates indices of elements that have **not yet found their answer**. When the loop ends, those elements are still in the stack — their answer is "none" (typically `-1` or `0`). Forgetting to handle them leaves the result array partially unfilled.

### Wrong Code

```python
# WRONG: loop ends but remaining stack elements are never processed
def next_greater_wrong(nums):
    n = len(nums)
    result = [-1] * n
    stack = []   # stores indices

    for i in range(n):
        # pop all indices whose "next greater" is nums[i]
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    # BUG: elements left in `stack` never have result set — but result was
    # initialised to -1 so... wait, actually this specific case works by luck
    # because the default is -1.
    #
    # The bug appears in VARIANTS where the default is NOT -1, e.g., sum of
    # subarray minimums or "next greater element circular":
    return result

# The real bug shows in circular next-greater-element:
def next_greater_circular_wrong(nums):
    n = len(nums)
    result = [-1] * n
    stack = []

    # Only one pass — misses wrap-around lookups
    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:
            result[stack.pop()] = nums[i]
        stack.append(i)

    return result   # BUG: wrap-around elements never resolved

# --- Test that exposes the bug ---
print(next_greater_circular_wrong([1, 2, 1]))
# Expected: [2, -1, 2]  (1 at index 2 wraps around and finds 2 at index 1... wait:
#   index 0: next greater going right/circular is 2  → 2
#   index 1: no element greater than 2 in circular   → -1
#   index 2: next greater wrapping around is 2       → 2 (at index 1 of wrap)
# Actual:   [2, -1, -1]  <-- BUG: index 2 never resolved
```

### Correct Code

```python
def next_greater_correct(nums):
    n = len(nums)
    result = [-1] * n
    stack = []

    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:
            result[stack.pop()] = nums[i]
        stack.append(i)

    # Remaining elements in stack have no next greater — already -1 by default
    return result

def next_greater_circular_correct(nums):
    n = len(nums)
    result = [-1] * n
    stack = []

    # Two passes simulate the circular array
    for i in range(2 * n):
        idx = i % n
        while stack and nums[stack[-1]] < nums[idx]:
            result[stack.pop()] = nums[idx]
        if i < n:
            stack.append(idx)   # only push indices from the first pass

    return result

# --- Tests ---
assert next_greater_correct([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
assert next_greater_correct([1, 3, 2])        == [3, -1, -1]

assert next_greater_circular_correct([1, 2, 1])       == [2, -1, 2]
assert next_greater_circular_correct([3, 1, 2, 4])    == [4, 2, 4, -1]
assert next_greater_circular_correct([1, 2, 3, 4, 3]) == [2, 3, 4, -1, 4]

print("Monotonic stack tests passed.")
```

---

## Mistake 4: Balanced Brackets — Returning `True` on a Non-Empty Stack

### The Confusion

After processing all characters, the stack may still contain unmatched opening brackets. Returning `True` unconditionally at the end means `"((("` passes validation.

### Wrong Code

```python
# WRONG: returns True without checking if stack is empty
def is_balanced_wrong(s):
    stack = []
    matching = {")": "(", "}": "{", "]": "["}

    for ch in s:
        if ch in "({[":
            stack.append(ch)
        elif ch in ")}]":
            if not stack or stack[-1] != matching[ch]:
                return False
            stack.pop()

    return True   # BUG: ignores unmatched opening brackets still in stack!

# --- Tests that expose the bug ---
print(is_balanced_wrong("((("))   # Expected: False — Actual: True  BUG
print(is_balanced_wrong("({["))   # Expected: False — Actual: True  BUG
print(is_balanced_wrong("((())")) # Expected: False — Actual: True  BUG
```

### Correct Code

```python
def is_balanced_correct(s):
    stack = []
    matching = {")": "(", "}": "{", "]": "["}

    for ch in s:
        if ch in "({[":
            stack.append(ch)
        elif ch in ")}]":
            if not stack or stack[-1] != matching[ch]:
                return False
            stack.pop()

    return len(stack) == 0   # stack must be empty — all opens were closed

# --- Tests ---
assert is_balanced_correct("()")        == True
assert is_balanced_correct("()[]{}")    == True
assert is_balanced_correct("([])")      == True
assert is_balanced_correct("(((")       == False   # was True with wrong code
assert is_balanced_correct("({[")       == False   # was True with wrong code
assert is_balanced_correct("((())")     == False   # was True with wrong code
assert is_balanced_correct("(]")        == False
assert is_balanced_correct("")          == True    # empty string is balanced
assert is_balanced_correct("]")         == False

print("Balanced brackets tests passed.")
```

---

## Mistake 5: DFS with Explicit Stack — Marking Visited When Popping Instead of Pushing

### The Confusion

When doing iterative DFS with an explicit stack, if you mark a node as visited only when you **pop** it, the same node can be pushed onto the stack multiple times by different neighbours before it is ever popped. This leads to redundant processing and, in graphs with cycles, potential infinite loops.

The fix: mark nodes as visited **when you push** them, not when you pop them.

### Wrong Code

```python
from collections import defaultdict

def dfs_count_wrong(graph, start):
    """Count nodes reachable from start. Wrong: marks visited on pop."""
    visited = set()
    stack = [start]
    count = 0

    while stack:
        node = stack.pop()
        if node in visited:   # guard helps, but node was pushed multiple times
            continue
        visited.add(node)     # BUG: mark on pop — duplicates already in stack
        count += 1
        for neighbour in graph[node]:
            stack.append(neighbour)   # push WITHOUT marking — allows duplicates

    return count

# --- Test that exposes the inefficiency / bug ---
# Build a graph where B and C both connect to D
graph = defaultdict(list)
graph["A"] = ["B", "C"]
graph["B"] = ["D"]
graph["C"] = ["D"]
graph["D"] = []

# Add instrumentation to count how many times D is pushed
push_count = {"D": 0}
def dfs_instrumented_wrong(graph, start):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for neighbour in graph[node]:
            if neighbour == "D":
                push_count["D"] += 1
            stack.append(neighbour)   # D pushed twice — once from B, once from C

dfs_instrumented_wrong(graph, "A")
print(f"D was pushed {push_count['D']} times")   # prints 2 — wasted work
# In a dense graph or with cycles this balloons severely
```

### Correct Code

```python
def dfs_count_correct(graph, start):
    """Count nodes reachable from start. Correct: marks visited on push."""
    visited = set([start])   # mark start as visited immediately
    stack = [start]
    count = 0

    while stack:
        node = stack.pop()
        count += 1
        for neighbour in graph[node]:
            if neighbour not in visited:
                visited.add(neighbour)    # mark BEFORE pushing
                stack.append(neighbour)

    return count

# --- Tests ---
graph1 = defaultdict(list)
graph1["A"] = ["B", "C"]
graph1["B"] = ["D"]
graph1["C"] = ["D"]
graph1["D"] = []

assert dfs_count_correct(graph1, "A") == 4   # A, B, C, D

# Graph with a cycle — wrong version would infinite loop without the `if in visited` guard
graph2 = defaultdict(list)
graph2[0] = [1, 2]
graph2[1] = [0, 3]   # cycle back to 0
graph2[2] = [3]
graph2[3] = []

assert dfs_count_correct(graph2, 0) == 4   # 0, 1, 2, 3

# Disconnected node — should not be counted
graph3 = defaultdict(list)
graph3[0] = [1]
graph3[1] = []
graph3[2] = []   # disconnected

assert dfs_count_correct(graph3, 0) == 2   # only 0 and 1 reachable

print("DFS stack tests passed.")
```

### Visual Comparison

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

---

## Summary Table

| # | Mistake                                        | Root Cause                                  | Fix                                              |
|---|------------------------------------------------|---------------------------------------------|--------------------------------------------------|
| 1 | `pop(0)` on a list used as a stack             | Confuses stack (LIFO) with queue (FIFO)     | Use `pop()` for stack; `deque.popleft()` for queue |
| 2 | Pop without empty check                        | Assumes elements always exist               | Guard with `if stack:` or `len(stack) >= k`      |
| 3 | Ignoring leftover stack after loop             | Remaining elements have no "next greater"   | Process remaining stack or initialise with defaults |
| 4 | `return True` without checking stack is empty  | Unmatched opening brackets go undetected    | `return len(stack) == 0`                         |
| 5 | Mark visited on pop instead of push            | Same node pushed multiple times by neighbours | Mark visited immediately when pushing            |
