# ⚡ Cheatsheet: Control Flow

## 🔀 Conditionals
```python
if condition:
    ...
elif condition2:
    ...
else:
    ...

# Ternary
x = "yes" if condition else "no"

# Match-Case (Python 3.10+)
match value:
    case pattern1: ...
    case pattern2 | pattern3: ...  # OR
    case (x, y): ...               # Destructure
    case _ : ...                   # Default
```

## 🔁 for Loop
```python
for item in iterable: ...
for i in range(5): ...          # 0,1,2,3,4
for i in range(1,6): ...        # 1,2,3,4,5
for i in range(0,10,2): ...     # 0,2,4,6,8
for i in range(10,0,-1): ...    # 10,9,...1

for i, val in enumerate(lst): ...          # index + value
for i, val in enumerate(lst, start=1): ... # start from 1
for a, b in zip(list1, list2): ...        # pair two lists
for k, v in dict.items(): ...            # dict iteration
```

## 🔄 while Loop
```python
while condition:
    ...

while True:          # infinite — use break to exit
    if exit_cond:
        break
```

## ⚡ Loop Controls
```python
break       # exit loop entirely
continue    # skip rest of current iteration
pass        # do nothing (placeholder)

# for/while...else
for item in lst:
    if found:
        break
else:
    # runs ONLY if loop never broke
    print("not found")
```

## 📦 Comprehensions
```python
# List
[expr for x in iterable]
[expr for x in iterable if condition]

# Dict
{k: v for k, v in items}

# Set
{expr for x in iterable}

# Generator (lazy)
(expr for x in iterable)
```

## 🔗 Logic / Short-Circuit
```python
# and: stops at first False, returns it (or last value)
True and True   → True
True and False  → False
False and True  → False   ← b never evaluated!

# or: stops at first True, returns it (or last value)
True or False   → True    ← b never evaluated!
False or True   → True
False or False  → False

# Practical
name = user and user.name      # None if user is None
val  = value or "default"      # "default" if value is falsy
safe = lst and lst[0]          # None if lst is empty
```

## 🎯 Useful Functions
```python
range(n)             # 0 to n-1
range(a, b)          # a to b-1
range(a, b, step)    # with step

enumerate(lst)       # (index, value) pairs
enumerate(lst, 1)    # starting index = 1
zip(a, b)            # pair iterables (stops at shortest)

sorted(lst)          # sorted copy
reversed(lst)        # reverse iterator
```

## ⚠️ Common Mistakes
```python
# 1. Modifying list while iterating → use copy
for item in lst[:]:        # or list(lst)

# 2. Off-by-one: range(10) is 0-9, not 1-10
for i in range(1, 11): ... # 1-10

# 3. Forgetting break in search → for/else handles it

# 4. Infinite while — always ensure exit condition changes

# 5. else on loop — only runs if NO break happened
```

## 📊 Loop Complexity
```
Single loop:   O(n)
Nested loops:  O(n²)
Binary search: O(log n)
```
