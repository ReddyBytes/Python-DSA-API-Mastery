# 🎯 Python Interview Master — Tricky Edge Cases  
The Hidden Traps That Break Interviews

---

# 🧠 Why Edge Cases Matter

Interviewers love edge cases because they test:

- Deep Python understanding
- Real debugging maturity
- Attention to detail
- Not just memorized knowledge

Most candidates fail here.

You won’t.

---

# 🔥 1️⃣ Mutable Default Argument Trap

### ❌ Problem

```python
def add_item(item, my_list=[]):
    my_list.append(item)
    return my_list
```

Calling:

```python
add_item(1)
add_item(2)
```

Output:
```
[1, 2]
```

Why?

Default arguments are evaluated only once.

---

### ✅ Correct Approach

```python
def add_item(item, my_list=None):
    if my_list is None:
        my_list = []
    my_list.append(item)
    return my_list
```

---

### 🎯 Interview Insight

Always mention:

> Default arguments are evaluated at function definition time, not at runtime.

---

# 🔥 2️⃣ Late Binding Closure Trap

### ❌ Problem

```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)

print([f() for f in funcs])
```

Output:
```
[2, 2, 2]
```

Why?

Lambda captures variable, not value.

---

### ✅ Fix

```python
funcs.append(lambda i=i: i)
```

---

### 🎯 Interview Insight

Closures capture variables by reference.

---

# 🔥 3️⃣ Identity vs Equality

### ❌ Example

```python
a = [1,2,3]
b = [1,2,3]

a == b  # True
a is b  # False
```

- `==` checks value
- `is` checks memory identity

---

### ⚠️ Special Case

```python
a = 256
b = 256
a is b  # True

a = 257
b = 257
a is b  # Might be False
```

Small integers are cached.

---

### 🎯 Interview Insight

Use `is` only for:

```python
if x is None:
```

---

# 🔥 4️⃣ Shallow vs Deep Copy Trap

### ❌ Problem

```python
import copy

original = [[1,2],[3,4]]
shallow = copy.copy(original)

shallow[0][0] = 99
print(original)
```

Original also modified.

---

### Why?

Shallow copy copies outer object only.

---

### ✅ Deep Copy

```python
deep = copy.deepcopy(original)
```

Now nested objects are copied.

---

# 🔥 5️⃣ Modifying List While Iterating

### ❌ Problem

```python
numbers = [1,2,3,4]

for num in numbers:
    if num % 2 == 0:
        numbers.remove(num)
```

Unpredictable behavior.

---

### ✅ Safe Approach

```python
numbers = [x for x in numbers if x % 2 != 0]
```

Or iterate over copy:

```python
for num in numbers[:]:
```

---

# 🔥 6️⃣ Floating Point Precision

### ❌ Problem

```python
0.1 + 0.2 == 0.3
```

Returns False.

Why?

Binary floating-point representation.

---

### ✅ Solution

```python
import math
math.isclose(0.1 + 0.2, 0.3)
```

Or use decimal module.

---

# 🔥 7️⃣ Mutable vs Immutable Types

Immutable:

- int
- float
- str
- tuple

Mutable:

- list
- dict
- set

---

### ❌ Confusing Example

```python
a = "hello"
a += " world"
```

Creates new string.

Strings are immutable.

---

# 🔥 8️⃣ Dict Ordering (Modern Python)

Before Python 3.7:

Dict order not guaranteed.

Python 3.7+:

Insertion order preserved.

Interview trick.

---

# 🔥 9️⃣ try-except-finally Behavior

```python
def test():
    try:
        return 1
    finally:
        return 2
```

Returns 2.

Finally overrides return.

Very common trap.

---

# 🔥 🔟 List Multiplication Trap

```python
matrix = [[0]*3]*3
matrix[0][0] = 1
print(matrix)
```

Output:
```
[[1,0,0],[1,0,0],[1,0,0]]
```

Why?

All rows reference same list.

---

### ✅ Correct Way

```python
matrix = [[0]*3 for _ in range(3)]
```

---

# 🔥 1️⃣1️⃣ None vs False Trap

```python
if value:
```

Fails for:

- 0
- ""
- []
- None

Better:

```python
if value is None:
```

Be explicit.

---

# 🔥 1️⃣2️⃣ Set vs List Performance

Membership check:

```python
x in list  # O(n)
x in set   # O(1)
```

Algorithmic understanding matters.

---

# 🔥 1️⃣3️⃣ Default Mutable Class Attributes

### ❌ Problem

```python
class A:
    items = []
```

Shared across instances.

---

### ✅ Correct Way

Initialize inside __init__.

---

# 🔥 1️⃣4️⃣ Iterator Exhaustion

```python
gen = (x for x in range(3))

list(gen)
list(gen)  # Empty
```

Generators are one-time use.

---

# 🔥 1️⃣5️⃣ Global vs Local Scope

```python
x = 10

def func():
    x += 1
```

Error: UnboundLocalError

Must declare:

```python
global x
```

Scope awareness matters.

---

# 🧠 How to Answer Edge Case Questions

When interviewer asks:

“What happens here?”

Do not panic.

Think:

- Mutability?
- Scope?
- Reference?
- Evaluation timing?
- Object identity?
- Shallow vs deep?
- Iterator exhaustion?

Structured thinking wins.

---

# ⚠️ Most Common Failure Points

- Mutable default arguments
- Shallow copy misunderstanding
- Modifying list during iteration
- Late binding closure
- List multiplication trap
- Identity vs equality confusion
- Floating point precision misunderstanding

Master these.
You eliminate 80% of Python traps.

---

# 🎯 Final Edge Case Checklist

- Default argument trap
- Closure late binding
- is vs ==
- Shallow vs deep copy
- Modifying during iteration
- Floating precision
- Dict ordering
- Generator exhaustion
- Class attribute sharing
- try-finally override

If you understand these deeply,
you are ahead of most candidates.

---

# 🏆 Final Interview Mindset

Edge cases test:

- Depth
- Calmness
- Real understanding
- Debugging maturity

When you:

- Explain clearly
- Mention why it happens
- Provide correct solution
- Mention real-world implication

You stand out immediately.

---

# 🔁 Navigation

Previous:  
[99_interview_master/scenario_based_questions.md](./scenario_based_questions.md)

Next:  
[README.md — Master Revision Strategy](../README.md)

