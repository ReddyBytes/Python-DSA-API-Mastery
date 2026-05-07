# Closures — The Complete Guide

A closure is a function that remembers variables from the scope where it was created — even after that scope has finished executing.

---

## 📌 Learning Priority

**Must Learn:** what closures are · closure factory pattern · make_multiplier/make_counter · when closures form

**Should Learn:** late-binding trap · closure cells · shared state between closures · closures vs classes

**Good to Know:** `__closure__` attribute · cell objects · nonlocal in closures

**Reference:** dis module for bytecode inspection of closures

---

## Chapter 1: What Is a Closure?

Imagine a function that packs up the variables it needs before it leaves the room. When called later, it unpacks those variables — even though the original room is gone.

In Python, every function call creates a **stack frame** — a temporary block of memory holding local variables. When the function returns, the frame is destroyed. Normally, those variables disappear.

But if an inner function references a variable from the outer function, Python keeps that variable alive on the **heap** inside a **closure cell**. The inner function carries that cell with it forever.

```python
def outer():
    message = "hello"        # ← message lives in outer's stack frame

    def inner():
        print(message)       # ← inner references message (free variable)

    return inner             # ← inner is returned before outer's frame dies

greet = outer()              # outer's frame is gone — but message survives
greet()                      # prints: hello
```

### Memory: what actually happens

```
DURING outer() call:
┌─────────────────────────┐
│  outer() stack frame     │
│  message = "hello"  ←───┼─── inner() references this
│  inner (function obj)    │
└─────────────────────────┘

AFTER outer() returns:
┌─────────────────────────┐     ┌──────────────────────────┐
│  outer() frame: GONE     │     │  HEAP                     │
└─────────────────────────┘     │  closure cell: "hello"    │
                                 │      ↑                    │
                                 │  greet (function object)──┘
                                 │  greet.__closure__[0]     │
                                 └──────────────────────────┘
```

Three key terms:

- **Free variable**: a variable used inside a function but defined in an enclosing scope (not local, not global)
- **Closure cell**: the heap object Python uses to keep a free variable alive after its original scope ends
- **Captured variable**: the variable the closure "captured" from its enclosing scope

---

## Chapter 2: When Does a Closure Form?

Three conditions must ALL be true:

1. A function is defined inside another function (nested function)
2. The inner function references at least one variable from the enclosing scope
3. The inner function is returned or passed out of the enclosing scope

```python
# ALL 3 conditions met — closure forms
def outer(x):
    def inner():        # condition 1: nested
        return x        # condition 2: references enclosing variable x
    return inner        # condition 3: returned

f = outer(10)
print(f())              # 10
print(f.__closure__)    # (<cell at 0x...>,)  ← NOT None
```

```python
# Missing condition 2 — inner does not reference x
def outer(x):
    def inner():
        return 42       # does NOT reference x
    return inner

f = outer(10)
print(f.__closure__)    # None  ← no closure formed
```

```python
# Missing condition 3 — inner is never returned
def outer(x):
    def inner():
        return x
    inner()             # called here but NOT returned
    return None

result = outer(10)
print(result)           # None  ← inner is gone
```

### Inspecting with `__closure__`

```python
def make_greeting(name):
    def greet():
        return f"Hello, {name}"
    return greet

say_hi = make_greeting("Alice")
print(say_hi.__closure__)                    # (<cell at 0x...>,)
print(say_hi.__closure__[0].cell_contents)   # Alice
```

The `__closure__` attribute is either `None` (no closure) or a **tuple of cell objects**. Each cell holds one captured variable.

---

## Chapter 3: Closure Factory Pattern

A factory function manufactures specialized functions. Like a stamp factory that produces stamps with different messages — same mechanism, different output each time.

```python
# make_multiplier: produces a function that multiplies by factor
def make_multiplier(factor):
    def multiply(n):
        return n * factor    # ← factor is captured from make_multiplier's scope
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))   # 10
print(triple(5))   # 15
print(double(7))   # 14  — each closure has its own captured factor
```

Each call to `make_multiplier` creates a **fresh closure cell** for `factor`. `double` and `triple` are completely independent functions with different cells.

```python
# make_adder: produces a function that adds n
def make_adder(n):
    def add(x):
        return x + n         # ← n captured
    return add

add5 = make_adder(5)
add10 = make_adder(10)

print(add5(3))    # 8
print(add10(3))   # 13

# Composing adders
add15 = lambda x: add5(add10(x))
print(add15(0))   # 15
```

```python
# make_power: produces a function that raises to exp
def make_power(exp):
    def power(base):
        return base ** exp   # ← exp captured
    return power

square = make_power(2)
cube = make_power(3)

print(square(4))  # 16
print(cube(3))    # 27
```

### Real-world example: input validator

```python
def make_validator(min_len, max_len):
    def validate(text):
        if len(text) < min_len:
            raise ValueError(f"Too short: min {min_len} chars")
        if len(text) > max_len:
            raise ValueError(f"Too long: max {max_len} chars")
        return True
    return validate

validate_username = make_validator(3, 20)
validate_bio = make_validator(10, 500)

validate_username("al")         # raises ValueError: Too short
validate_username("alice")      # True
validate_bio("Hi")              # raises ValueError: Too short
```

The factory pattern shines when you need multiple instances of similar behavior with different configurations — without duplicating logic.

---

## Chapter 4: Shared State Between Closures

Two closures can share the same variable — like two cashiers sharing the same till. Both can read from it and write to it, and the change is visible to both.

