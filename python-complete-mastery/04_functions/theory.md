# 🧩 Functions — The Complete Mastery Guide

> *"A program without functions is like a city without streets —*
> *every building exists, but nothing connects. Nothing scales."*

---

## 🗺️ What You Will Master

```
┌─────────────────────────────────────────────────────────────────────────┐
│  BEGINNER         INTERMEDIATE          ADVANCED          EXPERT         │
│                                                                          │
│  • What is a     • Scope & LEGB        • Closures        • Decorators   │
│    function?     • *args/**kwargs       • Late binding    • Recursion    │
│  • Parameters    • Default trap ⚠️      • First-class     • Generators   │
│  • Return        • Lambda              • nonlocal        • Memoization  │
│  • Call stack    • Higher-order        • functools       • Type hints   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`def`, return values · `*args` / `**kwargs` · Default arguments · Lambda functions · Closures · LEGB rule · `functools.lru_cache`

**Should Learn** — Important for real projects, comes up regularly:
Positional-only `/` and keyword-only `*` params · `functools.partial` · `functools.wraps` · Recursion + `sys.setrecursionlimit()`

**Good to Know** — Useful in specific situations:
`functools.reduce` · `inspect.signature()` · Docstring formats (Google/NumPy/Sphinx)

**Reference** — Know it exists, look up when needed:
Tail recursion (Python doesn't optimize it) · `functools.singledispatch` (see decorators module)

---

# 📖 Chapter 1 — The Problem Functions Solve

## 🎬 The Story

Imagine you're building a banking app.
Every time a user makes a transaction, you need to:
1. Validate the amount
2. Check the balance
3. Log the transaction
4. Send a confirmation

Without functions, you copy-paste this logic everywhere.
For 50 transaction types, that's 50 × 4 = 200 blocks of logic.

Now the bank changes its logging format.
You have to find and update 50 places.
You miss one. A transaction goes unlogged.
Audit fails. Bank gets fined.

**That's the cost of code duplication.**

Functions solve this by giving a name to a block of logic —
write once, use everywhere, change once, fixes everywhere.

```
WITHOUT FUNCTIONS                  WITH FUNCTIONS
─────────────────                  ──────────────────────
validate amount (here)             def process_transaction():
check balance (here)                   validate_amount()
log transaction (here)                 check_balance()
send confirmation (here)               log_transaction()
                                       send_confirmation()
validate amount (there)
check balance (there)              process_transaction()   ← call once
log transaction (there)            process_transaction()   ← reuse
send confirmation (there)          process_transaction()   ← reuse
...50 more times...
```

---

# 📖 Chapter 2 — Anatomy of a Function

Every function has 5 possible parts.
Not all are required, but understanding each one deeply matters.

```
┌──────────────────────────────────────────────────────────────────────┐
│                    ANATOMY OF A FUNCTION                             │
│                                                                      │
│  def   send_email  ( to,  subject,  body="No content" )  :         │
│   │        │          │      │            │                         │
│   │        │          │      │         default value                │
│   │        │          │   parameter                                 │
│   │        │        parameter                                       │
│   │    function name                                                 │
│  keyword                                                             │
│                                                                      │
│      """Send an email to the given address."""    ← docstring        │
│      validated = validate(to)                     ← function body   │
│      return validated                             ← return value    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

```python
def send_email(to, subject, body="No content"):
    """Send an email to the given address."""   # docstring
    if not to:
        return False                            # early return
    print(f"Sending to {to}: {subject}")
    return True                                 # return value
```

---

# 📖 Chapter 3 — How Python Executes a Function

Understanding execution order is what separates beginners from professionals.
Let's trace every step.

## Step-by-Step Execution

```python
def add(a, b):
    result = a + b
    return result

total = add(10, 5)
print(total)
```

```
EXECUTION FLOW
─────────────────────────────────────────────────────────────
Step 1:  Python reads `def add(...):`
         → Stores the function OBJECT in memory
         → Nothing runs yet — just stored

Step 2:  Python hits `add(10, 5)`
         → Creates a NEW memory frame (stack frame)
         → Copies: a=10, b=5 into that frame
         → Jumps into the function body

Step 3:  Inside function:
         → result = 10 + 5 = 15
         → `return result` → sends 15 back

Step 4:  Stack frame for add() is DESTROYED
         → a, b, result are gone from memory

Step 5:  `total = 15` (the returned value)

Step 6:  print(15)
─────────────────────────────────────────────────────────────
```

## The Call Stack — Visual Model

```
CALL STACK (grows upward when functions are called)

Before add() is called:
┌──────────────────────────┐
│       main module        │  ← total = ?, print waiting
└──────────────────────────┘

During add(10, 5):
┌──────────────────────────┐
│   add()  a=10  b=5       │  ← executing now
│   result = 15            │
├──────────────────────────┤
│       main module        │  ← paused, waiting
└──────────────────────────┘

After add() returns:
┌──────────────────────────┐
│       main module        │  ← total=15, continues
└──────────────────────────┘
  (add()'s frame was destroyed)
```

> **Key insight:** Each function call gets its own isolated memory frame.
> Variables in `add()` cannot accidentally affect variables in `main`.
> This isolation is why functions are safe to reuse.

---

## What the Stack Frame Actually Contains

Each stack frame holds more than just your variables:

```
┌──────────────────────────────────────────────────────────────────┐
│                    stack frame for add(10, 5)                    │
│                                                                  │
│  local namespace:   { 'a': →10, 'b': →5, 'result': →15 }       │
│                           ↓    ↓          ↓                      │
│                       heap  heap        heap  (actual objects)   │
│                                                                  │
│  reference to global namespace  (so the frame can find globals) │
│  reference to code object       (bytecode of the function)      │
│  return address                 (where to go after return)      │
│  previous frame pointer         (link back to caller's frame)   │
└──────────────────────────────────────────────────────────────────┘
```

Key points:

- The frame stores **references**, not values.
- The actual objects (10, 5, 15) live on the **heap**.
- Multiple frames can reference the same heap object.
- When the frame is destroyed, only the name bindings disappear — heap objects survive until reference count hits zero.

```python
x = [1, 2, 3]      # list object created on heap

def show(items):
    print(items)    # 'items' in frame → same list on heap as 'x'
    items.append(4) # mutates the heap object — x also sees this!

show(x)
print(x)            # [1, 2, 3, 4] — heap object was mutated
```

---

# 📖 Chapter 4 — Parameters & Arguments — All 7 Types

This is the chapter most people partially understand.
By the end of this chapter, you'll know every type, every edge case.

## The Difference (Once and For All)

