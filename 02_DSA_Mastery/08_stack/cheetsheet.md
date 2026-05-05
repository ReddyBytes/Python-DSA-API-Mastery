## STACK — QUICK REFERENCE CHEATSHEET

```
┌────────────────────────────────────────────────┐
│  LIFO — Last In, First Out                     │
│  Think: undo/redo, DFS, matching, history      │
└────────────────────────────────────────────────┘
```

---

## OPERATIONS COMPLEXITY

```
┌───────────────┬──────────────────────┬──────────────────────┐
│ Operation     │ list[]               │ collections.deque    │
├───────────────┼──────────────────────┼──────────────────────┤
│ push          │ O(1) amortized       │ O(1)                 │
│ pop           │ O(1) amortized       │ O(1)                 │
│ peek (top)    │ O(1)  stack[-1]      │ O(1)  dq[-1]         │
│ isEmpty       │ O(1)  not stack      │ O(1)  not dq         │
│ search        │ O(n)                 │ O(n)                 │
│ Space         │ O(n)                 │ O(n)                 │
└───────────────┴──────────────────────┴──────────────────────┘
Prefer list[] for stacks — cleaner syntax, same performance.
Use deque only when you also need O(1) operations on both ends.
```

---

## PYTHON STACK SYNTAX

```python
stack = []
stack.append(x)     # push
stack.pop()         # pop — raises IndexError if empty, check first
stack[-1]           # peek top without removing
if stack: ...       # isEmpty check (truthy)
len(stack)          # size

# Safe pop
val = stack.pop() if stack else None
```

---

## MONOTONIC STACK PATTERNS

### Next Greater Element (NGE)
```python
def next_greater(nums):
    n = len(nums)
    result = [-1] * n
    stack = []           # stores indices; stack is monotonically decreasing

    for i in range(n):
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]    # nums[i] is NGE for nums[idx]
        stack.append(i)

    return result        # remaining indices in stack have no NGE → -1
```

### Next Smaller Element (NSE)
```python
def next_smaller(nums):
    n = len(nums)
    result = [-1] * n
    stack = []           # monotonically increasing

    for i in range(n):
        while stack and nums[stack[-1]] > nums[i]:  # flip comparison
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result
```

### Daily Temperatures Pattern
```python
def daily_temperatures(temps):
    result = [0] * len(temps)
    stack = []                      # indices of unresolved days

    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            result[j] = i - j       # days to wait = distance between indices
        stack.append(i)

    return result
# Generalization: "how many steps until condition is met" → monotonic stack
```

---

## BALANCED PARENTHESES TEMPLATE

```python
def is_valid(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}

    for ch in s:
        if ch in mapping:                       # closing bracket
            top = stack.pop() if stack else '#'
            if mapping[ch] != top:
                return False
        else:
            stack.append(ch)                    # push opening bracket

    return not stack                            # valid iff stack is empty
```

---

## EXPRESSION EVALUATION TEMPLATE

```python
def eval_expr(s):
    stack = []
    num = 0
    sign = 1       # +1 or -1
    result = 0

    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch in '+-':
            result += sign * num
            num = 0
            sign = 1 if ch == '+' else -1
        elif ch == '(':
            stack.append(result)    # push current result
            stack.append(sign)      # push sign before parenthesis
            result = 0
            sign = 1
        elif ch == ')':
            result += sign * num
            num = 0
            result *= stack.pop()   # apply sign before '('
            result += stack.pop()   # add result before '('

    return result + sign * num
```

---

## ITERATIVE DFS WITH STACK

```python
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        # process node here
        for neighbor in graph[node]:
            if neighbor not in visited:
                stack.append(neighbor)

# Tree DFS (pre-order)
def preorder(root):
    if not root: return []
    result, stack = [], [root]
    while stack:
        node = stack.pop()
        result.append(node.val)
        if node.right: stack.append(node.right)  # right first (popped last)
        if node.left:  stack.append(node.left)
    return result
```

---

## VALID STACK SEQUENCES

```python
def validate_stack_sequences(pushed, popped):
    stack = []
    j = 0                              # pointer into popped sequence
    for val in pushed:
        stack.append(val)
        while stack and stack[-1] == popped[j]:
            stack.pop()
            j += 1
    return not stack                   # valid if stack is empty at end
```

---

## WHEN TO USE STACK vs QUEUE vs DEQUE

```
┌────────────┬──────────────────────────────────────────────────────────┐
│ Structure  │ Use When                                                 │
├────────────┼──────────────────────────────────────────────────────────┤
│ Stack      │ DFS, backtracking, undo/redo, expression parsing,        │
│            │ matching brackets, next greater/smaller element          │
├────────────┼──────────────────────────────────────────────────────────┤
│ Queue      │ BFS, level-order traversal, task scheduling,             │
│            │ producer-consumer, sliding window (FIFO eviction)        │
├────────────┼──────────────────────────────────────────────────────────┤
│ Deque      │ Sliding window max/min (monotonic deque),                │
│            │ palindrome check, when you need O(1) at both ends        │
└────────────┴──────────────────────────────────────────────────────────┘
```

---

## COMMON GOTCHAS

```
TRAP 1: Popping from empty stack
  Always check: if stack: stack.pop()  or use try/except IndexError

TRAP 2: Forgetting leftover elements in monotonic stack
  After loop, remaining stack elements may need processing (e.g., mark -1).

TRAP 3: Storing values vs indices in monotonic stack
  Store INDICES — you can always recover values, but need indices for
  distance/span calculations.

TRAP 4: Using deque.appendleft / popleft as a stack
  That's queue behavior. Use append + pop for stack (right end only).

TRAP 5: Monotonic stack direction
  NGE (next greater): maintain decreasing stack (pop when nums[i] > top)
  NSE (next smaller): maintain increasing stack (pop when nums[i] < top)
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Visual Explanation](./visual_explanation.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
