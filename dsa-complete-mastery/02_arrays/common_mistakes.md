# Common Mistakes with Python Arrays and Lists

> "Those who do not learn from their bugs are doomed to repeat them — usually at 2am, the night before an interview."

This guide covers the most common array/list mistakes in Python, explained with stories, analogies, and enough detail that you will recognize the bug the next time you are staring at a wrong answer on LeetCode at midnight.

---

## Table of Contents

1. [Modifying a List While Iterating](#1-modifying-a-list-while-iterating)
2. [Off-by-One in Slicing](#2-off-by-one-in-slicing)
3. [Shallow Copy vs Deep Copy](#3-shallow-copy-vs-deep-copy)
4. [List Multiplication Trap](#4-list-multiplication-trap)
5. [pop(0) is O(n) Not O(1)](#5-pop0-is-on-not-o1)
6. [Confusing append vs extend vs +](#6-confusing-append-vs-extend-vs-)
7. [Forgetting that sort() Returns None](#7-forgetting-that-sort-returns-none)
8. [Two-Pointer Without Pre-Sorting](#8-two-pointer-without-pre-sorting)
9. [Prefix Sum Off-by-One](#9-prefix-sum-off-by-one)
10. [Kadane's Algorithm State Reset](#10-kadanes-algorithm-state-reset)

---

## 1. Modifying a List While Iterating

### The Story: The Moving Escalator

Imagine you are standing on an escalator, counting the people in front of you one by one. Every time you count someone, they vanish and the next person takes a step forward. But here is the problem: you already moved *past* the gap where the vanished person was. You skipped someone without realizing it.

This is exactly what Python does when you remove elements from a list while iterating over it. Python's `for` loop uses an internal index counter. When you delete an element, everything shifts left — but the counter still advances by 1. The element that slid into the deleted slot gets skipped entirely.

### The WRONG Code

```python
# WRONG: Removing even numbers while iterating
numbers = [1, 2, 3, 4, 5, 6]

for num in numbers:
    if num % 2 == 0:
        numbers.remove(num)  # BUG: modifying the list we are iterating

print(numbers)
# Expected: [1, 3, 5]
# Actual:   [1, 3, 5, 6]  <-- 6 was NOT removed!
```

### Visual Trace: What Actually Happens

Watch the internal index counter (shown as `^`) step through the list as elements vanish beneath it:

```
Initial list:  [1, 2, 3, 4, 5, 6]
Internal idx:   0  1  2  3  4  5

--- Step 0: index=0, num=1 ---
  [1, 2, 3, 4, 5, 6]
   ^
  1 is odd, skip.

--- Step 1: index=1, num=2 ---
  [1, 2, 3, 4, 5, 6]
      ^
  2 is even! Call numbers.remove(2)

  List becomes: [1, 3, 4, 5, 6]
  Index advances to 2...

--- Step 2: index=2, num=4 ---
  [1, 3, 4, 5, 6]
         ^
  4 is even! Call numbers.remove(4)
  (Notice we SKIPPED index 1, which is now 3)

  List becomes: [1, 3, 5, 6]
  Index advances to 3...

--- Step 3: index=3, num=6 ---
  [1, 3, 5, 6]
            ^
  6 is even! Call numbers.remove(6)

  List becomes: [1, 3, 5]

  Wait... actually Python sees index 3 is out of range after this,
  but the issue: what about 2? It was at index 1.
  After removing 2, the list was [1, 3, 4, 5, 6].
  Index 1 is now '3', which we NEVER evaluated.
  Then we saw 4 (index 2), removed it.
  List became [1, 3, 5, 6].
  Index 3 is '6', we removed it.
  List is [1, 3, 5] — looks right here!

  But try a different input to see the skip:
```

Let's use a more revealing example:

```python
# Even more revealing: removing 2 and 4 adjacent
numbers = [2, 4, 6]
for num in numbers:
    if num % 2 == 0:
        numbers.remove(num)

print(numbers)  # Expected: []
                # Actual:   [4]  <-- 4 was skipped!
```

```
Trace for [2, 4, 6]:

Step 0: index=0, num=2
  [2, 4, 6]
   ^
  remove(2) -> [4, 6]
  index advances to 1...

Step 1: index=1, num=6
  [4, 6]
      ^
  remove(6) -> [4]
  index advances to 2, out of range, loop ends.

  4 was NEVER visited! It slid into index 0,
  but we already passed index 0.
```

### The RIGHT Approaches

**Approach A: Iterate over a copy, modify the original**

```python
# RIGHT: Iterate over a copy
numbers = [2, 4, 6, 1, 3, 5]

for num in numbers[:]:   # numbers[:] creates a full copy
    if num % 2 == 0:
        numbers.remove(num)

print(numbers)  # [1, 3, 5] -- correct!
```

**Approach B: List comprehension (cleanest and most Pythonic)**

```python
# RIGHT: List comprehension builds a new list
numbers = [2, 4, 6, 1, 3, 5]
numbers = [num for num in numbers if num % 2 != 0]

print(numbers)  # [1, 3, 5] -- correct!
```

**Approach C: Iterate in reverse (works for index-based deletion)**

```python
# RIGHT: Reverse iteration -- deletions don't affect unvisited elements
numbers = [2, 4, 6, 1, 3, 5]

for i in range(len(numbers) - 1, -1, -1):
    if numbers[i] % 2 == 0:
        numbers.pop(i)

print(numbers)  # [1, 3, 5] -- correct!
```

Why does reverse work? When you delete at index `i`, only elements at index `>= i` shift. Since we are iterating from right to left, we have already processed those higher indices. The lower indices we have not visited yet are unaffected.

**Approach D: Collect indices, then delete (useful for complex conditions)**

```python
# RIGHT: Two-pass approach
numbers = [2, 4, 6, 1, 3, 5]
to_remove = [i for i, num in enumerate(numbers) if num % 2 == 0]

for i in reversed(to_remove):   # reversed so indices stay valid
    numbers.pop(i)

print(numbers)  # [1, 3, 5] -- correct!
```

### Mini Test Case

```python
def remove_evens_wrong(lst):
    for num in lst:
        if num % 2 == 0:
            lst.remove(num)
    return lst

def remove_evens_right(lst):
    return [num for num in lst if num % 2 != 0]

test = [2, 4, 6, 8]
print(remove_evens_wrong(test[:]))   # [4, 8] -- WRONG, skipped 4 and 8
print(remove_evens_right(test[:]))   # []     -- correct
```

---

## 2. Off-by-One in Slicing

### The Story: The Bread Slicer

You tell the bread slicer: "Give me slices from position 1 to position 5." In Python's world, position 5 is *exclusive* — the slicer stops just before it. So you get slices 1, 2, 3, 4 (four slices). If you meant to get five slices including position 5, you needed to say "1 to 6."

This exclusive end-index is the source of countless off-by-one bugs in Python slicing.

### The WRONG Code

```python
arr = [10, 20, 30, 40, 50, 60, 70]
#       0   1   2   3   4   5   6

n = len(arr)

# BUG: Trying to get the last 3 elements
last_three = arr[n-3:n-1]   # WRONG: only gets 2 elements
print(last_three)  # [50, 60] -- missing 70!

# BUG: Trying to get elements from index 1 to 4 inclusive
middle = arr[1:4]   # This gets indices 1, 2, 3 -- is that what you meant?
print(middle)       # [20, 30, 40] -- index 4 (value 50) is NOT included

# BUG: Subarray for range [i, j] inclusive
i, j = 2, 5
subarray = arr[i:j]     # WRONG if j is inclusive
print(subarray)          # [30, 40, 50, 60] -- this is arr[2], arr[3], arr[4], arr[5]?
                         # Wait, arr[2:5] = [30, 40, 50] -- only up to index 4!
```

### Visual Trace: Slicing Boundaries

Think of slices as fences between elements, not at elements:

```
Index:    0    1    2    3    4    5    6
Value:   10   20   30   40   50   60   70
       |    |    |    |    |    |    |    |
Fence:  0    1    2    3    4    5    6    7

arr[2:5] cuts at fence 2 and fence 5:
       |    |[   2    3    4   ]|    |
              30   40   50
Result: [30, 40, 50]  -- 3 elements, indices 2,3,4

arr[2:5] does NOT include index 5 (value 60).
To include index 5, you need arr[2:6].
```

### Common Off-by-One Scenarios

```python
arr = [10, 20, 30, 40, 50, 60, 70]

# ---- Scenario 1: "Last N elements" ----
n = 3

wrong = arr[len(arr)-n : len(arr)-1]  # WRONG: misses last element
right = arr[-n:]                       # RIGHT: last 3 elements
right2 = arr[len(arr)-n:]              # RIGHT: explicit form

print(wrong)   # [40, 50, 60] -- only 2... wait, len-3=4, len-1=6: [50,60] -- 2 elements!
print(right)   # [50, 60, 70] -- correct


# ---- Scenario 2: "Subarray from index i to j inclusive" ----
i, j = 1, 4   # we want indices 1, 2, 3, 4

wrong = arr[i:j]       # WRONG: only gets indices 1, 2, 3
right = arr[i:j+1]     # RIGHT: j+1 because end is exclusive

print(wrong)   # [20, 30, 40]       -- index 4 (value 50) missing!
print(right)   # [20, 30, 40, 50]   -- correct


# ---- Scenario 3: All but last element ----
wrong = arr[0:len(arr)-1]   # Actually this IS right for "all but last"
right = arr[:-1]            # Same thing, cleaner

print(wrong)   # [10, 20, 30, 40, 50, 60] -- correct (no 70)
print(right)   # [10, 20, 30, 40, 50, 60] -- correct


# ---- Scenario 4: Sliding window subarray ----
# Window of size k starting at index start
k = 3
start = 2

wrong = arr[start : start + k - 1]  # WRONG: gets k-1 elements
right = arr[start : start + k]       # RIGHT: gets exactly k elements

print(wrong)   # [30, 40]       -- only 2 elements!
print(right)   # [30, 40, 50]   -- correct 3 elements
```

### The Golden Rule

```
Python slice arr[start:end]:
- Includes index: start, start+1, ..., end-1
- EXCLUDES index: end
- Number of elements: end - start

So if you want indices [i, j] inclusive:
    arr[i : j+1]

If you want exactly k elements starting at i:
    arr[i : i+k]
```

### Mini Test Case

```python
arr = [1, 2, 3, 4, 5]

# Test: get middle 3 elements (indices 1, 2, 3)
wrong = arr[1:3]   # [2, 3]       -- only 2 elements!
right = arr[1:4]   # [2, 3, 4]    -- correct!

assert right == [2, 3, 4], f"Got {right}"
print("Slicing test passed!")
```

---

## 3. Shallow Copy vs Deep Copy

### The Story: The Blueprint vs The Building

Imagine you want a copy of a house blueprint. You take a photocopy. Both the original and the photocopy show the same rooms. Now imagine you scribble "add a window" on one room in the photocopy. Because it is just a photocopy of symbols, the original blueprint is unchanged.

Now imagine instead of a blueprint, you want a copy of a *folder* that contains blueprints. You just copy the folder's tab label (not the blueprints inside). Now when you modify a blueprint inside your copy's folder, you are modifying the same physical blueprint that the original folder also points to. One folder, two labels, same contents.

This is the difference between a shallow copy and a deep copy in Python.

### Understanding the Four Ways to "Copy"

```python
import copy

original = [1, 2, 3, 4, 5]

# Option 1: Assignment -- NOT a copy, just another label for the same list
a = original           # a IS original (same object in memory)

# Option 2: Shallow copy -- new list object, but same inner elements
b = original.copy()    # new list, same element references
c = original[:]        # same as .copy()
d = list(original)     # same as .copy()

# Option 3: Deep copy -- new list AND new copies of all nested objects
e = copy.deepcopy(original)
```

### The Bug: Flat Lists (Works Fine)

```python
original = [1, 2, 3]
shallow = original.copy()

shallow[0] = 99   # modifying shallow
print(original)   # [1, 2, 3] -- original is unchanged. Flat lists are fine.
print(shallow)    # [99, 2, 3]
```

For flat (non-nested) lists, `.copy()` behaves like a true independent copy. Integers are immutable, so reassigning `shallow[0]` does not affect `original`.

### The REAL Bug: Nested Lists (2D Grids)

```python
# WRONG: Creating what looks like a copy of a 2D grid
grid = [[0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]]

grid_copy = grid.copy()   # BUG: shallow copy!

# Now let's place a piece on the copy
grid_copy[1][1] = 9   # placing '9' at center

print("Original grid:")
for row in grid:
    print(row)

print("\nCopy grid:")
for row in grid_copy:
    print(row)
```

Output:

```
Original grid:
[0, 0, 0]
[0, 9, 0]    <-- CORRUPTED! We only modified the copy!
[0, 0, 0]

Copy grid:
[0, 0, 0]
[0, 9, 0]
[0, 0, 0]
```

### Visual Trace: Why Shallow Copy Fails for Nested Lists

```
After grid.copy():

  grid ---------> [ ref0, ref1, ref2 ]
                     |     |     |
  grid_copy ------> [ ref0, ref1, ref2 ]
                     |     |     |
                   [0,0,0] [0,0,0] [0,0,0]
                     ^       ^       ^
                  SAME inner list objects!

When we do grid_copy[1][1] = 9:
  We follow ref1 in grid_copy -> same inner list as ref1 in grid
  We modify that inner list in place.
  Both grid and grid_copy point to the same inner list!

After modification:
  grid ---------> [ ref0, ref1, ref2 ]
                     |     |     |
  grid_copy ------> [ ref0, ref1, ref2 ]
                     |     |     |
                   [0,0,0] [0,9,0] [0,0,0]
                     ^  same  ^     ^
```

### The RIGHT Code: Deep Copy

```python
import copy

# RIGHT: Deep copy for nested lists
grid = [[0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]]

grid_copy = copy.deepcopy(grid)   # creates entirely new inner lists

grid_copy[1][1] = 9

print("Original grid:")
for row in grid:
    print(row)
# [0, 0, 0]
# [0, 0, 0]   <-- unchanged!
# [0, 0, 0]

print("\nCopy grid:")
for row in grid_copy:
    print(row)
# [0, 0, 0]
# [0, 9, 0]
# [0, 0, 0]
```

### Alternative for 2D Grids: List Comprehension

```python
# RIGHT: Manual deep copy using list comprehension (faster than deepcopy for 2D)
grid = [[0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]]

grid_copy = [row[:] for row in grid]   # copies each inner list individually

grid_copy[1][1] = 9
print(grid[1])       # [0, 0, 0]  -- unchanged!
print(grid_copy[1])  # [0, 9, 0]  -- modified only in copy
```

### Summary Table

```
Method                  | Creates new outer list? | Creates new inner lists? | Use when
------------------------|-------------------------|--------------------------|----------
b = a                   | No (same object)        | No                       | Never for copying
b = a.copy()            | Yes                     | No                       | Flat lists only
b = a[:]                | Yes                     | No                       | Flat lists only
b = list(a)             | Yes                     | No                       | Flat lists only
b = [r[:] for r in a]   | Yes                     | Yes (1 level deep)       | 2D grids
b = copy.deepcopy(a)    | Yes                     | Yes (all levels)         | Deeply nested
```

### Mini Test Case

```python
import copy

# Test: prove shallow copy fails on nested lists
a = [[1, 2], [3, 4]]
b = a.copy()          # shallow
c = copy.deepcopy(a)  # deep

b[0][0] = 99
c[1][1] = 88

print(a)  # [[99, 2], [3, 4]]  -- b's change leaked into a!
print(b)  # [[99, 2], [3, 4]]
print(c)  # [[1, 2], [3, 88]]  -- wait, a is [99,2],[3,4], c is separate
# a was modified via b's shallow reference!
```

---

## 4. List Multiplication Trap

### The Story: The Xerox Machine That Copies by Reference

You need three identical shopping lists. You write one on a piece of paper and photocopy it three times. But this is a magical photocopier: the copies are not independent sheets of paper. They are all windows onto the same underlying whiteboard. When you write "milk" on one copy, all three show "milk."

`[[0]*3]*3` creates three windows (references) onto the same inner list.

### The WRONG Code

```python
# WRONG: Creating a 3x3 grid of zeros
grid = [[0] * 3] * 3

print(grid)
# [[0, 0, 0], [0, 0, 0], [0, 0, 0]]  -- looks fine so far!

# Now let's place a value
grid[0][0] = 9

print(grid)
# [[9, 0, 0], [9, 0, 0], [9, 0, 0]]  -- ALL rows changed!
```

### Visual Trace: The Reference Problem

```
grid = [[0] * 3] * 3

Step 1: [0] * 3 creates ONE inner list:
  inner_list = [0, 0, 0]   at memory address 0xABC

Step 2: [inner_list] * 3 creates outer list with 3 references to THE SAME inner list:
  grid[0] ---> 0xABC --> [0, 0, 0]
  grid[1] ---> 0xABC --> [0, 0, 0]
  grid[2] ---> 0xABC --> [0, 0, 0]

All three rows point to the SAME object in memory.

When we do grid[0][0] = 9:
  We follow grid[0] -> 0xABC -> modify position 0 -> [9, 0, 0]
  Now ALL references to 0xABC see [9, 0, 0].

grid[0] ---> 0xABC --> [9, 0, 0]
grid[1] ---> 0xABC --> [9, 0, 0]
grid[2] ---> 0xABC --> [9, 0, 0]
```

### The RIGHT Code: List Comprehension

```python
# RIGHT: List comprehension creates a NEW inner list each time
grid = [[0] * 3 for _ in range(3)]

print(grid)
# [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

grid[0][0] = 9

print(grid)
# [[9, 0, 0], [0, 0, 0], [0, 0, 0]]  -- only row 0 changed!
```

### Why the Comprehension Works

```
grid = [[0] * 3 for _ in range(3)]

Iteration 1: creates [0, 0, 0] at address 0xABC
Iteration 2: creates [0, 0, 0] at address 0xDEF  (NEW object)
Iteration 3: creates [0, 0, 0] at address 0x123  (NEW object)

grid[0] ---> 0xABC --> [0, 0, 0]
grid[1] ---> 0xDEF --> [0, 0, 0]
grid[2] ---> 0x123 --> [0, 0, 0]

Three SEPARATE lists! Modifying one does not affect the others.
```

### The Rule: Multiplication is Fine for Immutables

```python
# SAFE: multiplying a flat list of immutables
zeros = [0] * 5
print(zeros)  # [0, 0, 0, 0, 0]
zeros[2] = 9
print(zeros)  # [0, 0, 9, 0, 0]  -- works correctly

# This is fine because integers are immutable.
# zeros[2] = 9 doesn't modify the integer 0;
# it replaces the reference at index 2 with a reference to 9.
# The other indices still point to their own 0 references.
```

### Mini Test Case

```python
# Verify the trap
bad_grid = [[0] * 3] * 3
good_grid = [[0] * 3 for _ in range(3)]

bad_grid[1][2] = 7
good_grid[1][2] = 7

print("Bad grid:", bad_grid)
# [[0, 0, 7], [0, 0, 7], [0, 0, 7]]  -- all rows affected!

print("Good grid:", good_grid)
# [[0, 0, 0], [0, 0, 7], [0, 0, 0]]  -- only row 1 affected
```

---

## 5. pop(0) is O(n) Not O(1)

### The Story: The Queue at the Post Office

Imagine a queue of 1000 people. The counter calls the person at the front. After they leave, ALL 999 remaining people must physically take one step forward to fill the gap. This happens every single time someone is served. If you serve 1000 people, you have made 1000 + 999 + 998 + ... + 1 = ~500,000 movements. That is O(n²) total work.

This is exactly what `list.pop(0)` does in Python. Lists are backed by a contiguous array. Removing the first element requires shifting every other element one position to the left.

### The WRONG Code (For Performance-Sensitive Code)

```python
# WRONG (for queues): Using a list as a queue
import time

# Simulate a large queue
queue = list(range(100_000))

start = time.time()
while queue:
    queue.pop(0)   # O(n) each time -- total is O(n²)!
end = time.time()

print(f"list.pop(0): {end - start:.3f} seconds")
```

### Visual Trace: Why pop(0) is O(n)

```
Before pop(0):
Index:  [0]  [1]  [2]  [3]  [4]
Value:  [10] [20] [30] [40] [50]
Memory: [  consecutive memory addresses  ]

pop(0) removes index 0 (value 10), then shifts everything:
  [20] moves from index 1 to index 0
  [30] moves from index 2 to index 1
  [40] moves from index 3 to index 2
  [50] moves from index 4 to index 3

After pop(0):
Index:  [0]  [1]  [2]  [3]
Value:  [20] [30] [40] [50]

For a list of n elements, pop(0) does n-1 shift operations.
For n pop(0) calls: (n-1) + (n-2) + ... + 1 + 0 = n*(n-1)/2 = O(n²)
```

### The RIGHT Code: Use collections.deque

```python
# RIGHT: Use deque for queue operations
import time
from collections import deque

# Comparison
n = 100_000

# List pop(0) -- O(n²)
lst = list(range(n))
start = time.time()
while lst:
    lst.pop(0)
list_time = time.time() - start

# Deque popleft() -- O(1) amortized
dq = deque(range(n))
start = time.time()
while dq:
    dq.popleft()   # O(1)!
deque_time = time.time() - start

print(f"list.pop(0):      {list_time:.3f}s")
print(f"deque.popleft():  {deque_time:.4f}s")
# list.pop(0):      ~2.5s
# deque.popleft():  ~0.01s  -- roughly 200x faster!
```

### How deque Achieves O(1) at Both Ends

```
deque uses a doubly-linked list of fixed-size blocks (not a contiguous array).

Removing from the left:
  [block] <-> [block] <-> [block]
   front

Just update the front pointer to the next element -- no shifting needed!

This is why deque is O(1) for both popleft() and appendleft().
```

### Practical Guide: When to Use What

```python
from collections import deque

# If you only pop from the right (stack behavior): use list
stack = []
stack.append(10)    # O(1)
stack.pop()         # O(1) -- pop from right is always O(1)

# If you pop from the left OR both ends (queue/deque behavior): use deque
queue = deque()
queue.append(10)    # O(1) -- add to right
queue.popleft()     # O(1) -- remove from left

# deque also supports:
queue.appendleft(5)  # O(1) -- add to left
queue.pop()          # O(1) -- remove from right

# deque can also have a maximum size (useful for sliding window)
recent = deque(maxlen=3)
for i in range(10):
    recent.append(i)
print(recent)  # deque([7, 8, 9], maxlen=3) -- auto-evicts old elements
```

### Mini Test Case

```python
from collections import deque

# Functional equivalence test
lst = [1, 2, 3, 4, 5]
dq = deque([1, 2, 3, 4, 5])

results_list = []
while lst:
    results_list.append(lst.pop(0))

results_deque = []
while dq:
    results_deque.append(dq.popleft())

print(results_list)   # [1, 2, 3, 4, 5]
print(results_deque)  # [1, 2, 3, 4, 5]
assert results_list == results_deque
print("Same results, very different performance!")
```

---

## 6. Confusing append vs extend vs +

### The Story: Packing a Suitcase

`append` is like stuffing a whole backpack into your suitcase. The suitcase now has one more item: a backpack. It is lumpy and nested.

`extend` is like unpacking the backpack and laying each item flat in the suitcase. The suitcase now has all the individual items, neatly arranged.

`+` is like buying a brand new suitcase, moving everything from both old suitcases in, and leaving the originals untouched.

### The WRONG Code

```python
# WRONG: Using append when you want to merge lists
fruits = ['apple', 'banana']
veggies = ['carrot', 'daikon']

# Mistake 1: append adds the entire list as a SINGLE element
fruits.append(veggies)
print(fruits)
# ['apple', 'banana', ['carrot', 'daikon']]  -- nested list, not what we wanted!

# Mistake 2: Using + thinking it modifies in place
fruits2 = ['apple', 'banana']
veggies2 = ['carrot', 'daikon']
fruits2 + veggies2   # This creates a new list but THROWS IT AWAY
print(fruits2)       # ['apple', 'banana']  -- unchanged!
```

### Detailed Behavior of Each Operation

```python
# append(x): adds x as a SINGLE ITEM to the end
lst = [1, 2, 3]
lst.append([4, 5])
print(lst)         # [1, 2, 3, [4, 5]]  -- [4,5] is ONE item at index 3
print(len(lst))    # 4

# append with a non-list
lst2 = [1, 2, 3]
lst2.append(99)
print(lst2)        # [1, 2, 3, 99]


# extend(iterable): unpacks the iterable and adds each element
lst3 = [1, 2, 3]
lst3.extend([4, 5])
print(lst3)        # [1, 2, 3, 4, 5]  -- 4 and 5 are separate items
print(len(lst3))   # 5

# extend works with any iterable
lst4 = [1, 2, 3]
lst4.extend("abc")   # strings are iterable!
print(lst4)          # [1, 2, 3, 'a', 'b', 'c']


# + operator: creates a NEW list, does NOT modify originals
a = [1, 2, 3]
b = [4, 5, 6]
c = a + b
print(a)  # [1, 2, 3]  -- unchanged
print(b)  # [4, 5, 6]  -- unchanged
print(c)  # [1, 2, 3, 4, 5, 6]  -- new list

# += modifies in place (for lists, it calls extend internally)
a += b
print(a)  # [1, 2, 3, 4, 5, 6]  -- modified!
```

### Mutation Behavior Summary

```
Operation        | Modifies original? | Adds as single item or unpacks?
-----------------|--------------------|--------------------------------
lst.append(x)    | Yes                | Single item (even if x is a list)
lst.extend(x)    | Yes                | Unpacks x (adds each element)
lst + other      | No (new list)      | Unpacks both into new list
lst += other     | Yes                | Unpacks (calls extend internally)
lst[len:] = x    | Yes                | Unpacks (slice assignment)
```

### The RIGHT Code for Each Use Case

```python
# Use case 1: Add a single item to the end
lst = [1, 2, 3]
lst.append(4)           # [1, 2, 3, 4]

# Use case 2: Add multiple items to the end
lst = [1, 2, 3]
lst.extend([4, 5, 6])   # [1, 2, 3, 4, 5, 6]

# Use case 3: Combine two lists into a NEW list (keep originals)
a = [1, 2, 3]
b = [4, 5, 6]
c = a + b               # new list, a and b unchanged

# Use case 4: Add a list AS an element (intentionally nested)
matrix = [[1, 2], [3, 4]]
new_row = [5, 6]
matrix.append(new_row)  # [[1, 2], [3, 4], [5, 6]] -- row appended correctly
```

### Mini Test Case

```python
# Demonstrate all three behaviors
base = [1, 2, 3]
add = [4, 5]

# Test append
a = base[:]
a.append(add)
print(f"append: {a}")       # [1, 2, 3, [4, 5]]  -- nested!
print(f"length: {len(a)}")  # 4

# Test extend
b = base[:]
b.extend(add)
print(f"extend: {b}")       # [1, 2, 3, 4, 5]    -- flat!
print(f"length: {len(b)}")  # 5

# Test +
c = base + add
print(f"+:      {c}")       # [1, 2, 3, 4, 5]    -- flat, new list!
print(f"base unchanged: {base}")  # [1, 2, 3]
```

---

## 7. Forgetting that sort() Returns None

### The Story: The Librarian Who Sorts In Place

You ask the librarian to sort the books. She does — she rearranges the books right there on the shelf. She does not hand you a sorted stack of books. She returns nothing (she hands you nothing). If you try to use what she handed you, you are holding air.

`list.sort()` sorts the list in place and returns `None`. `sorted()` (a built-in function) returns a new sorted list and does not modify the original.

### The WRONG Code

```python
# WRONG: Classic mistake -- assigning the return value of sort()
numbers = [3, 1, 4, 1, 5, 9, 2, 6]

sorted_numbers = numbers.sort()   # BUG: sort() returns None!

print(sorted_numbers)             # None  -- oops!

# The real disaster: using it immediately
if sorted_numbers[0] < 0:        # TypeError: 'NoneType' object is not subscriptable
    print("Has negatives")
```

### Visual Trace: What Actually Happens

```
numbers = [3, 1, 4, 1, 5, 9, 2, 6]

numbers.sort() is called:
  1. Python sorts the list IN PLACE: numbers is now [1, 1, 2, 3, 4, 5, 6, 9]
  2. sort() returns None (no return statement means implicit None)

sorted_numbers = None   <-- this is what gets assigned!
numbers = [1, 1, 2, 3, 4, 5, 6, 9]  <-- this is where the sorted data is!

sorted_numbers[0]  --> TypeError: 'NoneType' object is not subscriptable
```

### The RIGHT Approaches

```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6]

# RIGHT Option 1: Sort in place, use the original variable
numbers.sort()               # sorts numbers in place, returns None
print(numbers)               # [1, 1, 2, 3, 4, 5, 6, 9]  -- correct!
print(numbers[0])            # 1

# RIGHT Option 2: Use sorted() to get a new list
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
sorted_numbers = sorted(numbers)  # returns a NEW sorted list
print(sorted_numbers)             # [1, 1, 2, 3, 4, 5, 6, 9]
print(numbers)                    # [3, 1, 4, 1, 5, 9, 2, 6]  -- UNCHANGED
```

### When to Use Which

```python
# Use .sort() when:
# - You want to sort in place (mutate the original)
# - You do not need the original order
# - You want slightly better performance (no extra list allocation)

arr = [5, 2, 8, 1]
arr.sort()
# arr is now [1, 2, 5, 8]


# Use sorted() when:
# - You need to keep the original list unchanged
# - You want to sort a non-list iterable (tuple, generator, etc.)
# - You are chaining operations: sorted(...)[0], sorted(..., key=len), etc.

arr = [5, 2, 8, 1]
top_two = sorted(arr, reverse=True)[:2]
# arr is still [5, 2, 8, 1], top_two is [8, 5]

# sorted() works on any iterable
print(sorted("banana"))  # ['a', 'a', 'a', 'b', 'n', 'n']
print(sorted((3, 1, 2))) # [1, 2, 3]  -- tuple in, list out
```

### Related Bug: Chaining sort()

```python
# WRONG: Chaining on sort() result
numbers = [3, 1, 4, 1, 5]
result = numbers.sort()[:3]   # TypeError: 'NoneType' is not subscriptable

# RIGHT: Chain on sorted() result
result = sorted(numbers)[:3]
print(result)  # [1, 1, 3]
```

### Mini Test Case

```python
def get_top_3(nums):
    # WRONG version:
    # sorted_nums = nums.sort()
    # return sorted_nums[-3:]  # TypeError!

    # RIGHT version:
    return sorted(nums)[-3:]

print(get_top_3([5, 1, 8, 3, 9, 2]))  # [5, 8, 9]
```

---

## 8. Two-Pointer Without Pre-Sorting

### The Story: The Bouncer at the Two Doors

Imagine two people, one at each end of a sorted line, walking toward each other. Each person sees "my partner is too far left" and nudges in. This works perfectly because the line is sorted — everyone knows which direction to move.

Now imagine the same two people at each end of a *random, shuffled* line. The person on the left has no idea if nudging right will bring them closer to their target sum. They are wandering randomly. The algorithm breaks completely.

### The Classic Two-Sum Problem

```python
# Two-pointer approach: Find two numbers that sum to target
# REQUIREMENT: Array must be sorted!

# WRONG: Applying two-pointer to unsorted array
def two_sum_wrong(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        current_sum = arr[left] + arr[right]
        if current_sum == target:
            return (arr[left], arr[right])
        elif current_sum < target:
            left += 1
        else:
            right -= 1
    return None

# Test with unsorted array
arr = [8, 1, 6, 3, 7, 2]  # unsorted!
target = 9

result = two_sum_wrong(arr, target)
print(result)   # None -- misses the pair (8,1)? Let's trace...
```

### Visual Trace: Wrong Answer on Unsorted Array

```
arr = [8, 1, 6, 3, 7, 2], target = 9
Valid pairs: (8+1=9), (6+3=9), (7+2=9) -- three valid pairs!

L=0, R=5: arr[0]+arr[5] = 8+2 = 10 > 9, move R left
L=0, R=4: arr[0]+arr[4] = 8+7 = 15 > 9, move R left
L=0, R=3: arr[0]+arr[3] = 8+3 = 11 > 9, move R left
L=0, R=2: arr[0]+arr[2] = 8+6 = 14 > 9, move R left
L=0, R=1: arr[0]+arr[1] = 8+1 = 9  == target! Found (8,1)

OK this particular case got lucky. Let's try arr = [3, 7, 2, 6]:
target = 9, valid pairs: (3+6=9), (7+2=9)

L=0, R=3: arr[0]+arr[3] = 3+6 = 9 == target! Found (3,6)

Hmm, sometimes it works. The danger is when it DOESN'T:
arr = [4, 5, 3, 6], target = 9, valid pairs: (4+5=9), (3+6=9)

L=0, R=3: 4+6=10 > 9, move R left
L=0, R=2: 4+3=7  < 9, move L right
L=1, R=2: 5+3=8  < 9, move L right
L=2, R=2: left not < right, loop ends.

Returned None! But (4+5=9) and (3+6=9) both exist!
The unsorted array caused us to miss valid pairs.
```

### The RIGHT Code: Sort First

```python
# RIGHT: Sort first, then apply two-pointer
def two_sum_sorted(arr, target):
    arr_sorted = sorted(arr)   # O(n log n) -- necessary!
    left, right = 0, len(arr_sorted) - 1

    while left < right:
        current_sum = arr_sorted[left] + arr_sorted[right]
        if current_sum == target:
            return (arr_sorted[left], arr_sorted[right])
        elif current_sum < target:
            left += 1    # sum too small, increase left (next larger element)
        else:
            right -= 1   # sum too big, decrease right (next smaller element)
    return None

# Test
arr = [4, 5, 3, 6]
print(two_sum_sorted(arr, 9))  # (3, 6) or (4, 5) -- correct!

# Sorted array: [3, 4, 5, 6]
# L=0(3), R=3(6): 3+6=9 -- found!
```

### Why Sorting Enables the Two-Pointer Logic

```
Sorted array: [3, 4, 5, 6]
                ^         ^
               left     right

If arr[left] + arr[right] < target:
  We need a LARGER sum.
  Moving right left would only make it smaller.
  So we MUST move left right (to a larger value).

If arr[left] + arr[right] > target:
  We need a SMALLER sum.
  Moving left right would only make it larger.
  So we MUST move right left (to a smaller value).

This logic is ONLY valid when the array is sorted.
In an unsorted array, "moving right" doesn't mean "getting larger."
```

### Mini Test Case

```python
test_cases = [
    ([4, 5, 3, 6], 9),
    ([1, 2, 3, 4, 5], 7),
    ([10, 1, 8, 3], 11),
]

for arr, target in test_cases:
    result = two_sum_sorted(arr[:], target)
    print(f"arr={arr}, target={target} -> {result}")

# arr=[4, 5, 3, 6], target=9   -> (3, 6)
# arr=[1, 2, 3, 4, 5], target=7 -> (2, 5) or (3, 4)
# arr=[10, 1, 8, 3], target=11  -> (1, 10) or (3, 8)
```

---

## 9. Prefix Sum Off-by-One

### The Story: The Bank Balance Convention

Imagine two accountants at a bank. Accountant A says "balance[i] means the total deposits up to AND INCLUDING day i." Accountant B says "balance[i] means the total deposits BEFORE day i (not including day i)." Both conventions work, but if Accountant A passes their array to Accountant B's function, every answer is off by one transaction.

The prefix sum array has exactly this ambiguity. Pick a convention and stick to it.

### The Two Conventions

```python
arr = [3, 1, 4, 1, 5, 9, 2, 6]
#      0  1  2  3  4  5  6  7

# Convention 1: prefix[i] = sum of arr[0..i] inclusive (length n)
# prefix[0] = arr[0] = 3
# prefix[1] = arr[0] + arr[1] = 4
# prefix[i] = prefix[i-1] + arr[i]

prefix_inclusive = [0] * len(arr)
prefix_inclusive[0] = arr[0]
for i in range(1, len(arr)):
    prefix_inclusive[i] = prefix_inclusive[i-1] + arr[i]

# prefix_inclusive = [3, 4, 8, 9, 14, 23, 25, 31]


# Convention 2: prefix[i] = sum of arr[0..i-1] (length n+1, starts with 0)
# prefix[0] = 0 (empty sum)
# prefix[1] = arr[0] = 3
# prefix[i] = prefix[i-1] + arr[i-1]

prefix_exclusive = [0] * (len(arr) + 1)
for i in range(1, len(arr) + 1):
    prefix_exclusive[i] = prefix_exclusive[i-1] + arr[i-1]

# prefix_exclusive = [0, 3, 4, 8, 9, 14, 23, 25, 31]
```

### The WRONG Code: Mixing Conventions

```python
arr = [3, 1, 4, 1, 5, 9, 2, 6]

# Build with Convention 2 (exclusive, 1-indexed)
prefix = [0] * (len(arr) + 1)
for i in range(1, len(arr) + 1):
    prefix[i] = prefix[i-1] + arr[i-1]

# prefix = [0, 3, 4, 8, 9, 14, 23, 25, 31]

# Query: sum of arr[2..5] inclusive
# WRONG: Using Convention 1 formula with Convention 2 array
l, r = 2, 5  # 0-indexed, inclusive

# Convention 1 formula: prefix[r] - prefix[l-1]  (but this is for inclusive prefix)
wrong_sum = prefix[r] - prefix[l-1]  # prefix[5] - prefix[1] = 14 - 3 = 11
# arr[2..5] = 4+1+5+9 = 19  -- WRONG answer!

# Convention 2 formula: prefix[r+1] - prefix[l]
right_sum = prefix[r+1] - prefix[l]  # prefix[6] - prefix[2] = 23 - 4 = 19
print(f"Wrong sum: {wrong_sum}")  # 11 -- incorrect!
print(f"Right sum: {right_sum}")  # 19 -- correct!
```

### Visual Trace: Why the Formula Matters

```
arr =          [3,  1,  4,  1,  5,  9,  2,  6]
index:          0   1   2   3   4   5   6   7

prefix (excl): [0,  3,  4,  8,  9, 14, 23, 25, 31]
index:          0   1   2   3   4   5   6   7   8

To find sum of arr[l..r] inclusive using prefix_excl:
  sum = prefix[r+1] - prefix[l]

For l=2, r=5:
  sum = prefix[6] - prefix[2]
      = 23         - 4
      = 19

Check: arr[2]+arr[3]+arr[4]+arr[5] = 4+1+5+9 = 19 ✓

Why prefix[r+1] - prefix[l]?
  prefix[r+1] = sum of arr[0..r]   (everything up to and including r)
  prefix[l]   = sum of arr[0..l-1] (everything before l)
  Difference  = arr[l] + arr[l+1] + ... + arr[r]  ✓
```

### The RIGHT Code: Pick One Convention and Be Consistent

```python
def build_prefix(arr):
    """Convention 2: prefix[i] = sum of arr[0..i-1]. Length = n+1."""
    n = len(arr)
    prefix = [0] * (n + 1)
    for i in range(1, n + 1):
        prefix[i] = prefix[i-1] + arr[i-1]
    return prefix

def range_sum(prefix, l, r):
    """Sum of arr[l..r] inclusive (0-indexed)."""
    return prefix[r+1] - prefix[l]

# Test
arr = [3, 1, 4, 1, 5, 9, 2, 6]
prefix = build_prefix(arr)

print(range_sum(prefix, 0, 7))  # 31 = sum of all
print(range_sum(prefix, 2, 5))  # 19 = 4+1+5+9
print(range_sum(prefix, 0, 0))  # 3  = just arr[0]
```

### Mini Test Case

```python
arr = [1, 2, 3, 4, 5]
prefix = build_prefix(arr)

# All subarrays
for l in range(len(arr)):
    for r in range(l, len(arr)):
        expected = sum(arr[l:r+1])
        got = range_sum(prefix, l, r)
        assert got == expected, f"[{l},{r}]: expected {expected}, got {got}"

print("All prefix sum range queries correct!")
```

---

## 10. Kadane's Algorithm State Reset

### The Story: The Gold Miner on a Streak

Imagine a gold miner walking through a series of rooms. Some rooms add gold to their bag, some take gold away. The miner's strategy: "I'll keep going as long as I have positive gold. If my total goes negative, I'll drop everything and start fresh."

The bug is: "drop everything and start fresh" — meaning they reset to zero. But what if ALL rooms have negative gold? Then the answer is not zero (you never enter a room), it is the LEAST negative room (you enter only the best single room). Resetting to zero violates the problem constraint that you must pick at least one element.

### The WRONG Code

```python
# WRONG: Classic Kadane's with reset to 0
def max_subarray_wrong(arr):
    max_sum = float('-inf')
    current_sum = 0

    for num in arr:
        current_sum += num
        max_sum = max(max_sum, current_sum)
        if current_sum < 0:
            current_sum = 0   # BUG: reset to 0 fails for all-negative arrays!

    return max_sum

# All-negative test case:
arr = [-5, -3, -8, -1, -9]
print(max_subarray_wrong(arr))  # 0  -- WRONG! The subarray must have >= 1 element.
                                 # Correct answer: -1 (just the element -1)
```

### Visual Trace: The Reset Bug

```
arr = [-5, -3, -8, -1, -9]
max_sum = -inf, current_sum = 0

Step 1: num=-5
  current_sum = 0 + (-5) = -5
  max_sum = max(-inf, -5) = -5
  current_sum < 0 -> reset to 0

Step 2: num=-3
  current_sum = 0 + (-3) = -3
  max_sum = max(-5, -3) = -3
  current_sum < 0 -> reset to 0

Step 3: num=-8
  current_sum = 0 + (-8) = -8
  max_sum = max(-3, -8) = -3
  current_sum < 0 -> reset to 0

Step 4: num=-1
  current_sum = 0 + (-1) = -1
  max_sum = max(-3, -1) = -1   <-- correctly identified -1 as best so far
  current_sum < 0 -> reset to 0

Step 5: num=-9
  current_sum = 0 + (-9) = -9
  max_sum = max(-1, -9) = -1
  current_sum < 0 -> reset to 0

Final max_sum = -1  <-- wait, this is actually correct here!

But watch this: if we check max_sum AFTER the reset:
```

Actually the more subtle bug is when the reset changes the answer for mixed arrays. Let me show the real version of the bug:

```python
# The ACTUAL problematic pattern: the wrong version that returns 0
def max_subarray_wrong_v2(arr):
    max_sum = 0           # BUG: initializing to 0 instead of arr[0]
    current_sum = 0

    for num in arr:
        current_sum = max(0, current_sum + num)  # BUG: flooring at 0
        max_sum = max(max_sum, current_sum)

    return max_sum

arr = [-5, -3, -8, -1, -9]
print(max_subarray_wrong_v2(arr))  # 0  -- WRONG! Returns 0 which means "empty subarray"
```

### The RIGHT Code: Two Correct Approaches

**Approach A: The cleaner "max of two choices" formulation**

```python
# RIGHT: Correct Kadane's -- choice at each step
def max_subarray_right(arr):
    """
    At each position, we have two choices:
    1. Start a new subarray here (just take arr[i])
    2. Extend the previous subarray (current_sum + arr[i])
    We pick whichever is larger.
    """
    if not arr:
        return 0

    current_sum = arr[0]
    max_sum = arr[0]    # Initialize to arr[0], not 0!

    for num in arr[1:]:
        # Either start fresh here, or extend the running sum
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)

    return max_sum
```

**Approach B: Reset-based with correct initialization**

```python
# RIGHT: Reset-based Kadane's with proper initialization
def max_subarray_reset(arr):
    if not arr:
        return 0

    max_sum = arr[0]      # Must start with arr[0], not -infinity or 0
    current_sum = arr[0]

    for num in arr[1:]:
        if current_sum < 0:
            current_sum = num   # Start fresh from current element, NOT 0!
        else:
            current_sum += num
        max_sum = max(max_sum, current_sum)

    return max_sum
```

### Visual Trace: Correct Algorithm on All-Negative Array

```
arr = [-5, -3, -8, -1, -9]
current_sum = -5, max_sum = -5

Step 1: num=-3
  current_sum + num = -5 + (-3) = -8
  max(num, current_sum+num) = max(-3, -8) = -3
  current_sum = -3
  max_sum = max(-5, -3) = -3

Step 2: num=-8
  current_sum + num = -3 + (-8) = -11
  max(num, current_sum+num) = max(-8, -11) = -8
  current_sum = -8
  max_sum = max(-3, -8) = -3

Step 3: num=-1
  current_sum + num = -8 + (-1) = -9
  max(num, current_sum+num) = max(-1, -9) = -1
  current_sum = -1
  max_sum = max(-3, -1) = -1   <-- best single element found!

Step 4: num=-9
  current_sum + num = -1 + (-9) = -10
  max(num, current_sum+num) = max(-9, -10) = -9
  current_sum = -9
  max_sum = max(-1, -9) = -1

Final max_sum = -1  -- correct! The subarray [-1] is the maximum.
```

### Mini Test Case

```python
test_cases = [
    ([-5, -3, -8, -1, -9], -1),          # all negative: best single element
    ([-2, 1, -3, 4, -1, 2, 1, -5, 4], 6), # mixed: [4,-1,2,1]
    ([1], 1),                              # single element
    ([1, 2, 3, 4, 5], 15),               # all positive: entire array
    ([-1, -2, -3], -1),                  # all negative: least negative
]

for arr, expected in test_cases:
    result = max_subarray_right(arr[:])
    status = "PASS" if result == expected else "FAIL"
    print(f"{status}: arr={arr} -> got {result}, expected {expected}")

# PASS: arr=[-5, -3, -8, -1, -9] -> got -1, expected -1
# PASS: arr=[-2, 1, -3, 4, -1, 2, 1, -5, 4] -> got 6, expected 6
# PASS: arr=[1] -> got 1, expected 1
# PASS: arr=[1, 2, 3, 4, 5] -> got 15, expected 15
# PASS: arr=[-1, -2, -3] -> got -1, expected -1
```

---

## Quick Reference: All 10 Mistakes at a Glance

```
#  Mistake                          | Quick Fix
---|----------------------------------|-------------------------------------------
1  Modify list while iterating       | Iterate over copy: for x in lst[:]
2  Off-by-one in slicing             | arr[i:j+1] for inclusive j; arr[i:i+k] for k elements
3  Shallow copy of nested lists      | copy.deepcopy() or [row[:] for row in grid]
4  [[0]*3]*3 reference trap          | [[0]*3 for _ in range(3)]
5  pop(0) is O(n)                    | Use collections.deque and popleft()
6  append vs extend vs +             | append=single item, extend=unpack, +=extend in-place
7  sort() returns None               | Use sorted() for return value; .sort() modifies in place
8  Two-pointer without sorting       | Sort first! Two-pointer only valid on sorted arrays
9  Prefix sum off-by-one             | Use 1-indexed prefix of length n+1; query = prefix[r+1]-prefix[l]
10 Kadane's reset to 0               | Use max(num, current_sum + num); initialize to arr[0]
```

---

## Final Checklist Before Submitting Array Code

```
[ ] Did I check if modifying the list inside a loop?
[ ] Does my slice end at the right index (exclusive end)?
[ ] Did I deep copy nested lists when needed?
[ ] Did I use list comprehension instead of [[val]*n]*n for 2D?
[ ] Did I use deque instead of list for queue operations?
[ ] Do I know the difference between append and extend?
[ ] Did I use sorted() if I need the return value of sorting?
[ ] Did I sort the array before applying two-pointer?
[ ] Is my prefix sum convention consistent throughout?
[ ] Does my Kadane's handle all-negative arrays correctly?
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real World Usage](./real_world_usage.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