```
PARAMETER  = placeholder in function definition     def greet(name):   ← name is parameter
ARGUMENT   = actual value passed during call        greet("Alice")     ← "Alice" is argument
```

## Visual Map of All Parameter Types

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    7 PARAMETER TYPES IN PYTHON                           │
│                                                                          │
│  1. Positional        add(a, b)            order matters                 │
│  2. Keyword           add(b=5, a=10)       name matters, not order       │
│  3. Default           greet(name="Guest")  value if nothing passed       │
│  4. *args             def f(*args)         any number of positional      │
│  5. **kwargs          def f(**kwargs)      any number of keyword pairs   │
│  6. Keyword-only      def f(*, name)       MUST be passed by name        │
│  7. Positional-only   def f(x, /, y)       MUST be passed by position    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Type 1 — Positional Arguments

Order is everything. First argument → first parameter. Always.

```python
def describe(animal, action, place):
    print(f"The {animal} {action} in the {place}")

describe("cat", "sleeps", "garden")   # The cat sleeps in the garden
describe("sleeps", "cat", "garden")   # The sleeps cat in the garden ← wrong order!
```

---

## Type 2 — Keyword Arguments

Use the parameter name explicitly. Order no longer matters.

```python
describe(place="garden", animal="cat", action="sleeps")
# The cat sleeps in the garden  ← correct, even with different order!
```

> **Rule:** You can mix positional and keyword, but positional must come FIRST.
```python
describe("cat", place="garden", action="sleeps")   # ✓ valid
describe(animal="cat", "sleeps", "garden")          # ✗ SyntaxError — keyword before positional!
```

---

## Type 3 — Default Arguments

Give a parameter a value it uses when no argument is passed.

```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet("Alice")              # Hello, Alice!   ← greeting uses default
greet("Alice", "Hi")        # Hi, Alice!      ← default overridden
greet("Alice", greeting="Hey")  # Hey, Alice! ← keyword override
```

**The ordering rule for defaults:**
```
Parameters with defaults MUST come AFTER parameters without defaults.

def f(a, b, c=10):    ✓  non-defaults first, then defaults
def f(a=1, b, c=10):  ✗  SyntaxError — b (no default) after a (has default)
```

---

## ⚠️ Type 3 Edge Case — THE MUTABLE DEFAULT ARGUMENT TRAP

> This is the most famous Python gotcha. It has caused real production bugs.
> Learn this deeply. You will be asked about it.

```python


# What do you expect this to print?
def add_item(item, cart=[]):
    cart.append(item)
    return cart

print(add_item("apple"))    # Expected: ['apple']
print(add_item("banana"))   # Expected: ['banana']
print(add_item("cherry"))   # Expected: ['cherry']
```

