<a id="top"></a>
# 🧩 Functions — The Complete Mastery Guide

> *"A program without functions is like a city without streets —*
> *every building exists, but nothing connects. Nothing scales."*

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

## 📖 Table of Contents

- [The Problem Functions Solve](#the-problem-functions-solve)
- [1. Anatomy of a Function](#1-anatomy-of-a-function)
- [2. How Python Executes a Function](#2-how-python-executes-a-function)
  - [The Call Stack — Visual Model](#call-stack-visual-model)
  - [Stack Frame Contents](#stack-frame-contents)
- [3. Parameters & Arguments — All 7 Types](#3-parameters-arguments--all-7-types)
  - [The Mutable Default Argument Trap](#the-mutable-default-argument-trap)
  - [Complete Parameter Order Rule](#complete-parameter-order-rule)
- [4. The Return Statement — All Behaviors](#4-the-return-statement--all-behaviors)
  - [Return vs Print](#return-vs-print)
- [5. Scope — The LEGB Rule](#5-scope--the-legb-rule)
  - [global and nonlocal](#global-and-nonlocal)
  - [Memory Behavior by Scope](#memory-behavior-by-scope)
- [6. Functions Are Objects](#6-functions-are-objects)
  - [Higher-Order Functions](#higher-order-functions)
  - [Function Composition](#function-composition)
- [7. Lambda Functions](#7-lambda-functions)
- [8. Closures — Functions That Remember](#8-closures--functions-that-remember)
  - [The Late-Binding Trap](#the-late-binding-trap)
  - [Closure Cell Internals](#closure-cell-internals)
- [9. Decorators — Functions That Wrap Functions](#9-decorators--functions-that-wrap-functions)
  - [@wraps — Preserving Metadata](#wraps--preserving-metadata)
  - [Decorators with Arguments](#decorators-with-arguments)
  - [Stacking Decorators](#stacking-decorators)
  - [Real-World Decorator Patterns](#real-world-decorator-patterns)
- [10. Recursion — Functions That Call Themselves](#10-recursion--functions-that-call-themselves)
  - [Call Stack Visualization](#call-stack-visualization-recursion)
  - [Recursion vs Iteration](#recursion-vs-iteration)
- [11. Generator Functions](#11-generator-functions)
- [12. Type Annotations](#12-type-annotations)
- [13. Docstrings](#13-docstrings)
- [14. Pure Functions & Side Effects](#14-pure-functions--side-effects)
  - [Referential Transparency](#referential-transparency)
- [15. Advanced functools](#15-advanced-functools)
  - [lru_cache — Memoization](#lru-cache-memoization)
  - [partial — Specializing Functions](#partial-specializing-functions)
  - [reduce — Folding a Sequence](#reduce-folding-a-sequence)
- [16. Function Attributes & Introspection](#16-function-attributes--introspection)
- [17. The Complete Mental Model](#17-the-complete-mental-model)
  - [When to Use What](#when-to-use-what)
  - [The 10 Principles of Function Design](#the-10-principles)
- [🎯 Final Summary](#final-summary)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`def`, return values · `*args` / `**kwargs` · Default arguments · Lambda functions · Closures · LEGB rule · `functools.lru_cache`

**Should Learn** — Important for real projects, comes up regularly:
Positional-only `/` and keyword-only `*` params · `functools.partial` · `functools.wraps` · Recursion + `sys.setrecursionlimit()`

**Good to Know** — Useful in specific situations:
`functools.reduce` · `inspect.signature()` · Docstring formats (Google/NumPy/Sphinx)

**Reference** — Know it exists, look up when needed:
Tail recursion (Python doesn't optimize it) · `functools.singledispatch` (see decorators module)

<a id="the-problem-functions-solve"></a>
# The Problem Functions Solve

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

> 📝 **Practice:** [Q1 — Refactor duplicated code](./practice.md#q1--ch1--refactor-duplicated-code) · [Q2 — Function anatomy](./practice.md#q2--ch2--function-anatomy)

> [↑ Back to Top](#top)

<a id="1-anatomy-of-a-function"></a>
# 1. Anatomy of a Function

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

> 📝 **Practice:** [Q2 — Function anatomy](./practice.md#q2--ch2--function-anatomy)

> [↑ Back to Top](#top)

<a id="2-how-python-executes-a-function"></a>
# 2. How Python Executes a Function

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

<a id="call-stack-visual-model"></a>
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

<a id="stack-frame-contents"></a>
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

> 📝 **Practice:** [Q3 — Call stack trace](./practice.md#q3--ch3--call-stack-trace)

> [↑ Back to Top](#top)

<a id="3-parameters-arguments--all-7-types"></a>
# 3. Parameters & Arguments — All 7 Types

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

## Type 1 — Positional Arguments

Order is everything. First argument → first parameter. Always.

```python
def describe(animal, action, place):
    print(f"The {animal} {action} in the {place}")

describe("cat", "sleeps", "garden")   # The cat sleeps in the garden
describe("sleeps", "cat", "garden")   # The sleeps cat in the garden ← wrong order!
```

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

<a id="the-mutable-default-argument-trap"></a>
## ⚠️ Type 3 Edge Case — The Mutable Default Argument Trap

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

> 📝 **Practice:** [Q10 — Mutable default trap](../python_practice_questions_100.md#q10--critical--mutable-default-argument) · [Q5 — Spot and fix](./practice.md#q5--ch4--mutable-default-arg-trap)

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

**Unpacking a dict with `**` in a call:**
```python
data = {"name": "Alice", "age": 25}
create_profile(**data)    # same as create_profile(name="Alice", age=25)
```

## Type 6 — Keyword-Only Parameters (after `*`)

Force a parameter to ALWAYS be passed by name. Never by position.

```python
def connect(host, port, *, timeout, retries=3):
    #                    ↑
    #              bare * means: everything after this is keyword-only
    print(f"Connecting to {host}:{port}, timeout={timeout}")

connect("localhost", 8080, timeout=30)            # ✓
connect("localhost", 8080, timeout=30, retries=5) # ✓
connect("localhost", 8080, 30)                    # ✗ TypeError: timeout must be keyword
```

**Why is this useful?**
```
Without keyword-only:
connect("localhost", 8080, 30, 5)   ← What is 30? What is 5? Unclear!

With keyword-only:
connect("localhost", 8080, timeout=30, retries=5)  ← Crystal clear!
```

## Type 7 — Positional-Only Parameters (before `/`)

Force a parameter to ALWAYS be passed by position. Never by name.
(Added in Python 3.8)

```python
def power(base, exponent, /):
    #                    ↑
    #   / means: everything before this is positional-only
    return base ** exponent

power(2, 10)              # ✓  1024
power(base=2, exponent=10)  # ✗ TypeError: must be positional
```

**Real-world use:** The built-in `len()`, `abs()` etc. use positional-only.

<a id="complete-parameter-order-rule"></a>
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

> 📝 **Practice:** [Q4 — Positional/keyword args](./practice.md#q4--ch4--positional--keyword-args) · [Q6 — *args](./practice.md#q6--ch4--args) · [Q7 — **kwargs](./practice.md#q7--ch4--kwargs) · [Q8 — All 7 param types](./practice.md#q8--ch4--all-7-parameter-types)

> [↑ Back to Top](#top)

<a id="4-the-return-statement--all-behaviors"></a>
# 4. The Return Statement — All Behaviors

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

**Common mistake — None comparison:** Use `if result is None:` not `if result == None:`. The `is` operator checks identity. Some objects override `__eq__` such that `== None` can behave unexpectedly. `is None` always works correctly.

<a id="return-vs-print"></a>
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

> 📝 **Practice:** [Q9 — Return with early returns](./practice.md#q9--ch5--return-with-early-returns) · [Q10 — Return vs Print](./practice.md#q10--ch5--return-vs-print)

> [↑ Back to Top](#top)

<a id="5-scope--the-legb-rule"></a>
# 5. Scope — The LEGB Rule

> When Python encounters a variable name, it searches for it in this exact order.
> Miss one level and you'll be confused for years.

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

<a id="global-and-nonlocal"></a>
## global and nonlocal

**`global` — reach the module-level scope:**

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

**`nonlocal` — reach the enclosing (outer function) scope:**

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

**Common mistake — overusing global:** If multiple functions need to share state, use a class or pass values explicitly. `global` is a design smell — it makes functions harder to test and reason about. In production code reviews, unnecessary `global` is a red flag. The one common exception: module-level configuration constants.

<a id="memory-behavior-by-scope"></a>
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

> 📝 **Practice:** [Q11 — LEGB prediction](./practice.md#q11--ch6--legb-prediction) · [Q12 — global and nonlocal](./practice.md#q12--ch6--global-and-nonlocal)

> [↑ Back to Top](#top)

<a id="6-functions-are-objects"></a>
# 6. Functions Are Objects (First-Class Citizens)

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

<a id="higher-order-functions"></a>
## Higher-Order Functions

A **higher-order function** is any function that takes a function as argument OR returns a function.
This is the foundation for decorators, map/filter/reduce, and callback patterns.

```python
def apply_twice(func, value):
    return func(func(value))

def double(x):
    return x * 2

print(apply_twice(double, 3))    # double(double(3)) = double(6) = 12

# With lambdas:
print(apply_twice(lambda x: x + 10, 5))    # (5+10)+10 = 25
```

```python
# Returning a function — factory pattern:
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

<a id="function-composition"></a>
## Function Composition

Combining small, focused functions to build more complex behavior — the output of one function becomes the input of the next.

```python
def double(x):
    return x * 2

def add_one(x):
    return x + 1

def to_string(x):
    return f"Result: {x}"

# Manual composition (right to left):
result = to_string(add_one(double(5)))   # double→10, add_one→11, to_string→"Result: 11"

# General compose function:
def compose(*funcs):
    """Apply functions right-to-left: compose(f, g)(x) = f(g(x))"""
    def composed(x):
        for f in reversed(funcs):
            x = f(x)
        return x
    return composed

transform = compose(to_string, add_one, double)
print(transform(5))    # "Result: 11"
```

```
COMPOSITION PIPELINE:
  5 ──► double ──► 10 ──► add_one ──► 11 ──► to_string ──► "Result: 11"
```

> 📝 **Practice:** [Q13 — First-class functions](./practice.md#q13--ch7--first-class-functions) · [Q14 — apply_twice](./practice.md#q14--ch7--apply_twice) · [Q15 — compose()](./practice.md#q15--ch7--compose)

> [↑ Back to Top](#top)

<a id="7-lambda-functions"></a>
# 7. Lambda Functions

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

**Common mistake — complex lambda:** Heavy logic in a lambda is a readability trap. If it doesn't fit in one clear expression, use `def`. Lambdas are for throwaway one-liners — sort keys, quick filters, callback slots.

> 📝 **Practice:** [Q16 — Lambda sort](./practice.md#q16--ch8--lambda-sort) · [Q17 — Lambda map/filter](./practice.md#q17--ch8--lambda-with-mapfilter)

> [↑ Back to Top](#top)

<a id="8-closures--functions-that-remember"></a>
# 8. Closures — Functions That Remember

A closure happens when an inner function uses a variable from its outer function,
and the outer function returns the inner function.

The inner function "closes over" those outer variables — it carries them with it,
even after the outer function has finished and its stack frame is gone.

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

<a id="the-late-binding-trap"></a>
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

<a id="closure-cell-internals"></a>
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

> 📝 **Practice:** [Q18 — Basic closure](./practice.md#q18--ch9--basic-closure) · [Deep dive →](./02_closures_decorators/01_closures_theory.md)

> [↑ Back to Top](#top)

<a id="9-decorators--functions-that-wrap-functions"></a>
# 9. Decorators — Functions That Wrap Functions

You have 5 functions and you want to time how long each takes.
Without decorators, you add timing code to every function — 5 places.
Tomorrow you want to also log. That's 10 places.

Decorators let you add behavior to a function without touching its code.

## Building a Decorator From Scratch

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

```
DECORATOR ANATOMY:
  @timer            ← 1. Python sees this
  def add(a, b):    ← 2. Reads the function definition
      ...
                    ← 3. Runs: add = timer(add)
                    ← 4. 'add' now points to 'wrapper'
```

<a id="wraps--preserving-metadata"></a>
## ⚠️ @wraps — Preserving Metadata

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

**Common mistake — forgetting @wraps:** Without `@wraps(func)`, every decorated function reports `__name__ = 'wrapper'`. This breaks logging, debugging, and `help()` output for your entire codebase.

<a id="decorators-with-arguments"></a>
## Decorators with Arguments

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

<a id="stacking-decorators"></a>
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

<a id="real-world-decorator-patterns"></a>
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

# 3. Cache/Memoize — see functools.lru_cache in Chapter 15
```

> 📝 **Practice:** [Q19 — Basic decorator](./practice.md#q19--ch10--basic-decorator) · [Q31 — retry decorator](./practice.md#q31--mixed--retry-decorator) · [Q32 — Decorator with arguments](./practice.md#q32--mixed--decorator-with-arguments) · [Deep dive →](./02_closures_decorators/02_decorators_theory.md)

> [↑ Back to Top](#top)

<a id="10-recursion--functions-that-call-themselves"></a>
# 10. Recursion — Functions That Call Themselves

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

**Common mistake — missing base case:** Every recursive function MUST have a base case. Without it, the function calls itself forever until Python raises `RecursionError: maximum recursion depth exceeded` (at ~1000 calls). Always write the base case FIRST before writing the recursive step.

<a id="call-stack-visualization-recursion"></a>
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

<a id="recursion-vs-iteration"></a>
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

> 📝 **Practice:** [Q20 — Recursion: factorial](./practice.md#q20--ch11--recursion-factorial) · [Q21 — Fix broken recursion](./practice.md#q21--ch11--fix-broken-recursion)

> [↑ Back to Top](#top)

<a id="11-generator-functions"></a>
# 11. Generator Functions

A **generator function** uses `yield` instead of `return`. It produces values one at a time — pausing execution at each `yield` and resuming when the caller asks for the next value. This gives O(1) memory regardless of how many values are generated.

```python
# Regular function — builds entire list in memory:
def squares(n):
    return [x**2 for x in range(n)]   # 1 million items = 8MB

# Generator function — produces one value at a time:
def squares_lazy(n):
    for x in range(n):
        yield x**2                     # pauses here, resumes on next()

gen = squares_lazy(1_000_000)
print(next(gen))    # 0   ← runs until yield, pauses
print(next(gen))    # 1   ← resumes, runs until next yield
# 1 million items = 200 bytes (just the generator object!)
```

```
GENERATOR EXECUTION MODEL:
  squares_lazy(5)
       │
  [start]──► yield 0 ──► [pause]
                              │ next()
  [resume]──► yield 1 ──► [pause]
                              │ next()
  [resume]──► yield 4 ──► [pause]  ...and so on
```

This is a major Python topic. The full depth — iterator protocol (`__iter__` / `__next__`), `yield from`, `send()`, generator pipelines, async generators — lives in the dedicated module.

**[→ Deep dive: 11_generators_iterators/theory.md](../11_generators_iterators/theory.md)**
- Iterator protocol and lazy evaluation
- `yield from` and delegation
- `send()` — generators as coroutines
- Generator pipelines for O(1) memory processing

> 📝 **Practice:** [Q22 — Generator: lazy squares](./practice.md#q22--ch12--generator-lazy-squares) · [Q23 — Generator pipeline](./practice.md#q23--ch12--generator-pipeline)

> [↑ Back to Top](#top)

<a id="12-type-annotations"></a>
# 12. Type Annotations

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

> 📝 **Practice:** [Q24 — Type annotations](./practice.md#q24--ch13--type-annotations)

> [↑ Back to Top](#top)

<a id="13-docstrings"></a>
# 13. Docstrings

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

> 📝 **Practice:** [Q25 — Google-style docstring](./practice.md#q25--ch14--google-style-docstring)

> [↑ Back to Top](#top)

<a id="14-pure-functions--side-effects"></a>
# 14. Pure Functions & Side Effects

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

<a id="referential-transparency"></a>
## Referential Transparency

A function is **referentially transparent** if you can replace any call to it with its return value anywhere in the program without changing the program's behavior.

```python
# Referentially transparent:
def add(a, b):
    return a + b

result = add(3, 4)    # → 7
# You can replace `add(3, 4)` with `7` everywhere — program behaves identically.
# This is why pure functions are easy to reason about and cache.

# NOT referentially transparent:
def get_user_count():
    return db.query("SELECT COUNT(*) FROM users")
# Returns 5 now, 6 tomorrow — depends on external state.
# Cannot substitute with a fixed value.
```

```
REFERENTIALLY TRANSPARENT?
                                        │
  Same input → same output?  ──── YES ──┤
  No external state read?    ──── YES ──┴──► YES → can memoize, parallelize, substitute
                                        │
  Any of the above fails? ──────────────┴──► NO  → must treat as effectful
```

Pure functions are always referentially transparent. This property is what makes `functools.lru_cache` safe — if a function isn't pure, caching its result would return stale data.

> 📝 **Practice:** [Q26 — Pure vs impure](./practice.md#q26--ch15--pure-vs-impure) · [Deep dive →](./01_functional_programming/practice.md)

> [↑ Back to Top](#top)

<a id="15-advanced-functools"></a>
# 15. Advanced functools

<a id="lru-cache-memoization"></a>
## `functools.lru_cache` — Memoization Made Easy

**Memoization** = caching function results so repeated calls with same args are instant.
Safe to use on pure (referentially transparent) functions only.

```python
from functools import lru_cache

# Without cache — extremely slow for large n:
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

# fib(40) makes 2+ billion redundant calls!

# With lru_cache — each value computed only once:
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

<a id="partial-specializing-functions"></a>
## `functools.partial` — Specializing Functions

`partial` creates a new function with some arguments pre-filled. It's the tool for specializing a general function without writing a new one.

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
debug_print = partial(print, "[DEBUG]", end="\n\n")
debug_print("User logged in")    # [DEBUG] User logged in
                                  # (with double newline)
```

<a id="reduce-folding-a-sequence"></a>
## `functools.reduce` — Folding a Sequence

`reduce` applies a function cumulatively to all items in a sequence, collapsing it into a single value — like "folding" a list from left to right.

```python
from functools import reduce

# reduce(func, [a, b, c, d]) = func(func(func(a, b), c), d)

# Sum using reduce:
total = reduce(lambda acc, x: acc + x, [1, 2, 3, 4, 5])
# → ((((1+2)+3)+4)+5) = 15

# Product:
product = reduce(lambda acc, x: acc * x, [1, 2, 3, 4, 5])
# → 120

# Find maximum:
maximum = reduce(lambda a, b: a if a > b else b, [3, 1, 4, 1, 5, 9, 2])
# → 9
```

```
REDUCE VISUALIZATION:
  [1, 2, 3, 4, 5]  with  lambda acc, x: acc + x

  Step 1:  acc=1,  x=2  → 3
  Step 2:  acc=3,  x=3  → 6
  Step 3:  acc=6,  x=4  → 10
  Step 4:  acc=10, x=5  → 15
  Result: 15
```

**When to use reduce vs comprehension:**
```python
# Use reduce for custom fold operations:
reduce(lambda d, kv: {**d, kv[0]: kv[1]}, [("a",1),("b",2)], {})  # dict from pairs

# Prefer sum/max/min for standard aggregations (clearer):
sum([1,2,3,4,5])          # ← prefer this over reduce for simple sums
max([3,1,4,1,5,9])        # ← prefer this over reduce for max
```

> 📝 **Practice:** [Q27 — lru_cache](./practice.md#q27--ch16--lru_cache) · [Q28 — partial](./practice.md#q28--ch16--functools.partial) · [Itertools/Functools deep dive →](./03_itertools_functools/practice.md)

> [↑ Back to Top](#top)

<a id="16-function-attributes--introspection"></a>
# 16. Function Attributes & Introspection

Functions are objects and carry metadata you can inspect at runtime.

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
```

**Deeper introspection with the `inspect` module:**

```python
import inspect

sig = inspect.signature(greet)
for name, param in sig.parameters.items():
    print(f"{name}: default={param.default}, kind={param.kind.name}")

# name: default=<class 'inspect._empty'>, kind=POSITIONAL_OR_KEYWORD
# greeting: default=Hello, kind=POSITIONAL_OR_KEYWORD
```

**Real-world use — building a framework that reads function signatures:**
```python
import inspect

def auto_call(func, available_data: dict):
    """Call func with only the arguments it needs from available_data."""
    sig = inspect.signature(func)
    needed = {k: v for k, v in available_data.items() if k in sig.parameters}
    return func(**needed)

def process(name, age):
    return f"{name} is {age}"

data = {"name": "Alice", "age": 30, "city": "Mumbai"}  # extra key ignored
auto_call(process, data)    # "Alice is 30"
```

> 📝 **Practice:** [Q29 — Introspection](./practice.md#q29--ch17--introspection)

> [↑ Back to Top](#top)

<a id="17-the-complete-mental-model"></a>
# 17. The Complete Mental Model

<a id="when-to-use-what"></a>
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

<a id="the-10-principles"></a>
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

> [↑ Back to Top](#top)

<a id="final-summary"></a>
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
│  Referential transp.   Replaceable by its value     "no surprises"       │
└──────────────────────────────────────────────────────────────────────────┘
```

> 📝 **Practice:** [Q30 — Capstone](./practice.md#q30--ch18--capstone) · [Q34 — Debug TypeError](./practice.md#q34--mixed--debug-typeerror) · [Q35 — Rate limiter](./practice.md#q35--mixed--rate-limiter-using-closures)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [03_data_types → theory.md](../03_data_types/theory.md) |
| ➡ Next Module | [05_oops → theory.md](../05_oops/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[11_generators_iterators →](../11_generators_iterators/theory.md) · [10_decorators →](../10_decorators/theory.md) · [13_concurrency →](../13_concurrency/theory.md)

**Jump to specific topics in other files:**
- Mutable default arg trap → [04_functions/theory.md#the-mutable-default-argument-trap](./theory.md#the-mutable-default-argument-trap)
- LEGB scope → [04_functions/theory.md#5-scope--the-legb-rule](./theory.md#5-scope--the-legb-rule)
- Late binding closure → [04_functions/theory.md#the-late-binding-trap](./theory.md#the-late-binding-trap)
- Generators lazy evaluation → [11_generators_iterators/theory.md](../11_generators_iterators/theory.md)
- GIL → [13_concurrency/theory.md](../13_concurrency/theory.md)

> [↑ Back to Top](#top)