```python
def make_counter():
    count = 0                      # ← single variable, shared by all three functions

    def increment():
        nonlocal count             # ← must declare nonlocal to modify
        count += 1
        return count

    def decrement():
        nonlocal count
        count -= 1
        return count

    def reset():
        nonlocal count
        count = 0
        return count

    return increment, decrement, reset

inc, dec, rst = make_counter()

print(inc())    # 1
print(inc())    # 2
print(inc())    # 3
print(dec())    # 2   ← decrement saw the value that increment left behind
print(rst())    # 0   ← reset affects the same count
print(inc())    # 1   ← all three share the same cell
```

### What the shared cell looks like

```
make_counter() closure cells:
┌─────────────────────────────────────────┐
│  heap                                    │
│                                          │
│  cell: count = 2                         │
│    ↑           ↑           ↑            │
│  increment   decrement   reset           │
│  (all three point to the same cell)      │
└─────────────────────────────────────────┘
```

**Warning:** they ALL modify the same variable. If `increment` is called 10 times before `decrement`, `decrement` starts from 10, not 0. This is intentional in a counter, but can be a surprise in other patterns.

---

## Chapter 5: The Late-Binding Trap

The closure does not capture the VALUE of the variable — it captures a REFERENCE to the variable. So if the variable changes after the closure is created, the closure sees the new value.

### The classic loop bug

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])    # [2, 2, 2]  — all print 2!
```

You might expect `[0, 1, 2]`. Here is why you get `[2, 2, 2]`:

All three lambdas reference the same variable `i` in the list comprehension's scope. By the time any lambda is called, the loop has finished and `i` is `2`. All three lambdas look up the current value of `i` — which is `2`.

### Cell reference vs value capture

```
WHAT YOU THINK HAPPENS:
  lambda 0 → cell holding 0
  lambda 1 → cell holding 1
  lambda 2 → cell holding 2

WHAT ACTUALLY HAPPENS:
  lambda 0 ─┐
  lambda 1 ─┼─→ same cell → i = 2  (after loop ends)
  lambda 2 ─┘
```

### Fix 1: default argument captures value at definition time

```python
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])    # [0, 1, 2]
```

Default argument values are evaluated when the function is defined, not when it is called. `lambda i=i: i` creates a new default `i` each iteration, capturing the current value.

### Fix 2: wrapping function creates a fresh scope

```python
def make_f(i):
    return lambda: i           # ← i is now a local variable in make_f's scope

funcs = [make_f(i) for i in range(3)]
print([f() for f in funcs])    # [0, 1, 2]
```

Each call to `make_f(i)` creates a completely new scope with its own `i`. The lambda in each call captures a different cell.

---

## Chapter 6: Closures vs Classes

Both closures and classes can hold state and expose behavior. The question is which tool fits the job.

| Situation | Closure | Class |
|---|---|---|
| Single behavior with private state | preferred | overkill |
| Multiple related methods | awkward | preferred |
| Need `__repr__` or `__str__` | not possible | natural |
| Inheritance needed | not possible | natural |
| Serialization / pickling | difficult | easier |
| Testing individual methods | harder | straightforward |
| Quick one-off stateful function | perfect | verbose |

**Rule of thumb:** use a closure when you need one callable with hidden state. Use a class when you need multiple methods, or when the object needs to be inspected, serialized, or subclassed.

```python
# Closure version — clean for a single behavior
def make_counter():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter

# Class version — better when you need reset(), value(), __repr__
class Counter:
    def __init__(self):
        self.count = 0
    def increment(self):
        self.count += 1
        return self.count
    def reset(self):
        self.count = 0
    def __repr__(self):
        return f"Counter({self.count})"
```

---

## Chapter 7: Common Mistakes

### Mistake 1: forgetting `nonlocal` when modifying an enclosing variable

```python
def make_counter():
    count = 0
    def increment():
        count += 1      # UnboundLocalError: local variable 'count' referenced before assignment
        return count
    return increment
```

Python sees `count +=` and treats `count` as a local variable in `increment`. But it has no local value yet. Fix: add `nonlocal count` before the assignment.

### Mistake 2: the late-binding trap in loops

Already covered in Chapter 5. Always use default arguments or a wrapping function when creating closures in a loop.

### Mistake 3: mutating a mutable captured object

```python
def make_accumulator():
    items = []
    def add(x):
        items.append(x)    # ← modifying the list, not reassigning the variable
        return items       # ← caller gets a reference to the SAME list
    return add

acc = make_accumulator()
result = acc(1)
acc(2)
print(result)    # [1, 2] — result and the internal list are the same object
```

If the caller stores the returned list and the closure keeps appending, the caller's reference shows every update. Return a copy if you want isolation: `return list(items)`.

### Mistake 4: returning the cell, not the value

```python
def make_value():
    x = 10
    def get():
        return x         # correct — returns the value
    def get_cell():
        return x.__class__  # example of inspecting rather than using
    return get

# The mistake is trying to access __closure__[0] directly and treating it as the value
f = make_value()
# f.__closure__[0] is a cell object, not 10
# f.__closure__[0].cell_contents is 10
```

Always call the closure to get the value. Do not try to extract it from `__closure__` directly in production code.

---

**[Back to Functions](../theory.md)** | **[Decorators →](./02_decorators_theory.md)**

**Related:** [Practice Problems](./practice.md) · [Functional Programming](../01_functional_programming/theory.md)