> 📝 **Practice:** [Q10 · mutable-default-argument](../python_practice_questions_100.md#q10--critical--mutable-default-argument) · [Q49 · mutable-default-fix](../python_practice_questions_100.md#q49--thinking--mutable-default-fix)


**Actual output:**
```
['apple']
['apple', 'banana']
['apple', 'banana', 'cherry']
```

**Why?!**

```
DEFAULT VALUES ARE EVALUATED ONCE — WHEN THE FUNCTION IS DEFINED.
Not every time the function is called.

When Python reads `def add_item(item, cart=[]):`:
→ It creates ONE list object in memory: []
→ That same list object is reused on every call!

So all three calls share the SAME list.
```

```
Memory diagram:

def add_item(item, cart=[]):    ← Python creates this list ONCE: id=0x1234
                  └────────────────────────────────────────────────────┐
                                                                        │
Call 1: cart is still 0x1234 → append "apple" → ['apple']              │
Call 2: cart is still 0x1234 → append "banana" → ['apple','banana']    │
Call 3: cart is still 0x1234 → append "cherry" → ['apple','banana','cherry']
```

**The fix — always use None as default for mutable objects:**

```python
# ✅ Correct pattern:
def add_item(item, cart=None):
    if cart is None:
        cart = []          # new list created on EACH call
    cart.append(item)
    return cart

print(add_item("apple"))    # ['apple']
print(add_item("banana"))   # ['banana']   ← fresh list each time!
```

**This applies to ALL mutable defaults:**
```python
# ❌ These are all dangerous:
def f(x, result=[]):   ...   # list
def f(x, data={}):    ...    # dict
def f(x, seen=set()): ...    # set

# ✅ Always do this instead:
def f(x, result=None):
    if result is None: result = []
```

---

## Type 4 — *args (Variable Positional Arguments)

When you don't know how many positional arguments will be passed.

```python
def total(*numbers):
    print(type(numbers))    # <class 'tuple'>  ← always a tuple!
    return sum(numbers)

total(1, 2, 3)          # 6
total(10, 20)            # 30
total(5)                 # 5
total()                  # 0  ← zero args also works!
```

**Unpacking with `*` in a call:**
```python
nums = [1, 2, 3, 4, 5]
total(*nums)    # same as total(1, 2, 3, 4, 5)
```

---

## Type 5 — **kwargs (Variable Keyword Arguments)

When you don't know what key-value pairs will be passed.

```python
def create_profile(**info):
    print(type(info))    # <class 'dict'>  ← always a dict!
    for key, value in info.items():
        print(f"  {key}: {value}")

create_profile(name="Alice", age=25, city="Mumbai")


# name: Alice
# age: 25
# city: Mumbai
```

> 📝 **Practice:** [Q11 · args-kwargs](../python_practice_questions_100.md#q11--normal--args-kwargs)


**Unpacking a dict with `**` in a call:**
```python
data = {"name": "Alice", "age": 25}
create_profile(**data)    # same as create_profile(name="Alice", age=25)
```

---

## Type 6 — Keyword-Only Parameters (after `*`)

Force a parameter to ALWAYS be passed by name. Never by position.

```python
def connect(host, port, *, timeout, retries=3):
    #                    ↑
    #              bare * means: everything after this is keyword-only
    print(f"Connecting to {host}:{port}, timeout={timeout}")

connect("localhost", 8080, timeout=30)           # ✓
connect("localhost", 8080, timeout=30, retries=5) # ✓
connect("localhost", 8080, 30)                   # ✗ TypeError: timeout must be keyword
```

**Why is this useful?**
```
Without keyword-only:
connect("localhost", 8080, 30, 5)   ← What is 30? What is 5? Unclear!

With keyword-only:
connect("localhost", 8080, timeout=30, retries=5)  ← Crystal clear!
```

---

## Type 7 — Positional-Only Parameters (before `/`)

Force a parameter to ALWAYS be passed by position. Never by name.
(Added in Python 3.8)

```python
def power(base, exponent, /):
    #                    ↑
    #   / means: everything before this is positional-only
    return base ** exponent

power(2, 10)           # ✓  1024
power(base=2, exponent=10)   # ✗ TypeError: must be positional
```

**Real-world use:** The built-in `len()`, `abs()` etc. use positional-only.

---

## The Complete Parameter Order Rule

When combining all types, there is ONE valid ordering:

```
┌─────────────────────────────────────────────────────────────────────────┐
│               COMPLETE PARAMETER ORDERING                               │
│                                                                         │
│  def func( pos_only, /, normal, *args, kw_only, **kwargs ):            │
│              │        │    │       │              │                     │
│         positional  mixed  |   keyword-only     keyword                │
│           only      zone  any number            pairs                  │
│                          of positional                                  │
│                                                                         │
│  RULE: / before * before **                                             │
└─────────────────────────────────────────────────────────────────────────┘
```

```python
# Full example combining everything:
def full_example(pos_only, /, normal, default=10, *args, kw_only, **kwargs):
    print(f"pos_only={pos_only}")
    print(f"normal={normal}")
    print(f"default={default}")
    print(f"args={args}")
    print(f"kw_only={kw_only}")
    print(f"kwargs={kwargs}")

full_example(1, 2, 3, 4, 5, kw_only="must", extra="yes")
# pos_only=1
# normal=2
# default=3
# args=(4, 5)
# kw_only=must
# kwargs={'extra': 'yes'}
```

## Decision Flowchart — Which Parameter Type?

```
I'm designing a function parameter...

Is the number of values unknown?
├── Yes, positional → use *args
├── Yes, keyword pairs → use **kwargs
└── No → Is there a sensible default?
          ├── Yes → default parameter  def f(x=10)
          └── No → Is clarity essential?
                    ├── Must always use name → keyword-only  def f(*, x)
                    ├── Must always use position → positional-only  def f(x, /)
                    └── Flexible → regular parameter  def f(x)
```

---

# 📖 Chapter 5 — The Return Statement — All Behaviors

## Return Does Two Things

```
1. Sends a value back to the caller
2. Immediately exits the function
```

## All Return Scenarios

```python
# Scenario 1: Return a value
def add(a, b):
    return a + b

result = add(3, 4)    # result = 7

# Scenario 2: Return nothing (implicit None)

def greet(name):
    print(f"Hello, {name}")
    # no return statement

result = greet("Alice")    # prints "Hello, Alice"
print(result)               # None  ← function returns None!


# Scenario 3: Return early (guard clause)
def divide(a, b):
    if b == 0:
        return None       # early exit — avoids crash
    return a / b

# Scenario 4: Return multiple values (actually returns a tuple)
def min_max(numbers):
    return min(numbers), max(numbers)   # returns (min, max) tuple

low, high = min_max([3, 1, 4, 1, 5])   # tuple unpacking
print(low, high)    # 1  5

# Scenario 5: Return stops execution
def find_first(items, target):
    for i, item in enumerate(items):
        if item == target:
            return i         # ← exits immediately when found
    return -1                # ← only reached if not found
```

> 📝 **Practice:** [Q12 · return-none](../python_practice_questions_100.md#q12--thinking--return-none)


## ⚠️ The Return vs Print Confusion

```
PRINT                             RETURN
──────────────────────────────    ──────────────────────────────
Shows output in the console       Sends value back to caller
Used for debugging                Used in real applications
Caller gets None back             Caller gets the actual value
Cannot chain/reuse output         Can chain: result = f(g(x))
```

```python
# ❌ Print-based (broken in real usage):
def add_bad(a, b):
    print(a + b)            # prints but doesn't return

total = add_bad(3, 4)       # 7 appears in console
print(total * 2)            # TypeError! total is None, not 7!

# ✅ Return-based (correct):
def add_good(a, b):
    return a + b

total = add_good(3, 4)      # total = 7
print(total * 2)            # 14  ✓
```

---

# 📖 Chapter 6 — Scope — The LEGB Rule

> When Python encounters a variable name, it searches for it in this exact order.
> Miss one level and you'll be confused for years.

> 📝 **Practice:** [Q91 · predict-output-scope](../python_practice_questions_100.md#q91--logical--predict-output-scope)

## The LEGB Pyramid

```
┌──────────────────────────────────────────────────────────────┐
│                     LEGB SCOPE PYRAMID                       │
│                                                              │
│                    ┌─────────────┐                           │
│                    │   Built-in  │  outermost                │
│                    │  len, print │                           │
│                 ┌──┴─────────────┴──┐                       │
│                 │      Global       │                        │
│                 │  (module level)   │                        │
│              ┌──┴───────────────────┴──┐                    │
│              │      Enclosing         │                     │
│              │  (outer function)      │                     │
│           ┌──┴───────────────────────┴──┐                  │
│           │           Local             │  innermost       │
│           │    (current function)       │                  │
│           └─────────────────────────────┘                  │
│                                                              │
│     Python searches:  L → E → G → B                         │
│     (first match wins — search stops)                        │
└──────────────────────────────────────────────────────────────┘
```

## Live Example — Tracing Each Level

```python
x = "global"                          # G: global scope

def outer():
    x = "enclosing"                   # E: enclosing scope

    def inner():
        x = "local"                   # L: local scope
        print(x)                      # finds "local" first (L)

    def inner_no_local():
        print(x)                      # no local x → finds "enclosing" (E)

    inner()             # prints "local"
    inner_no_local()    # prints "enclosing"

outer()
print(x)                # prints "global" (G)
```

```
Scope search trace:
inner():          L→ found "local"    → stop
inner_no_local(): L→ not found
                  E→ found "enclosing" → stop
module level:     L→ not found
                  E→ not found
                  G→ found "global"   → stop
```

---

## The `global` Keyword

Without `global`, a function cannot MODIFY a global variable (it can READ it).

```python
count = 0           # global variable

def increment():
    count += 1      # ❌ UnboundLocalError!
                    # Python sees assignment → treats count as LOCAL
                    # But local count was never defined → error!

# WHY? When Python sees `count += 1` (which is `count = count + 1`)
# it classifies count as LOCAL (because there's an assignment).
# Then it tries to READ the local count before it's defined → error!
```

```python
count = 0

def increment():
    global count    # ← tell Python: use the GLOBAL count
    count += 1      # now it works

increment()
increment()
print(count)    # 2
```

**The professional opinion on `global`:**
```
Using `global` is usually a design smell.
If multiple functions need to share state, use a class or pass values explicitly.
In production code, overuse of `global` is a red flag in code reviews.
The ONE common exception: module-level configuration constants.
```

---

## The `nonlocal` Keyword

`global` is for global scope.
`nonlocal` is for enclosing (outer function) scope.

```python
def make_counter():
    count = 0                   # enclosing scope variable

    def increment():
        nonlocal count          # ← I want the ENCLOSING count
        count += 1
        return count

    def reset():
        nonlocal count
        count = 0

    return increment, reset

inc, rst = make_counter()
print(inc())    # 1
print(inc())    # 2
print(inc())    # 3
rst()
print(inc())    # 1  ← reset worked!
```

> 📝 **Practice:** [Q28 · nonlocal](../python_practice_questions_100.md#q28--normal--nonlocal)

## Scope Summary Table

```
┌──────────────────────────────────────────────────────────────┐
│  Variable  │  Where defined     │  Keyword needed to modify? │
├────────────┼────────────────────┼────────────────────────────┤
│  Local     │  Inside function   │  None (just assign)        │
│  Enclosing │  Outer function    │  nonlocal                  │
│  Global    │  Module level      │  global                    │
│  Built-in  │  Python internals  │  Cannot modify             │
└──────────────────────────────────────────────────────────────┘
```

---

## Memory Behavior by Scope

Scope isn't just about WHERE Python looks for names — it also determines WHERE the variables live in memory and HOW LONG they survive.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Scope      │  Memory Location         │  Lifetime                           │
├─────────────┼──────────────────────────┼─────────────────────────────────────┤
│  Local      │  Current stack frame     │  Dies when function returns.        │
│             │                          │  The fastest access.                │
├─────────────┼──────────────────────────┼─────────────────────────────────────┤
│  Enclosing  │  Heap — cell object      │  Survives after outer function      │
│             │  held by __closure__     │  returns, as long as inner          │
│             │                          │  function is alive.                 │
├─────────────┼──────────────────────────┼─────────────────────────────────────┤
│  Global     │  Module __dict__ (heap)  │  Lives for entire program run.      │
│             │                          │  Never auto-cleaned.                │
├─────────────┼──────────────────────────┼─────────────────────────────────────┤
│  Built-in   │  builtins module (heap)  │  Lives for entire interpreter       │
│             │                          │  session.                           │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Local scope — stack, fastest, auto-cleaned:**

```python
def process():
    result = compute()   # 'result' lives in THIS frame's local namespace
    return result
# After return: 'result' reference is gone, heap object collected if no other ref
```

**Global scope — heap, persists forever:**

```python
cache = {}   # module-level: lives in module.__dict__ on heap

def add_to_cache(key, value):
    cache[key] = value   # mutates the heap dict — persists across all calls
```

**Enclosing scope — heap cell, survives outer function:**

```python
def make_adder(n):
    # 'n' becomes a cell object on heap when inner function captures it
    def add(x):
        return x + n     # looks up n in __closure__ cell, not a stack frame
    return add

add5 = make_adder(5)
# make_adder() returned — its stack frame is GONE
# but 'n=5' still lives in a cell on the heap, referenced by add5.__closure__

```

> 📝 **Practice:** [Q26 · closures](../python_practice_questions_100.md#q26--thinking--closures)

---

# 📖 Chapter 7 — Functions Are Objects (First-Class Citizens)

This is the concept that unlocks all advanced Python.

> In Python, functions are objects — the same kind as integers, strings, and lists.
> This means functions can be stored, passed around, and returned like any other value.

## Functions Can Be Stored in Variables

```python
def greet(name):
    return f"Hello, {name}!"

# Storing the function (NOT calling it — no parentheses!):
say_hello = greet              # say_hello now points to the same function object

print(say_hello("Alice"))      # Hello, Alice!
print(greet is say_hello)      # True — same object!

# You can even store functions in a list:
operations = [str.upper, str.lower, str.title]
text = "hello world"
for op in operations:
    print(op(text))
# HELLO WORLD
# hello world
# Hello World
```

## ⚠️ `func` vs `func()` — The Confusion That Causes Silent Bugs

```python
def add(a, b):
    return a + b

x = add       # stores the FUNCTION OBJECT — nothing runs
y = add(3, 4) # CALLS the function — returns 7 and stores 7

print(type(x))  # <class 'function'>
print(type(y))  # <class 'int'>

# Classic mistake:
result = add    # forgot parentheses!
print(result)   # <function add at 0x...>   ← prints the function, not the result!
```

## Functions Can Be Passed as Arguments

```python
def apply_twice(func, value):
    return func(func(value))

def double(x):
    return x * 2

print(apply_twice(double, 3))    # double(double(3)) = double(6) = 12

# With lambdas (next chapter):
print(apply_twice(lambda x: x + 10, 5))    # (5+10)+10 = 25
```

## Functions Can Be Returned

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor      # uses 'factor' from outer scope
    return multiply            # returns the function, not the result!

double  = make_multiplier(2)
triple  = make_multiplier(3)
times10 = make_multiplier(10)

print(double(5))    # 10
print(triple(5))    # 15
print(times10(5))   # 50
```

---

# 📖 Chapter 8 — Lambda Functions

## What Is a Lambda?

A lambda is a small, anonymous (no-name) function written in one line.

```
NORMAL FUNCTION                    LAMBDA EQUIVALENT
──────────────────────────────     ──────────────────────────────
def square(x):                     square = lambda x: x ** 2
    return x ** 2
```

```
ANATOMY:
  lambda   x, y   :   x + y
    │      │            │
  keyword  params    expression (automatically returned)
```

## Where Lambdas Shine — Sorting

```python
students = [
    {"name": "Charlie", "gpa": 8.5},
    {"name": "Alice",   "gpa": 9.2},
    {"name": "Bob",     "gpa": 8.9},
]

# Sort by gpa:
sorted_students = sorted(students, key=lambda s: s["gpa"])
# Alice (9.2) is last — sorts ascending by default

# Sort by name:
sorted_students = sorted(students, key=lambda s: s["name"])

# Sort descending:
sorted_students = sorted(students, key=lambda s: s["gpa"], reverse=True)
```

## With `map()` and `filter()`

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# map() — apply function to every item:
squared = list(map(lambda x: x**2, numbers))
# [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

# filter() — keep items where function returns True:
evens = list(filter(lambda x: x % 2 == 0, numbers))
# [2, 4, 6, 8, 10]

# Combined:
even_squares = list(map(lambda x: x**2, filter(lambda x: x%2==0, numbers)))
# [4, 16, 36, 64, 100]

# Pythonic alternative using comprehensions (often preferred):
even_squares = [x**2 for x in numbers if x % 2 == 0]
```

## Lambda Limitations

```
Lambdas CANNOT:
  • Use statements (if/else/for/while as statements)
  • Have multiple expressions
  • Use return keyword
  • Have docstrings
  • Be complex

Lambdas CAN:
  • Use conditional expressions  lambda x: "even" if x%2==0 else "odd"
  • Call other functions          lambda x: len(x)
  • Access outer scope            lambda x: x + offset
```

**When NOT to use lambda:**
```python
# ❌ Too complex for a lambda — use def:
result = sorted(items, key=lambda x: (x.age, -x.score, x.name.lower()))

# ✅ Use def for clarity:
def sort_key(x):
    return (x.age, -x.score, x.name.lower())
result = sorted(items, key=sort_key)
```

---

# 📖 Chapter 9 — Closures — Functions That Remember

## The Setup

A closure happens when an inner function uses a variable from its outer function,
and the outer function returns the inner function.

The inner function "closes over" those outer variables — it carries them with it.

```python
def make_greeting(language):
    # language lives in outer (enclosing) scope

    def greet(name):
        # This function uses 'language' from outer scope
        if language == "english":
            return f"Hello, {name}!"
        elif language == "spanish":
            return f"¡Hola, {name}!"
        else:
            return f"Hi, {name}!"

    return greet    # return the FUNCTION, not its result

english_greet = make_greeting("english")
spanish_greet = make_greeting("spanish")

print(english_greet("Alice"))    # Hello, Alice!
print(spanish_greet("Alice"))    # ¡Hola, Alice!
```

## Closure Memory Model

```
MEMORY AFTER make_greeting("english") returns:

Heap Memory:
┌─────────────────────────────────────────────┐
│  Function object: greet                      │
│  ┌─────────────────────────────────────────┐ │
│  │  Code: if language == "english"...      │ │
│  │  __closure__: {language → "english"}    │ │
│  │              ↑                          │ │
│  │   carries this even after outer()       │ │
│  │   is completely gone from memory        │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘

english_greet points to this object.
language="english" is preserved INSIDE the function.
```

**Inspecting a closure:**
```python
def outer(x):
    def inner(y):
        return x + y
    return inner

add5 = outer(5)

print(add5.__closure__)                     # (<cell at 0x...>,)
print(add5.__closure__[0].cell_contents)    # 5  ← x is stored here!
```

## ⚠️ The Late Binding Closure Trap

> This is the #2 most famous Python gotcha. It appears in interviews constantly.

```python


# You want 5 functions that each print their loop number:
functions = []
for i in range(5):
    def f():
        print(i)
    functions.append(f)

functions[0]()    # Expected: 0   Got: 4
functions[1]()    # Expected: 1   Got: 4
functions[2]()    # Expected: 2   Got: 4
functions[3]()    # Expected: 3   Got: 4
functions[4]()    # Expected: 4   Got: 4  (only this is "correct")
```

> 📝 **Practice:** [Q27 · closure-loop-trap](../python_practice_questions_100.md#q27--critical--closure-loop-trap)


**Why?**
```
LATE BINDING: Closures bind to the VARIABLE, not the VALUE at the time of creation.

When functions[0]() is called:
→ Python looks up 'i' in the enclosing scope
→ By that time, the loop has finished
→ i is now 4 (its final value)
→ ALL functions see i=4

The functions don't remember i's VALUE when they were created.
They remember WHERE i lives in memory.
And they look up that location when called.
```

**The fix — capture the value using a default argument:**
```python
functions = []
for i in range(5):
    def f(captured_i=i):       # ← default argument evaluated NOW
        print(captured_i)
    functions.append(f)

functions[0]()    # 0  ✓
functions[1]()    # 1  ✓
functions[2]()    # 2  ✓
```

**The fix with lambda:**
```python
functions = [lambda x=i: x for i in range(5)]
functions[0]()    # 0  ✓
```

---

## Closure Cell Internals — How Captured Variables Actually Work

When an inner function captures a variable from its enclosing scope, Python doesn't copy the value. It creates a **cell object** on the heap that both functions share.

```
def outer(x):
    def inner(y):
        return x + y    # 'x' is captured — becomes a cell
    return inner

add5 = outer(5)
```

Memory after `outer(5)` returns:

```
Stack: outer() frame DESTROYED (x reference gone from stack)

Heap:
  ┌──────────────────────────────────────┐
  │  cell object                         │
  │    cell_contents: 5                  │  ← 'x=5' lives here
  └──────────────────────────────────────┘
         ↑
  ┌──────────────────────────────────────┐
  │  function object: inner              │
  │    __closure__: (cell_object,)       │  ← keeps cell alive
  └──────────────────────────────────────┘
         ↑
  add5 → points to this function object
```

Inspect the cell:

```python
print(add5.__closure__)                     # (<cell at 0x...>,)
print(add5.__closure__[0].cell_contents)    # 5
```

**Why cells cause late binding:**

The cell doesn't store the value at closure creation time — it stores a **reference**.
When `inner` runs and looks up `x`, it reads the cell's current value.

```python
# The classic late binding trap
functions = []
for i in range(3):
    def f():
        return i       # captures the CELL for 'i', not the current value
    functions.append(f)

print(functions[0]())  # 2 — reads cell at call time, loop is done, i=2
print(functions[1]())  # 2
print(functions[2]())  # 2
```

Fix: force value capture by using a default argument (evaluated at definition time, not call time):

```python
functions = [lambda i=i: i for i in range(3)]
print(functions[0]())  # 0  ✓
print(functions[1]())  # 1  ✓
```

**Multiple closures sharing one cell:**

```python
def make_counter():
    count = 0               # one cell for 'count'

    def increment():
        nonlocal count
        count += 1
        return count

    def reset():
        nonlocal count
        count = 0            # same cell — both functions modify the same object

    return increment, reset

inc, rst = make_counter()
inc()   # 1
inc()   # 2
rst()   # resets to 0
inc()   # 1  — shared cell, reset worked
```

---

# 📖 Chapter 10 — Decorators — Functions That Wrap Functions

## Building a Decorator From Scratch

Let's understand the problem first.

You have 5 functions and you want to time how long each takes.
Without decorators, you add timing code to every function — 5 places.
Tomorrow you want to also log. That's 10 places.

Decorators let you add behavior to a function without touching its code.

```python
# Step 1: The basic wrapper pattern
def add(a, b):
    return a + b

# Manually wrapping (without decorator syntax):
import time

def timed_add(a, b):
    start = time.time()
    result = add(a, b)
    end = time.time()
    print(f"add() took {end-start:.6f}s")
    return result

# This works but it's not reusable for OTHER functions.
```

```python
# Step 2: Make it work for ANY function
import time

def timer(func):                   # takes a function
    def wrapper(*args, **kwargs):  # matches ANY signature
        start = time.time()
        result = func(*args, **kwargs)  # calls the original
        end = time.time()
        print(f"{func.__name__}() took {end-start:.6f}s")
        return result              # returns original result
    return wrapper                 # returns the wrapper function

# Step 3: Apply it
def add(a, b):
    return a + b

timed_add = timer(add)    # manually applying
print(timed_add(3, 4))    # add() took 0.000001s  →  7
```

```python
# Step 4: The @ syntax is just shorthand for the above!
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__}() took {time.time()-start:.6f}s")
        return result
    return wrapper

@timer                    # ← same as: add = timer(add)
def add(a, b):
    return a + b

@timer
def multiply(a, b):
    return a * b

add(3, 4)         # add() took 0.000001s
multiply(3, 4)    # multiply() took 0.000001s
```

## ⚠️ Preserving Function Identity — `functools.wraps`

```python
def timer(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@timer
def add(a, b):
    """Adds two numbers."""
    return a + b

# Problem:
print(add.__name__)    # 'wrapper'  ← wrong! Should be 'add'
print(add.__doc__)     # None       ← wrong! Docstring is gone!

# The decorator replaced 'add' with 'wrapper' — metadata is lost!
```

```python
from functools import wraps

def timer(func):
    @wraps(func)                   # ← preserves __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@timer
def add(a, b):
    """Adds two numbers."""
    return a + b

print(add.__name__)    # 'add'              ✓
print(add.__doc__)     # 'Adds two numbers.'  ✓
```

> **Rule:** Always use `@wraps(func)` on your wrapper. Always. No exceptions.

## Decorators With Arguments

What if you want `@timer(unit="ms")`?
You need a decorator factory — a function that returns a decorator.

```python
from functools import wraps
import time

def timer(unit="s"):                     # outer: receives arguments
    def decorator(func):                  # middle: receives function
        @wraps(func)
        def wrapper(*args, **kwargs):     # inner: runs on each call
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            if unit == "ms":
                elapsed *= 1000
            print(f"{func.__name__}() took {elapsed:.4f}{unit}")
            return result
        return wrapper
    return decorator

@timer(unit="ms")
def add(a, b):
    return a + b

add(3, 4)    # add() took 0.0123ms
```

```
DECORATOR FACTORY STRUCTURE:

outer(arguments)                     # @timer(unit="ms")
  └─ returns → decorator(func)       # @decorator applied to add
                  └─ returns → wrapper(*args, **kwargs)  # runs each call
```

## Stacking Multiple Decorators

```python
def bold(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return "<b>" + func(*args, **kwargs) + "</b>"
    return wrapper

def italic(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return "<i>" + func(*args, **kwargs) + "</i>"
    return wrapper

@bold
@italic
def greet(name):
    return f"Hello, {name}"

print(greet("Alice"))    # <b><i>Hello, Alice</i></b>
```

**Order of stacking:**
```
@bold          ← applied LAST  (outermost)
@italic        ← applied FIRST (innermost)
def greet:

Equivalent to:  greet = bold(italic(greet))

Execution order:  bold.wrapper → italic.wrapper → greet → back up
```

## Real-World Decorator Patterns

```python
# 1. Logging decorator
from functools import wraps
import logging

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with {args}, {kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__} returned {result}")
        return result
    return wrapper

# 2. Retry decorator
def retry(times=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == times - 1:
                        raise
                    print(f"Attempt {attempt+1} failed: {e}. Retrying...")
        return wrapper
    return decorator

@retry(times=3)
def fetch_data(url):
    ...    # might fail due to network

# 3. Cache/Memoize decorator (next chapter shows functools.lru_cache)
```

---

# 📖 Chapter 11 — Recursion — Functions That Call Themselves

## The Mental Model

```
Recursion is not magic. It's just a function calling itself.
But to use it correctly, you need TWO things:

1. BASE CASE  — the condition where recursion STOPS
2. RECURSIVE CASE — where the function calls itself with a SMALLER problem

Without base case → infinite recursion → stack overflow → crash!
```

## Classic Example — Factorial

```
5! = 5 × 4 × 3 × 2 × 1 = 120

Recursively:
5! = 5 × 4!
4! = 4 × 3!
3! = 3 × 2!
2! = 2 × 1!
1! = 1         ← BASE CASE (stop here)
```

```python
def factorial(n):
    # Base case: stop condition
    if n <= 1:
        return 1
    # Recursive case: reduce the problem
    return n * factorial(n - 1)

print(factorial(5))    # 120
```

## Call Stack Visualization

```
factorial(5) is called:

CALL STACK builds up:                 THEN unwinds:
───────────────────────               ───────────────────────
│ factorial(1) → 1     │              │ factorial(1) = 1     │ → returns 1
│ factorial(2) → 2×?   │              │ factorial(2) = 2×1=2 │ → returns 2
│ factorial(3) → 3×?   │              │ factorial(3) = 3×2=6 │ → returns 6
│ factorial(4) → 4×?   │              │ factorial(4) = 4×6=24│ → returns 24
│ factorial(5) → 5×?   │              │ factorial(5) = 5×24  │ → returns 120
───────────────────────               ───────────────────────
  (stack full, base case hit)           (stack empties, answers propagate up)
```

## The Recursion Limit

Python limits recursive calls to prevent stack overflow.

```python
import sys
print(sys.getrecursionlimit())    # 1000 (default)

# You CAN increase it (carefully):
sys.setrecursionlimit(5000)

# Deep recursion will still crash eventually:
def deep(n):
    return deep(n+1)

deep(0)    # RecursionError: maximum recursion depth exceeded
```

## Recursion vs Iteration — When to Use Which

```
┌────────────────────────────────────────────────────────────┐
│  USE RECURSION WHEN:         USE ITERATION WHEN:           │
│                                                            │
│  • Problem is naturally       • Performance matters        │
│    recursive (trees, graphs)  • Input can be very large   │
│  • Code clarity matters       • Simple repetition         │
│  • Divide & conquer           • Linear processing         │
│                                                            │
│  RECURSION PROS:              ITERATION PROS:             │
│  ✓ Elegant, readable          ✓ Faster (no frame overhead) │
│  ✓ Matches problem structure  ✓ No stack limit             │
│  ✓ Less state to manage       ✓ Memory efficient           │
│                                                            │
│  RECURSION CONS:              ITERATION CONS:             │
│  ✗ Stack overflow risk        ✗ More verbose sometimes    │
│  ✗ Slower (frame creation)    ✗ Harder for tree problems  │
│  ✗ Python has recursion limit                             │
└────────────────────────────────────────────────────────────┘
```

---

# 📖 Chapter 12 — Generator Functions

## The Problem With Regular Functions and Large Data

```python
# Imagine reading a 10GB log file:
def read_all_lines(filename):
    lines = []
    with open(filename) as f:
        for line in f:
            lines.append(line)    # stores ALL 10GB in memory!
    return lines

# This would crash most systems!
```

## The Generator Solution

A generator uses `yield` instead of `return`.
It produces one value at a time, on demand. Memory-efficient.

```python
def read_lines(filename):
    with open(filename) as f:
        for line in f:
            yield line       # pauses here, gives one line, resumes next call
```

## How `yield` Works

```python
def count_up(start, end):
    current = start
    while current <= end:
        yield current       # pause, send value, wait for next()
        current += 1        # resumes HERE after next() is called

gen = count_up(1, 5)        # creates generator object — nothing runs yet!
print(type(gen))            # <class 'generator'>

print(next(gen))    # 1   ← runs until yield, pauses
print(next(gen))    # 2   ← resumes, runs until yield again
print(next(gen))    # 3
print(next(gen))    # 4
print(next(gen))    # 5
print(next(gen))    # StopIteration exception ← no more values!
```

## Generator Memory Advantage

```
REGULAR FUNCTION:
[1][2][3][4][5]...[1000000]   ← ALL values in memory at once

GENERATOR:
[1]  →  processed  →  [2]  →  processed  →  [3]  → ...
        only one value in memory at a time!
```

```python
# Memory comparison:
import sys

regular = [x**2 for x in range(1_000_000)]    # list comprehension
gen_ver = (x**2 for x in range(1_000_000))    # generator expression

print(sys.getsizeof(regular))   # ~8,000,056 bytes (8 MB!)
print(sys.getsizeof(gen_ver))   # 200 bytes (almost nothing!)
```

## yield vs return

```
┌──────────────────────────────────────────────────────────┐
│  RETURN                        YIELD                     │
│                                                          │
│  Exits function completely     Pauses function           │
│  All state destroyed           State preserved           │
│  Called once                   Called many times         │
│  Returns all data at once      Returns one item at time  │
│  Memory: all data loaded       Memory: one item at time  │
└──────────────────────────────────────────────────────────┘
```

---

# 📖 Chapter 13 — Type Annotations

Python is dynamically typed — you don't have to declare types.
But you CAN add type hints for readability, IDE support, and static analysis.

```python
# Without annotations:
def add(a, b):
    return a + b

# With annotations:
def add(a: int, b: int) -> int:
    return a + b
```

> **Important:** Annotations are HINTS only. Python does NOT enforce them at runtime.
> `add("hello", "world")` still works even with `int` annotations.

## Common Annotation Patterns

```python
from typing import Optional, List, Dict, Tuple, Union, Callable

# Basic types:
def greet(name: str) -> str:
    return f"Hello, {name}"

# Optional (can be None):
def find_user(user_id: int) -> Optional[str]:
    # might return a name or None
    ...

# Collections:
def sum_all(numbers: List[int]) -> int:
    return sum(numbers)

def get_scores() -> Dict[str, int]:
    return {"Alice": 95, "Bob": 87}

# Multiple return:
def min_max(items: List[int]) -> Tuple[int, int]:
    return min(items), max(items)

# Union (one or the other):
def process(data: Union[str, int]) -> str:
    return str(data)

# Callable (a function as argument):
def apply(func: Callable[[int], int], value: int) -> int:
    return func(value)

# Python 3.10+ simplified syntax:
def find(x: int | None) -> str | None:
    ...
```

---

# 📖 Chapter 14 — Docstrings

A docstring is a string literal as the very first statement in a function.
It documents what the function does, its parameters, and return value.

```python
def calculate_tax(amount: float, rate: float = 0.18) -> float:
    """
    Calculate tax on a given amount.

    Args:
        amount: The base amount before tax.
        rate: Tax rate as a decimal (default: 0.18 for 18%).

    Returns:
        The tax amount (not the total — just the tax portion).

    Raises:
        ValueError: If amount is negative.

    Example:
        >>> calculate_tax(1000)
        180.0
        >>> calculate_tax(1000, 0.28)
        280.0
    """
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    return amount * rate
```

Accessing the docstring:
```python
print(calculate_tax.__doc__)
help(calculate_tax)    # formatted output with full docstring
```

---

# 📖 Chapter 15 — Pure Functions & Side Effects

## What Is a Pure Function?

```
A pure function:
  1. Given the same input, ALWAYS returns the same output
  2. Has NO side effects (doesn't change anything outside itself)
```

```python
# ✅ Pure function:
def add(a, b):
    return a + b
# Always: add(3,4) == 7. No matter when, how many times, nothing else runs.

# ❌ Not pure — same input, different output:
import random
def random_add(a, b):
    return a + b + random.random()

# ❌ Not pure — modifies external state:
total = 0
def add_to_total(x):
    global total
    total += x    # side effect: modifies global!
    return total
```

## Side Effects — What Counts?

```
Side effects include:
  • Modifying a global variable
  • Modifying a mutable argument (list, dict)
  • Writing to a file
  • Printing to console
  • Sending a network request
  • Modifying a database
  • Raising exceptions
```

## Why Pure Functions Matter

```
TESTING:     pure functions are trivially testable — just assert input/output
DEBUGGING:   pure functions never cause "action at a distance" bugs
CONCURRENCY: pure functions can run in parallel safely — no shared state
CACHING:     pure functions can be safely memoized — same input → same output
RELIABILITY: pure functions are predictable — no surprises
```

---

# 📖 Chapter 16 — Advanced functools

## `functools.lru_cache` — Memoization Made Easy

Memoization = caching function results so repeated calls with same args are instant.

```python
from functools import lru_cache

# Without cache — extremely slow for large n:
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

# fib(40) makes 2+ billion redundant calls!

# With lru_cache — computed each value only once:
@lru_cache(maxsize=None)    # None = unlimited cache
def fib_fast(n):
    if n < 2:
        return n
    return fib_fast(n-1) + fib_fast(n-2)

fib_fast(100)    # instant! each value computed exactly once
```

**Visualizing the difference:**
```
fib(5) WITHOUT cache:              fib(5) WITH cache:
────────────────────               ─────────────────
fib(5)                             fib(5)
├── fib(4)                         ├── fib(4)
│   ├── fib(3)                     │   ├── fib(3)
│   │   ├── fib(2)                 │   │   ├── fib(2)
│   │   │   ├── fib(1)=1           │   │   │   ├── fib(1)=1
│   │   │   └── fib(0)=0           │   │   │   └── fib(0)=0
│   │   └── fib(1)=1               │   │   └── [cached: 1]
│   └── fib(2)       ← REPEATED    │   └── [cached: fib(2)]
│       ├── fib(1)=1                └── [cached: fib(3)]
│       └── fib(0)=0
└── fib(3)           ← REPEATED
    ├── fib(2)       ← REPEATED
    │   └── ...
    └── fib(1)=1

15 calls total                      5 calls total
```

## `functools.partial` — Pre-filling Arguments

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

# Create a specialized version with exponent pre-filled:
square = partial(power, exponent=2)
cube   = partial(power, exponent=3)

print(square(5))    # 25
print(cube(3))      # 27

# Real use case — pre-configured print:
from functools import partial
debug_print = partial(print, "[DEBUG]", end="\n\n")
debug_print("User logged in")    # [DEBUG] User logged in
                                  # (with double newline)
```

---

# 📖 Chapter 17 — Function Attributes & Introspection

Functions are objects and carry metadata you can inspect.

```python
def greet(name: str, greeting: str = "Hello") -> str:
    """Greets a person."""
    return f"{greeting}, {name}!"

print(greet.__name__)         # 'greet'
print(greet.__doc__)          # 'Greets a person.'
print(greet.__module__)       # '__main__'
print(greet.__annotations__)  # {'name': <class 'str'>, 'greeting': <class 'str'>, 'return': <class 'str'>}
print(greet.__defaults__)     # ('Hello',)
print(greet.__code__.co_varnames)  # ('name', 'greeting')

# Inspect module for deeper introspection:
import inspect

sig = inspect.signature(greet)
for name, param in sig.parameters.items():
    print(f"{name}: default={param.default}, kind={param.kind.name}")
```

---

# 📖 Chapter 18 — The Complete Mental Model

## When to Use What

```
┌────────────────────────────────────────────────────────────────────────┐
│  SITUATION                          SOLUTION                           │
├────────────────────────────────────────────────────────────────────────┤
│  Reusable logic                     Regular def function               │
│  Inline short expression            Lambda                             │
│  Remember state between calls       Closure or class                  │
│  Add behavior without changing code Decorator                          │
│  Problem reduces to smaller version Recursion                          │
│  Large data, one-at-a-time          Generator                          │
│  Cache expensive computations       lru_cache                          │
│  Specialize a general function      partial                            │
│  Variable number of args            *args / **kwargs                   │
│  Force named arguments              keyword-only (* in signature)      │
│  Cache same-output for same-input   Pure function + lru_cache          │
└────────────────────────────────────────────────────────────────────────┘
```

## The 10 Principles of Function Design

```
 1. ONE RESPONSIBILITY      One function does one thing, well
 2. MEANINGFUL NAME         Name tells you what it does — no need for comments
 3. SMALL SIZE              If it doesn't fit on screen, split it
 4. PREFER RETURN           Return values; avoid print inside functions
 5. AVOID MUTABLE DEFAULTS  Use None; create inside the function body
 6. USE @wraps              Always preserve metadata in decorators
 7. DOCUMENT                Docstring for anything non-obvious
 8. PURE WHEN POSSIBLE      No side effects = easier testing
 9. HANDLE NONE             If input might be None, handle it explicitly
10. TYPE HINTS              Annotate for readability and tooling support
```

## The Most Common Mistakes

```python
# ❌ Mistake 1: Mutable default argument
def bad(items=[]):  ...                # USE: def bad(items=None):

# ❌ Mistake 2: Late binding in closure
funcs = [lambda: i for i in range(5)] # USE: lambda i=i: i

# ❌ Mistake 3: Forgetting @wraps
def my_decorator(func):
    def wrapper(*args, **kwargs): ...  # USE: @wraps(func) on wrapper
    return wrapper

# ❌ Mistake 4: Calling vs referencing a function
result = my_func                       # stores function — nothing runs
result = my_func()                     # calls function — runs!

# ❌ Mistake 5: Using global when you shouldn't
global counter                         # use class or pass/return instead

# ❌ Mistake 6: No base case in recursion
def infinite(n): return infinite(n-1) # RecursionError! Missing base case

# ❌ Mistake 7: Checking for None with ==
if result == None: ...                 # USE: if result is None:

# ❌ Mistake 8: Heavy logic in lambda
f = lambda x: (x**2 if x>0 else abs(x)*3 + x/2)  # USE def for clarity
```

---

# 🎯 Final Summary

```
┌──────────────────────────────────────────────────────────────────────────┐
│  CONCEPT               WHAT IT IS                   REMEMBER BY          │
├──────────────────────────────────────────────────────────────────────────┤
│  def                   Function definition          "define for later"   │
│  Parameters            Placeholders in definition   "blueprint slots"    │
│  Arguments             Values at call time          "actual fill-ins"    │
│  return                Exit + send value back       "reply to caller"    │
│  *args                 Variable positionals→tuple   "star = spread"      │
│  **kwargs              Variable keywords→dict       "double star = map"  │
│  LEGB                  Scope search order           L→E→G→B (Local 1st) │
│  global/nonlocal       Reach into outer scope       "knock upward"       │
│  First-class func      Functions are objects        "treat like data"    │
│  Lambda                Anonymous one-liner          "throwaway function" │
│  Closure               Inner func + outer state     "captures memory"   │
│  Late binding          Closure sees current value   "lookup at call time"│
│  Decorator             Wrap without touching        "@symbol = wrapper"  │
│  @wraps                Preserve metadata            "always use it"      │
│  Recursion             Function calls itself        "smaller + stop"     │
│  Generator             yield = pause + resume       "lazy delivery"      │
│  lru_cache             Cache results                "remember answers"   │
│  partial               Pre-fill arguments           "specialize general" │
│  Pure function         No side effects              "math function"      │
└──────────────────────────────────────────────────────────────────────────┘
```

---

# 🔁 Navigation

| | |
|---|---|
| ⬅️ Previous | [03 — Data Types](../03_data_types/theory.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🎤 Interview Prep | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ➡️ Next | [05 — OOP](../05_oops/theory.md) |
| 🏠 Home | [README](../README.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Data Types — Interview Q&A](../03_data_types/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
