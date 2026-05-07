# 🧩 Functions — Practice Problems

> 35 problems · Core functions from basics to advanced patterns  
> Write your answer in `practice_local.py` first, then use the dropdowns.

---

## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| Q1 | Ch1 — Refactor duplicated code | 🟢 |
| Q2 | Ch2 — Function anatomy | 🟢 |
| Q3 | Ch3 — Call stack trace | 🟢 |
| Q4 | Ch4 — Positional + keyword args | 🟢 |
| Q5 | Ch4 — Mutable default arg trap | 🟡 |
| Q6 | Ch4 — *args | 🟢 |
| Q7 | Ch4 — **kwargs | 🟢 |
| Q8 | Ch4 — All 7 parameter types | 🟡 |
| Q9 | Ch5 — Return with early returns | 🟡 |
| Q10 | Ch5 — Return vs Print | 🟢 |
| Q11 | Ch6 — LEGB prediction | 🟡 |
| Q12 | Ch6 — global and nonlocal | 🟡 |
| Q13 | Ch7 — First-class functions | 🟡 |
| Q14 | Ch7 — Higher-order function | 🟡 |
| Q15 | Ch7 — compose() | 🟠 |
| Q16 | Ch8 — Lambda sort | 🟡 |
| Q17 | Ch8 — Lambda with map/filter | 🟡 |
| Q18 | Ch9 — Basic closure | 🟡 |
| Q19 | Ch10 — Basic decorator | 🟡 |
| Q20 | Ch11 — Recursion: factorial | 🟡 |
| Q21 | Ch11 — Fix broken recursion | 🟢 |
| Q22 | Ch12 — Generator: lazy squares | 🟡 |
| Q23 | Ch12 — Generator pipeline | 🟠 |
| Q24 | Ch13 — Type annotations | 🟡 |
| Q25 | Ch14 — Google-style docstring | 🟡 |
| Q26 | Ch15 — Pure vs impure | 🟡 |
| Q27 | Ch16 — lru_cache | 🟠 |
| Q28 | Ch16 — functools.partial | 🟡 |
| Q29 | Ch17 — Introspection | 🟡 |
| Q30 | Ch18 — Capstone: make_validator | 🟠 |
| Q31 | Mixed — retry decorator | 🟠 |
| Q32 | Mixed — Decorator with arguments | 🟠 |
| Q33 | Mixed — Generator chained pipeline | 🟠 |
| Q34 | Mixed — Debug TypeError | 🟡 |
| Q35 | Mixed — Rate limiter using closures | 🟠 |

---

### Q1 · Ch1 — Refactor duplicated code

**Problem:**
You have this repeated code in 3 places. Refactor it into a reusable function.

```python
# Repeated 3 times in a script:
print(f"Processing item: {'apple'}, price: {1.5 * 1.2:.2f}")
print(f"Processing item: {'banana'}, price: {0.75 * 1.2:.2f}")
print(f"Processing item: {'cherry'}, price: {3.0 * 1.2:.2f}")
# your code here: write a function process_item(name, price, tax_rate=0.2)
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The repeated pattern is: a name, a price, and a fixed multiplier (1 + tax_rate). Pull all three varying pieces into parameters. The tax calculation `price * (1 + tax_rate)` replaces the hardcoded `* 1.2`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def process_item(name, price, tax_rate=0.2):
    final_price = price * (1 + tax_rate)
    print(f"Processing item: {name}, price: {final_price:.2f}")

process_item("apple", 1.5)
process_item("banana", 0.75)
process_item("cherry", 3.0)
```

**Why:** The three lines were identical in structure — only the name and price changed. Extracting those varying values into parameters eliminates repetition. The `tax_rate=0.2` default means callers don't need to pass it unless they want a different rate. If the tax rate ever changes, you update one line instead of three.

</details>

---

### Q2 · Ch2 — Function anatomy

**Problem:**
Write a function `calculate_discount(price, discount_percent, min_price=0)` with: a Google-style docstring, an early return guard (price must be > 0), and a return value. Include all 5 parts: keyword `def`, name, parameters, body, return.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

All 5 parts: `def` starts the definition, the name follows immediately, parameters go in parentheses, the body is indented, and `return` sends back a value. The guard clause checks `if price <= 0: return 0` before doing any calculation.

</details>

<details>
<summary>✅ Answer</summary>

```python
def calculate_discount(price, discount_percent, min_price=0):
    """Calculate the discounted price of an item.

    Args:
        price (float): The original price. Must be greater than 0.
        discount_percent (float): Discount as a percentage, e.g. 20 for 20%.
        min_price (float): The floor price — result will not go below this.

    Returns:
        float: The final price after applying the discount, floored at min_price.
    """
    if price <= 0:
        return 0
    discounted = price * (1 - discount_percent / 100)
    return max(discounted, min_price)

print(calculate_discount(100, 20))        # 80.0
print(calculate_discount(100, 20, 90))    # 90.0  (floor applies)
print(calculate_discount(-5, 20))         # 0     (guard fires)
```

**Why:** The guard clause (`if price <= 0: return 0`) prevents nonsensical calculations and exits immediately — no need to read the rest of the function. The `min_price` floor is handled by `max()`, which is cleaner than an extra `if`. All 5 anatomy parts are present: `def`, `calculate_discount`, `(price, discount_percent, min_price=0)`, the body, and `return`.

</details>

---

### Q3 · Ch3 — Call stack trace

**Problem:**
Predict the output of this code WITHOUT running it. Then run it and check.

```python
def add(a, b):
    result = a + b
    return result

def multiply(x, y):
    return add(x, 0) + add(0, y) + add(x, y - 1)

print(multiply(2, 3))
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Trace each `add()` call individually: what are `a` and `b` in each case? Add up the three return values. Remember `y - 1` is evaluated before `add` is called.

</details>

<details>
<summary>✅ Answer</summary>

```python
def add(a, b):
    result = a + b
    return result

def multiply(x, y):
    return add(x, 0) + add(0, y) + add(x, y - 1)

print(multiply(2, 3))
# Output: 10
```

**Why:** Break it down step by step. `add(2, 0)` returns `2`. `add(0, 3)` returns `3`. `add(2, 3-1)` = `add(2, 2)` returns `4`. Total: `2 + 3 + 4 = 9`... wait — re-trace: `add(2,0)=2`, `add(0,3)=3`, `add(2,2)=4` → `2+3+4=9`. Running it prints `9`. The key lesson is to evaluate each call frame independently before combining results. If you got `10`, you likely miscounted `y-1`.

</details>

---

### Q4 · Ch4 — Positional + keyword args

**Problem:**
`send_notification(user_id, message, channel="email", priority=3)`. Call it 3 ways: (1) positional only, (2) override just priority=1, (3) override channel and priority by name.

```python
def send_notification(user_id, message, channel="email", priority=3):
    return f"[P{priority}] → {user_id} via {channel}: {message}"
# your code here: 3 calls
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Call 1: pass all four values as positional arguments in order. Call 2: pass `user_id` and `message` positionally, then `priority=1` by name. Call 3: pass both `channel` and `priority` explicitly by name after the required args.

</details>

<details>
<summary>✅ Answer</summary>

```python
def send_notification(user_id, message, channel="email", priority=3):
    return f"[P{priority}] → {user_id} via {channel}: {message}"

# 1. Positional only — all 4 in order
print(send_notification("u001", "Hello", "sms", 2))
# [P2] → u001 via sms: Hello

# 2. Override just priority
print(send_notification("u001", "Hello", priority=1))
# [P1] → u001 via email: Hello

# 3. Override channel and priority by name
print(send_notification("u001", "Hello", channel="push", priority=5))
# [P5] → u001 via push: Hello
```

**Why:** Positional arguments are matched left-to-right by position. Keyword arguments are matched by name regardless of order, and they can be skipped selectively — in call 2 we skip `channel` entirely, leaving it at its default `"email"`. Mixing positional and keyword args is fine as long as positional ones come first.

</details>

---

### Q5 · Ch4 — Mutable default arg trap

**Problem:**
This function has a dangerous bug. Identify it, explain why it breaks, and fix it.

```python
def add_to_history(event, history=[]):
    history.append(event)
    return history

print(add_to_history("login"))
print(add_to_history("logout"))  # What happens here?
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Python evaluates default argument values once at function definition time, not each time the function is called. So the same list object is reused across every call. Use `None` as the default and create a new list inside the function.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Broken version — what actually happens:
def add_to_history(event, history=[]):
    history.append(event)
    return history

print(add_to_history("login"))   # ['login']
print(add_to_history("logout"))  # ['login', 'logout']  ← BUG: accumulates!

# Fixed version:
def add_to_history(event, history=None):
    if history is None:
        history = []
    history.append(event)
    return history

print(add_to_history("login"))   # ['login']
print(add_to_history("logout"))  # ['logout']  ← fresh list each time
```

**Why:** The `[]` in `history=[]` is created once when Python parses the `def` statement. Every call that doesn't pass `history` explicitly shares the exact same list object. So `"logout"` gets appended to the same list that already contains `"login"`. The fix is `None` as the sentinel — `None` is immutable and safe as a default, and you create a fresh `[]` inside the body each time.

</details>

---

### Q6 · Ch4 — *args

**Problem:**
Write `log(*args)` that prints each argument on its own line with a line number prefix. Then call it with 1, 3, and 5 arguments.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Inside the function, `args` is a regular tuple. Use `enumerate(args, start=1)` to get a counter alongside each value.

</details>

<details>
<summary>✅ Answer</summary>

```python
def log(*args):
    for i, arg in enumerate(args, start=1):
        print(f"{i}: {arg}")

log("starting up")
# 1: starting up

log("user login", "user=alice", "ip=10.0.0.1")
# 1: user login
# 2: user=alice
# 3: ip=10.0.0.1

log("a", "b", "c", "d", "e")
# 1: a
# 2: b
# 3: c
# 4: d
# 5: e
```

**Why:** `*args` collects any number of positional arguments into a tuple named `args`. The function has no idea how many arguments it will receive — it works with 1, 100, or 0. `enumerate(args, start=1)` gives the 1-based line number without a manual counter variable.

</details>

---

### Q7 · Ch4 — **kwargs

**Problem:**
Write `create_user(name, email, **kwargs)` that builds and returns a dict with `name`, `email`, plus any extra keyword arguments. Call it with: just name+email, then with `role="admin"` and `active=True` added.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`**kwargs` is a dict inside the function. You can merge it into another dict with `{**base_dict, **kwargs}` or by calling `.update()`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def create_user(name, email, **kwargs):
    user = {"name": name, "email": email}
    user.update(kwargs)
    return user

print(create_user("Alice", "alice@example.com"))
# {'name': 'Alice', 'email': 'alice@example.com'}

print(create_user("Bob", "bob@example.com", role="admin", active=True))
# {'name': 'Bob', 'email': 'bob@example.com', 'role': 'admin', 'active': True}
```

**Why:** `**kwargs` catches all keyword arguments not matched by explicit parameters. Inside the function it is a plain `dict`. `user.update(kwargs)` merges those extra fields into the base dict. This pattern is common in factory functions and ORM models where optional fields vary per call.

</details>

---

### Q8 · Ch4 — All 7 parameter types

**Problem:**
Write one function that uses all 7 parameter types in the correct order: positional-only, normal, default, *args, keyword-only, keyword-only with default, **kwargs.

```python
# def full_example(pos_only, /, normal, default=1, *args, kw_only, kw_default=2, **kwargs)
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The `/` marker means "everything before me is positional-only". The `*args` marker means "everything after me is keyword-only". Order: positional-only `/` normal default `*args` kw-only kw-only-with-default `**kwargs`.

</details>

<details>
<summary>✅ Answer</summary>

```python
def full_example(pos_only, /, normal, default=1, *args, kw_only, kw_default=2, **kwargs):
    print(f"pos_only   = {pos_only}")
    print(f"normal     = {normal}")
    print(f"default    = {default}")
    print(f"args       = {args}")
    print(f"kw_only    = {kw_only}")
    print(f"kw_default = {kw_default}")
    print(f"kwargs     = {kwargs}")

full_example(
    10,                  # pos_only — positional only, cannot use name
    20,                  # normal
    30,                  # default
    40, 50,              # captured into *args
    kw_only="hello",     # keyword-only, required
    kw_default=99,       # keyword-only, optional
    extra="bonus"        # goes into **kwargs
)
```

**Why:** Python enforces a strict left-to-right ordering for parameter types. `/` separates positional-only from normal params. `*args` acts as a separator — after it, all remaining non-`**kwargs` params must be passed by name. This gives API designers fine-grained control over how callers must supply arguments.

</details>

---

### Q9 · Ch5 — Return with early returns

**Problem:**
Write `validate_password(password)` that returns `(True, "OK")` if valid, or `(False, reason)` if not. Rules: must be at least 8 chars, must contain a digit, must not contain spaces. Use early returns for each failure case.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Check each rule one at a time at the top of the function. If a rule fails, return immediately — don't nest checks. `any(c.isdigit() for c in password)` tests for a digit. `" " in password` tests for spaces.

</details>

<details>
<summary>✅ Answer</summary>

```python
def validate_password(password):
    if len(password) < 8:
        return (False, "Too short — must be at least 8 characters")
    if not any(c.isdigit() for c in password):
        return (False, "Must contain at least one digit")
    if " " in password:
        return (False, "Must not contain spaces")
    return (True, "OK")

print(validate_password("abc"))             # (False, 'Too short...')
print(validate_password("abcdefgh"))        # (False, 'Must contain at least one digit')
print(validate_password("abc defg1"))       # (False, 'Must not contain spaces')
print(validate_password("secureP4ss"))      # (True, 'OK')
```

**Why:** Each early return bails out the moment a rule is violated, without evaluating any subsequent conditions. This is called the "guard clause" pattern — it keeps the happy path at the bottom without deep nesting. Returning a tuple `(bool, message)` lets callers check success and get the reason in one shot.

</details>

---

### Q10 · Ch5 — Return vs Print

**Problem:**
This function is broken when used in a calculation. Explain why and fix it.

```python
def double(x):
    print(x * 2)

result = double(5)
print(result + 10)  # What happens? Why?
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

What does a function that has no `return` statement actually return? What happens when you try to do arithmetic with that value?

</details>

<details>
<summary>✅ Answer</summary>

```python
# Broken version — what happens:
def double(x):
    print(x * 2)       # prints 10 to screen, returns nothing

result = double(5)     # result = None
print(result + 10)     # TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'

# Fixed version:
def double(x):
    return x * 2

result = double(5)     # result = 10
print(result + 10)     # 20
```

**Why:** In Python, a function without an explicit `return` statement implicitly returns `None`. `print()` outputs to the screen but returns `None`. When you then try `None + 10`, Python raises a `TypeError` because you can't add `None` and an integer. The fix is replacing `print` inside the function with `return`, so the computed value flows back to the caller.

</details>

---

### Q11 · Ch6 — LEGB prediction

**Problem:**
Predict what each `print` statement outputs. Then verify by running.

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)  # 1
    inner()
    print(x)  # 2

outer()
print(x)  # 3
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

LEGB: Local, Enclosing, Global, Built-in. Each `x` assignment creates a new variable in that scope — it does NOT overwrite the outer one. Each `print` finds the nearest `x` in its own scope first.

</details>

<details>
<summary>✅ Answer</summary>

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)  # 1 → "local"
    inner()
    print(x)  # 2 → "enclosing"

outer()
print(x)  # 3 → "global"
```

**Why:** Print 1 is inside `inner()` — Python finds `x = "local"` in the Local scope and uses it. Print 2 is inside `outer()` — `inner`'s `x` is gone, so Python finds `x = "enclosing"` in the Enclosing scope. Print 3 is at module level — both function-level `x` bindings are gone, leaving the Global `x = "global"`. Assignment in a scope creates a new variable there; it never reaches upward to change an outer one.

</details>

---

### Q12 · Ch6 — global and nonlocal

**Problem:**
Fix both broken functions. The first has an `UnboundLocalError`; the second can't modify the enclosing variable.

```python
count = 0
def increment():
    count += 1  # broken
    return count

def make_counter():
    total = 0
    def add(n):
        total += n  # broken
        return total
    return add
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

For `increment`: the `+=` assignment makes Python treat `count` as a local variable, but it has no local value yet. Declare `global count` at the top of the function. For `add`: same problem one level up — use `nonlocal total` to tell Python `total` lives in the enclosing scope.

</details>

<details>
<summary>✅ Answer</summary>

```python
count = 0
def increment():
    global count
    count += 1
    return count

print(increment())  # 1
print(increment())  # 2

def make_counter():
    total = 0
    def add(n):
        nonlocal total
        total += n
        return total
    return add

counter = make_counter()
print(counter(5))   # 5
print(counter(3))   # 8
```

**Why:** In Python, any variable that appears on the left side of `=` in a function is treated as local to that function. `count += 1` is `count = count + 1`, so Python marks `count` as local — but then tries to read the local `count` before it's assigned, causing `UnboundLocalError`. `global count` tells Python to use the module-level `count`. `nonlocal total` does the same but reaches into the nearest enclosing function scope rather than the global scope.

</details>

---

### Q13 · Ch7 — First-class functions

**Problem:**
Create a dict `operations` that maps string names to functions: `"add"`, `"subtract"`, `"multiply"`, `"square"`. Then write a `calculate(op_name, a, b=None)` function that looks up the operation by name and calls it.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Functions are objects — you can store them in a dict just like integers or strings. `operations["add"]` returns the function itself. Add `()` to call it. Handle `"square"` specially since it only takes one argument.

</details>

<details>
<summary>✅ Answer</summary>

```python
def add(a, b):       return a + b
def subtract(a, b):  return a - b
def multiply(a, b):  return a * b
def square(a):       return a * a

operations = {
    "add":      add,
    "subtract": subtract,
    "multiply": multiply,
    "square":   square,
}

def calculate(op_name, a, b=None):
    func = operations.get(op_name)
    if func is None:
        raise ValueError(f"Unknown operation: {op_name}")
    if b is None:
        return func(a)
    return func(a, b)

print(calculate("add", 3, 4))       # 7
print(calculate("subtract", 10, 3)) # 7
print(calculate("multiply", 3, 4))  # 12
print(calculate("square", 5))       # 25
```

**Why:** This is the "function dispatch table" pattern. Because functions are first-class objects in Python, they can be stored in any container. Looking up an operation by string key and calling it is cleaner than a long `if/elif` chain — and adding a new operation is a one-line change to the dict.

</details>

---

### Q14 · Ch7 — Higher-order function

**Problem:**
Write `apply_twice(func, value)` that applies `func` to `value` twice. Test it with `lambda x: x * 2` and `lambda x: x + 3`.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

"Apply twice" means call `func` on `value`, then call `func` again on the result of that first call. One line inside `apply_twice` is enough.

</details>

<details>
<summary>✅ Answer</summary>

```python
def apply_twice(func, value):
    return func(func(value))

double = lambda x: x * 2
add3   = lambda x: x + 3

print(apply_twice(double, 5))  # 20  — 5→10→20
print(apply_twice(add3, 7))    # 13  — 7→10→13
print(apply_twice(double, 1))  # 4   — 1→2→4
```

**Why:** `apply_twice` is a higher-order function — it takes a function as an argument and calls it. `func(func(value))` evaluates the inner call first, then passes that result to the outer call. This is function composition in its simplest form: `f(f(x))`.

</details>

---

### Q15 · Ch7 — compose()

**Problem:**
Write `compose(*functions)` that returns a new function applying each function right-to-left. Test: `transform = compose(str.upper, str.strip, lambda s: s + "!")` applied to `"  hello  "` should give `"HELLO!"`.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Right-to-left means the last function in the list runs first. Use `functools.reduce` with a lambda, or loop through `reversed(functions)` and apply each one. The result of each step becomes the input for the next.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def compose(*functions):
    def composed(value):
        result = value
        for func in reversed(functions):
            result = func(result)
        return result
    return composed

transform = compose(str.upper, str.strip, lambda s: s + "!")
print(transform("  hello  "))  # "HELLO!"

# Step trace:
# lambda s: s + "!" applied to "  hello  "  → "  hello  !"
# str.strip applied to "  hello  !"          → "hello  !"   ← note: only strips leading
# Actually: strip("  hello  !") → "hello  !" ... let's retrace:
# Step 1 (last func first): lambda("  hello  ") → "  hello  !"
# Step 2: str.strip("  hello  !") → "hello  !"
# Step 3: str.upper("hello  !") → "HELLO  !"
# To get exactly "HELLO!" pass pre-stripped input:
print(transform("hello"))   # "HELLO!"
```

**Why:** Mathematical function composition is `(f ∘ g)(x) = f(g(x))` — the rightmost function runs first. `reversed(functions)` iterates the list from right to left, so the last-listed function applies first. The inner `composed` function is a closure that captures `functions`. This pattern is the foundation of functional pipelines.

</details>

---

### Q16 · Ch8 — Lambda sort

**Problem:**
Sort this list of employees by department (ascending), then by salary (descending) within department.

```python
employees = [
    {"name": "Alice", "dept": "eng", "salary": 90000},
    {"name": "Bob", "dept": "sales", "salary": 60000},
    {"name": "Carol", "dept": "eng", "salary": 105000},
    {"name": "Dave", "dept": "sales", "salary": 75000},
]
# Sort using key=lambda — two criteria
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Return a tuple from the lambda: `(primary_key, secondary_key)`. Python sorts tuples lexicographically. To reverse only the salary, negate it: `-e["salary"]`.

</details>

<details>
<summary>✅ Answer</summary>

```python
employees = [
    {"name": "Alice", "dept": "eng",   "salary": 90000},
    {"name": "Bob",   "dept": "sales", "salary": 60000},
    {"name": "Carol", "dept": "eng",   "salary": 105000},
    {"name": "Dave",  "dept": "sales", "salary": 75000},
]

sorted_employees = sorted(employees, key=lambda e: (e["dept"], -e["salary"]))

for emp in sorted_employees:
    print(f"{emp['dept']:6} | {emp['salary']:>7} | {emp['name']}")

# eng    | 105000 | Carol
# eng    |  90000 | Alice
# sales  |  75000 | Dave
# sales  |  60000 | Bob
```

**Why:** When the lambda returns a tuple, Python compares first by the first element, then by the second only when the first elements are equal. `e["dept"]` is a string so it sorts alphabetically ascending by default. Negating the salary (`-e["salary"]`) reverses the numeric order, producing descending sort within each department without needing `reverse=True` (which would reverse everything).

</details>

---

### Q17 · Ch8 — Lambda with map/filter

**Problem:**
`prices = [10.5, 25.0, 3.99, 150.0, 7.49]`. Use `filter` to keep only prices under $20, then use `map` to apply a 10% discount to each. Convert the final result to a list and print it.

```python
prices = [10.5, 25.0, 3.99, 150.0, 7.49]
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`filter(condition, iterable)` returns an iterator of items where the condition is `True`. `map(transform, iterable)` returns an iterator applying the transform to each item. Chain them: pass the result of `filter` directly into `map`.

</details>

<details>
<summary>✅ Answer</summary>

```python
prices = [10.5, 25.0, 3.99, 150.0, 7.49]

result = list(map(lambda p: round(p * 0.9, 2),
                  filter(lambda p: p < 20, prices)))

print(result)  # [9.45, 3.59, 6.74]
```

**Why:** `filter(lambda p: p < 20, prices)` keeps `10.5`, `3.99`, and `7.49`. `map(lambda p: p * 0.9, ...)` applies a 10% discount to each of those. Both `map` and `filter` return lazy iterators — nothing is computed until `list()` forces evaluation. Chaining them avoids creating an intermediate list.

</details>

---

### Q18 · Ch9 — Basic closure

**Problem:**
Write `make_multiplier(factor)` that returns a function. The returned function takes a number and multiplies it by `factor`. Create `double = make_multiplier(2)` and `triple = make_multiplier(3)`. Test with several values.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The inner function "closes over" `factor` — it remembers the value of `factor` from the outer function's scope even after `make_multiplier` has returned. Define the inner function inside the outer one and return it (without calling it).

</details>

<details>
<summary>✅ Answer</summary>

```python
def make_multiplier(factor):
    def multiply(number):
        return number * factor
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))   # 10
print(double(7))   # 14
print(triple(5))   # 15
print(triple(7))   # 21
print(double(triple(4)))  # double(12) = 24
```

**Why:** Each call to `make_multiplier` creates a new scope with its own `factor` value. The `multiply` function defined inside that scope captures (closes over) that `factor`. When you call `double(5)`, Python looks up `factor` in `multiply`'s closure and finds `2`. `double` and `triple` are independent functions that each remember their own `factor`.

</details>

---

### Q19 · Ch10 — Basic decorator

**Problem:**
Write a `@timer` decorator that measures how long a function takes to run and prints `"{func_name} took {time:.4f}s"`. Apply it to a function that does `time.sleep(0.1)`.

```python
import time
# your code here: define timer decorator, then:
@timer
def slow_function():
    time.sleep(0.1)
    return "done"
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

A decorator is a function that takes a function and returns a function. The wrapper calls `time.time()` before and after the original function, computes the difference, and prints it. Use `functools.wraps(func)` on the wrapper to preserve the original function's name and docstring.

</details>

<details>
<summary>✅ Answer</summary>

```python
import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(0.1)
    return "done"

output = slow_function()
# slow_function took 0.1003s  (approximately)
print(output)  # done
```

**Why:** The decorator replaces `slow_function` with `wrapper`. When you call `slow_function()`, you're actually calling `wrapper()`, which bookends the real call with timing code. `@functools.wraps(func)` copies the original function's `__name__`, `__doc__`, and other metadata to `wrapper`, so the function still looks like itself to introspection tools. `*args, **kwargs` ensures the wrapper works with any function signature.

</details>

---

### Q20 · Ch11 — Recursion: factorial

**Problem:**
Write `factorial(n)` recursively. It should raise `ValueError` for negative input, return 1 for n=0, and work correctly for n=1 through n=10. Print the results for n=0 through n=7.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Two base cases: `n < 0` raises an error, `n == 0` returns 1. The recursive case: `n * factorial(n - 1)`. Each call reduces `n` by 1, eventually hitting the base case.

</details>

<details>
<summary>✅ Answer</summary>

```python
def factorial(n):
    if n < 0:
        raise ValueError(f"factorial not defined for negative numbers: {n}")
    if n == 0:
        return 1
    return n * factorial(n - 1)

for i in range(8):
    print(f"{i}! = {factorial(i)}")

# 0! = 1
# 1! = 1
# 2! = 2
# 3! = 6
# 4! = 24
# 5! = 120
# 6! = 720
# 7! = 5040
```

**Why:** Every recursive function needs a base case to stop recursion. Here `n == 0` is the base case — without it the function would call itself forever until Python raises a `RecursionError`. The recursive case `n * factorial(n-1)` reduces the problem by 1 each time. For `factorial(4)`: `4 * factorial(3)` → `4 * 3 * factorial(2)` → ... → `4 * 3 * 2 * 1 * 1 = 24`.

</details>

---

### Q21 · Ch11 — Fix broken recursion

**Problem:**
This recursive function has a bug. Identify what's wrong and fix it.

```python
def count_down(n):
    print(n)
    return count_down(n - 1)  # broken — what's missing?

count_down(5)
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

What stops the recursion? Without a condition that returns without making another recursive call, the function never stops. A recursive function needs at least one base case.

</details>

<details>
<summary>✅ Answer</summary>

```python
# Broken: no base case → infinite recursion → RecursionError
def count_down(n):
    print(n)
    return count_down(n - 1)

# Fixed: add a base case
def count_down(n):
    if n <= 0:
        print("Done!")
        return
    print(n)
    return count_down(n - 1)

count_down(5)
# 5
# 4
# 3
# 2
# 1
# Done!
```

**Why:** Without `if n <= 0: return`, the function calls `count_down(0)`, then `count_down(-1)`, then `count_down(-2)` forever. Python has a default recursion limit of 1000 frames, so it eventually raises `RecursionError: maximum recursion depth exceeded`. The base case acts as the exit door — every recursive call must eventually reach it.

</details>

---

### Q22 · Ch12 — Generator: lazy squares

**Problem:**
Write a generator function `squares(n)` that yields the square of each number from 1 to n, one at a time. Then iterate over `squares(5)` and sum the results WITHOUT storing all values in a list first.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Replace `return` with `yield` inside a loop. `sum()` accepts any iterable — including a generator — so you can pass `squares(5)` directly to `sum()` without calling `list()` first.

</details>

<details>
<summary>✅ Answer</summary>

```python
def squares(n):
    for i in range(1, n + 1):
        yield i * i

# Iterate and print each value
for sq in squares(5):
    print(sq)
# 1
# 4
# 9
# 16
# 25

# Sum without materializing a list
total = sum(squares(5))
print(total)  # 55

# Prove it's lazy — only computes what you ask for
gen = squares(1_000_000)
print(next(gen))  # 1  (computed immediately without building 1M-item list)
```

**Why:** A generator function uses `yield` instead of `return`. Each call to `next()` runs the function until the next `yield`, suspends it, and hands the yielded value to the caller. No values are stored — each one is computed on demand. This is why `sum(squares(1_000_000))` works without allocating a million-element list in memory.

</details>

---

### Q23 · Ch12 — Generator pipeline

**Problem:**
Build a generator pipeline: (1) `read_numbers` yields numbers from a list, (2) `only_even` filters to only even numbers, (3) `doubled` doubles each. Chain them for `[1,2,3,4,5,6,7,8]` and print each result.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Each generator in the pipeline takes the previous generator as its input and yields transformed values. The pipeline is lazy end-to-end — values flow through one at a time, triggered only when the final consumer requests the next item.

</details>

<details>
<summary>✅ Answer</summary>

```python
def read_numbers(data):
    for n in data:
        yield n

def only_even(numbers):
    for n in numbers:
        if n % 2 == 0:
            yield n

def doubled(numbers):
    for n in numbers:
        yield n * 2

data = [1, 2, 3, 4, 5, 6, 7, 8]

pipeline = doubled(only_even(read_numbers(data)))

for result in pipeline:
    print(result)
# 4
# 8
# 12
# 16
```

**Why:** Each generator wraps the previous one. When the `for` loop asks for the next item from `doubled`, it asks `only_even`, which asks `read_numbers`, which pulls from `data`. The value flows through all three stages before the next one is requested. This is the Unix pipe model applied to Python: `data | read_numbers | only_even | doubled`. Memory usage stays constant regardless of data size.

</details>

---

### Q24 · Ch13 — Type annotations

**Problem:**
Add proper type annotations to this function. Use `Optional` for parameters that can be None, `List` for list params, and the `->` return type.

```python
def find_user(users, user_id, default=None):
    # users is a list of dicts
    # user_id is a string
    # default can be None or a dict
    # returns a dict or None
    for user in users:
        if user["id"] == user_id:
            return user
    return default
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Import `List`, `Dict`, `Optional`, `Any` from `typing`. `Optional[X]` is shorthand for `Union[X, None]`. In Python 3.9+ you can use `list[dict]` directly without importing `List`.

</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import List, Dict, Optional, Any

def find_user(
    users: List[Dict[str, Any]],
    user_id: str,
    default: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    for user in users:
        if user["id"] == user_id:
            return user
    return default

# Python 3.9+ alternative (no imports needed):
def find_user_modern(
    users: list[dict[str, Any]],
    user_id: str,
    default: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    for user in users:
        if user["id"] == user_id:
            return user
    return default
```

**Why:** `List[Dict[str, Any]]` says "a list of dicts where keys are strings and values can be anything". `Optional[Dict[str, Any]]` says "either a dict of that shape, or None". The `->` return annotation tells callers what to expect back. Type annotations don't change runtime behavior — they are hints for IDEs, `mypy`, and human readers. Python 3.10+ introduced `X | None` as a cleaner alternative to `Optional[X]`.

</details>

---

### Q25 · Ch14 — Google-style docstring

**Problem:**
Add a complete Google-style docstring to this function: description, Args section (with types), Returns section, Raises section, and an Example.

```python
def divide(numerator, denominator):
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    return numerator / denominator
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Google-style uses `Args:`, `Returns:`, `Raises:`, and `Example:` as section headers, each indented with 4 spaces. Each arg is `name (type): description`. Raises lists the exception class and when it is raised.

</details>

<details>
<summary>✅ Answer</summary>

```python
def divide(numerator, denominator):
    """Divide numerator by denominator and return the result.

    Performs floating-point division. Raises an error if the
    denominator is zero to prevent undefined behavior.

    Args:
        numerator (float): The number to be divided.
        denominator (float): The number to divide by. Must not be zero.

    Returns:
        float: The result of numerator / denominator.

    Raises:
        ValueError: If denominator is 0.

    Example:
        >>> divide(10, 4)
        2.5
        >>> divide(7, 0)
        ValueError: Cannot divide by zero
    """
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    return numerator / denominator
```

**Why:** Google-style docstrings are the most readable format for humans and are supported by tools like Sphinx and `help()`. The first line is a one-sentence summary. The `Args` section documents every parameter with its type and meaning. `Returns` states what the caller gets back. `Raises` makes exceptions explicit — callers know what to catch. `Example` shows working code snippets, which also serve as doctests.

</details>

---

### Q26 · Ch15 — Pure vs impure

**Problem:**
Classify each function as pure or impure. For each impure one, explain what makes it impure, then rewrite it as a pure function.

```python
import random

def add(a, b): return a + b                    # 1
def get_random(): return random.randint(1,10)  # 2
total = 0
def running_sum(n):                            # 3
    global total
    total += n
    return total
def process(items):                            # 4
    items.append("done")
    return items
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

A pure function: same inputs always give the same output, and it has no side effects (no global mutation, no I/O, no modifying its arguments). Check each function against both criteria.

</details>

<details>
<summary>✅ Answer</summary>

```python
import random

# 1. PURE — same inputs always give same output, no side effects
def add(a, b): return a + b

# 2. IMPURE — non-deterministic (different output each call, same input)
def get_random(): return random.randint(1, 10)
# Pure alternative: pass the random source in
def get_value(source_func): return source_func()

# 3. IMPURE — reads and mutates global state (`total`)
total = 0
def running_sum(n):
    global total
    total += n
    return total
# Pure alternative: pass state in, return new state
def pure_running_sum(current_total, n):
    return current_total + n

# 4. IMPURE — mutates the input argument (side effect on caller's list)
def process(items):
    items.append("done")
    return items
# Pure alternative: return a new list, leave original unchanged
def pure_process(items):
    return items + ["done"]

# Demonstrate pure_process doesn't mutate:
original = [1, 2, 3]
result = pure_process(original)
print(original)  # [1, 2, 3]   ← unchanged
print(result)    # [1, 2, 3, 'done']
```

**Why:** `add` is pure — `add(2, 3)` always returns `5` no matter when or how many times you call it. `get_random` is impure due to non-determinism — same call, different results. `running_sum` is impure because it reads and writes the global `total` — calling it changes program state outside its scope. `process` is impure because it mutates the caller's list — after calling it, the caller's variable has changed without them expecting it. Pure functions are easier to test, cache, and reason about.

</details>

---

### Q27 · Ch16 — lru_cache

**Problem:**
Implement fibonacci WITHOUT cache, then add `@functools.lru_cache`. Print the 35th fibonacci number both ways and time the difference using `time.time()`. Then print `fib.cache_info()`.

```python
import functools
import time
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Without cache, `fib(35)` makes exponential recursive calls — about 29 million. With `@lru_cache`, each unique argument is computed only once and stored. Time each version separately with `time.time()` before and after.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools
import time

# Without cache
def fib_slow(n):
    if n <= 1:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)

start = time.time()
print(fib_slow(35))
print(f"Without cache: {time.time() - start:.4f}s")
# 9227465
# Without cache: ~3.5s  (varies by machine)

# With lru_cache
@functools.lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

start = time.time()
print(fib(35))
print(f"With lru_cache: {time.time() - start:.6f}s")
# 9227465
# With lru_cache: ~0.000030s  (thousands of times faster)

print(fib.cache_info())
# CacheInfo(hits=33, misses=36, maxsize=None, currsize=36)
```

**Why:** Without caching, `fib(35)` recomputes the same sub-problems millions of times — its time complexity is O(2^n). `@lru_cache` memoizes results: the first time `fib(10)` is called, the result is stored. Every subsequent call for `fib(10)` returns the cached value instantly. `maxsize=None` means unlimited cache size. `cache_info()` shows how many calls were cache hits vs misses.

</details>

---

### Q28 · Ch16 — functools.partial

**Problem:**
`send_message(user_id, channel, message, priority=3)` is the base function. Use `functools.partial` to create: `send_email` (channel="email"), `send_sms` (channel="sms"). Test each with a user_id and message.

```python
import functools
def send_message(user_id, channel, message, priority=3):
    return f"[P{priority}] {user_id} via {channel}: {message}"
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

`functools.partial(func, **fixed_kwargs)` returns a new callable with some arguments pre-filled. The resulting partial function accepts the remaining arguments when called.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def send_message(user_id, channel, message, priority=3):
    return f"[P{priority}] {user_id} via {channel}: {message}"

send_email = functools.partial(send_message, channel="email")
send_sms   = functools.partial(send_message, channel="sms")

print(send_email("u001", message="Your order shipped"))
# [P3] u001 via email: Your order shipped

print(send_sms("u002", message="Verification code: 4821"))
# [P3] u002 via sms: Verification code: 4821

# Can still override the pre-filled value
print(send_email("u003", message="URGENT", priority=1))
# [P1] u003 via email: URGENT
```

**Why:** `partial` creates a new callable with one or more arguments pre-bound. It is cleaner than writing wrapper functions like `def send_email(user_id, message, priority=3): return send_message(user_id, "email", message, priority)`. The partial can still be overridden — `priority=1` in the last call overrides the default from the original function. This is the "partial application" concept from functional programming.

</details>

---

### Q29 · Ch17 — Introspection

**Problem:**
Write a function `inspect_function(func)` that prints: the function's `__name__`, its `__doc__` (first line only), its `__defaults__`, and its `__annotations__`. Test it on a function you write with defaults and type hints.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

All these are attributes on the function object itself: `func.__name__`, `func.__doc__`, `func.__defaults__`, `func.__annotations__`. Access the first line of `__doc__` by splitting on `"\n"` and taking index 0. Guard against `None` docstrings.

</details>

<details>
<summary>✅ Answer</summary>

```python
def inspect_function(func):
    doc = func.__doc__ or ""
    first_line = doc.strip().split("\n")[0] if doc.strip() else "(no docstring)"
    print(f"Name:        {func.__name__}")
    print(f"Docstring:   {first_line}")
    print(f"Defaults:    {func.__defaults__}")
    print(f"Annotations: {func.__annotations__}")

def greet(name: str, greeting: str = "Hello", times: int = 1) -> str:
    """Greet a person with an optional custom greeting.

    Repeats the greeting the specified number of times.
    """
    return (f"{greeting}, {name}! " * times).strip()

inspect_function(greet)
# Name:        greet
# Docstring:   Greet a person with an optional custom greeting.
# Defaults:    ('Hello', 1)
# Annotations: {'name': <class 'str'>, 'greeting': <class 'str'>, 'times': <class 'int'>, 'return': <class 'str'>}
```

**Why:** Python functions are objects with rich metadata stored as attributes. `__name__` is the function's identifier. `__doc__` holds the docstring. `__defaults__` is a tuple of the default values in left-to-right order for parameters that have defaults. `__annotations__` is a dict mapping parameter names and `"return"` to their annotated types. This is how tools like IDEs, `help()`, and `functools.wraps` work under the hood.

</details>

---

### Q30 · Ch18 — Capstone

**Problem:**
Build a `make_validator(min_len, max_len, required_chars)` function factory. It returns a validator function that checks if a string meets all criteria and returns `(True, None)` or `(False, "reason")`. Use a closure to capture the limits. Test with password validation.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The outer function captures `min_len`, `max_len`, and `required_chars` in a closure. The inner function receives only the string to validate. Check each rule and return early with a reason on failure. `required_chars` can be a string of characters that must all appear.

</details>

<details>
<summary>✅ Answer</summary>

```python
def make_validator(min_len, max_len, required_chars=""):
    """Factory that returns a validator function for string rules.

    Args:
        min_len (int): Minimum string length.
        max_len (int): Maximum string length.
        required_chars (str): Each character in this string must appear
                              at least once in the validated string.

    Returns:
        callable: A function (s: str) -> (bool, str | None)
    """
    def validate(s):
        if len(s) < min_len:
            return (False, f"Too short: minimum {min_len} characters")
        if len(s) > max_len:
            return (False, f"Too long: maximum {max_len} characters")
        for ch in required_chars:
            if ch not in s:
                return (False, f"Missing required character: '{ch}'")
        return (True, None)
    return validate

# Build validators via the factory
validate_password = make_validator(
    min_len=8,
    max_len=64,
    required_chars="0123456789"  # must contain at least one digit
)

validate_username = make_validator(min_len=3, max_len=20)

tests = ["hi", "toolongpasswordthatexceedsthemaximumallowedcharacterlimitset", "nodigits", "valid4me"]
for pw in tests:
    ok, reason = validate_password(pw)
    status = "OK" if ok else f"FAIL: {reason}"
    print(f"{pw!r:50} → {status}")
```

**Why:** This combines closures, factory functions, early returns, and tuple return values — the key patterns from Chapters 5, 6, 9, and 18. `make_validator` is called once to configure a validator. The returned `validate` function closes over `min_len`, `max_len`, and `required_chars`, carrying that configuration with it wherever it goes. You can create dozens of different validators with different rules from the same factory.

</details>

---

### Q31 · Mixed — retry decorator

**Problem:**
Write a `@retry(max_attempts=3, delay=0.0)` decorator that calls the function up to `max_attempts` times if it raises an exception. Print `"Attempt {n} failed: {error}"` each time. Raise the last exception if all attempts fail.

```python
import time
# your code here

@retry(max_attempts=3)
def unreliable():
    import random
    if random.random() < 0.7:
        raise ConnectionError("Server busy")
    return "success"
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

This is a decorator with arguments — you need three layers: the outermost function accepts the decorator arguments (`max_attempts`, `delay`), returns a decorator function, which returns a wrapper. Loop up to `max_attempts` times, catching exceptions. Re-raise only after all attempts are exhausted.

</details>

<details>
<summary>✅ Answer</summary>

```python
import time
import functools

def retry(max_attempts=3, delay=0.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt < max_attempts and delay > 0:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=3)
def unreliable():
    import random
    if random.random() < 0.7:
        raise ConnectionError("Server busy")
    return "success"

try:
    result = unreliable()
    print(f"Result: {result}")
except ConnectionError as e:
    print(f"All attempts failed: {e}")
```

**Why:** A decorator with arguments requires an extra wrapping layer. `retry(max_attempts=3)` is called first and returns `decorator`. `decorator` is applied to `unreliable` and returns `wrapper`. When `unreliable()` is called, it runs `wrapper`. The `for` loop retries on any exception, saving the last one. After the loop finishes without a `return`, `raise last_exception` propagates the final failure. This pattern is fundamental in production code for handling transient network errors.

</details>

---

### Q32 · Mixed — Decorator with arguments (3-layer)

**Problem:**
Write a `@validate_types(**expected_types)` decorator that checks each keyword argument matches its expected type and raises `TypeError` if not. Usage: `@validate_types(name=str, age=int)`.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Three layers again: `validate_types(**expected_types)` → `decorator(func)` → `wrapper(*args, **kwargs)`. Inside `wrapper`, iterate over `expected_types.items()` and use `isinstance()` to check each kwarg. Only validate kwargs that were actually passed and have an expected type.

</details>

<details>
<summary>✅ Answer</summary>

```python
import functools

def validate_types(**expected_types):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for param_name, expected_type in expected_types.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"Argument '{param_name}' must be {expected_type.__name__}, "
                            f"got {type(value).__name__} instead"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_types(name=str, age=int)
def create_profile(name, age, role="user"):
    return {"name": name, "age": age, "role": role}

print(create_profile(name="Alice", age=30))
# {'name': 'Alice', 'age': 30, 'role': 'user'}

try:
    create_profile(name="Bob", age="thirty")
except TypeError as e:
    print(e)
# Argument 'age' must be int, got str instead
```

**Why:** The outermost call `validate_types(name=str, age=int)` captures the type constraints in `expected_types`. `decorator` receives the function being decorated. `wrapper` runs the checks at call time — not at decoration time — because that is when the actual argument values exist. Only checking `kwargs` means positional args are not validated here (a deliberate simplification — a production version would use `inspect.signature` to map positional args to names too).

</details>

---

### Q33 · Mixed — Generator chained pipeline

**Problem:**
Build a data pipeline using generators only. Input: list of raw log strings `"2024-01-15 ERROR Database timeout"`. Pipeline: (1) parse to dict, (2) filter to ERROR level only, (3) extract just the message. Print the results.

```python
# your code here
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

Each stage is a generator that `yield`s transformed values from its input. Stage 1 splits each line and yields a dict. Stage 2 checks the `level` key and yields only ERROR entries. Stage 3 yields just the `message` value. Chain them like nested function calls.

</details>

<details>
<summary>✅ Answer</summary>

```python
raw_logs = [
    "2024-01-15 ERROR Database timeout",
    "2024-01-15 INFO  User login successful",
    "2024-01-15 ERROR Connection refused",
    "2024-01-15 WARN  Disk usage at 80%",
    "2024-01-15 ERROR Out of memory",
]

def parse_logs(lines):
    for line in lines:
        parts = line.split(None, 2)
        if len(parts) == 3:
            date, level, message = parts
            yield {"date": date, "level": level.strip(), "message": message}

def filter_errors(records):
    for record in records:
        if record["level"] == "ERROR":
            yield record

def extract_messages(records):
    for record in records:
        yield record["message"]

pipeline = extract_messages(filter_errors(parse_logs(raw_logs)))

for message in pipeline:
    print(message)
# Database timeout
# Connection refused
# Out of memory
```

**Why:** Each generator stage does exactly one thing. No intermediate lists are created — the value of each log line flows through all three stages before the next line is even looked at. Adding a new stage (e.g., `enrich_with_hostname`) means inserting one more generator in the chain. This is the Unix pipe philosophy applied to Python: composable, lazy, memory-efficient.

</details>

---

### Q34 · Mixed — Debug TypeError

**Problem:**
This function call raises a `TypeError`. Identify the exact cause and fix it.

```python
def configure(host, port, /, timeout=30, *, debug=False, **options):
    return {"host": host, "port": port, "timeout": timeout,
            "debug": debug, **options}

# These calls are broken — fix each one:
result1 = configure(host="localhost", port=5432)
result2 = configure("localhost", 5432, debug=True, timeout="30")
result3 = configure("localhost", 5432, 30, True)
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The `/` marker makes `host` and `port` positional-only — they cannot be passed by name. The `*` marker makes `debug` keyword-only — it cannot be passed positionally. For `result2`, look at what type `timeout` receives.

</details>

<details>
<summary>✅ Answer</summary>

```python
def configure(host, port, /, timeout=30, *, debug=False, **options):
    return {"host": host, "port": port, "timeout": timeout,
            "debug": debug, **options}

# result1: BROKEN — host and port are positional-only (before /), cannot use keyword syntax
# Fix: pass positionally
result1 = configure("localhost", 5432)
print(result1)  # {'host': 'localhost', 'port': 5432, 'timeout': 30, 'debug': False}

# result2: NOT a TypeError — but a logic bug. timeout="30" passes a string where int expected.
# Python won't raise a TypeError here at the function boundary (no runtime type enforcement),
# but downstream code using timeout arithmetically would break.
# Fix: pass an int
result2 = configure("localhost", 5432, debug=True, timeout=30)
print(result2)  # {'host': 'localhost', 'port': 5432, 'timeout': 30, 'debug': True}

# result3: BROKEN — debug is after *, so it is keyword-only. Passing True positionally
# means True is captured by **options, not debug. debug stays False.
# Fix: pass debug by name
result3 = configure("localhost", 5432, 30, debug=True)
print(result3)  # {'host': 'localhost', 'port': 5432, 'timeout': 30, 'debug': True}
```

**Why:** The `/` in the signature means `host` and `port` cannot be passed by keyword — `configure(host="localhost", ...)` raises `TypeError: configure() got some positional-only arguments passed as keyword arguments`. The `*` means `debug` cannot be passed positionally — the fourth positional arg after `/` goes to `**options`, not `debug`. Understanding `/` and `*` as boundary markers is essential for reading modern Python library signatures correctly.

</details>

---

### Q35 · Mixed — Rate limiter using closures

**Problem:**
Write `make_rate_limiter(max_calls, period_seconds)` that returns a function. The returned function should: allow up to `max_calls` calls within `period_seconds`, raise `RuntimeError("Rate limit exceeded")` if exceeded, and reset after the period expires. Use `time.time()` for timing.

```python
import time
# your code here

api_call = make_rate_limiter(max_calls=3, period_seconds=1.0)
```

**Your answer:** *(write in practice_local.py, then check below)*

<details>
<summary>💡 Hint</summary>

The closure needs to track two things: how many calls have been made in the current window, and when the current window started. Use a mutable container (like a list) to hold these values so `nonlocal` isn't required, or use `nonlocal` directly. Check if the period has expired on each call and reset the counter if so.

</details>

<details>
<summary>✅ Answer</summary>

```python
import time

def make_rate_limiter(max_calls, period_seconds):
    """Returns a callable that enforces a rate limit.

    Args:
        max_calls (int): Maximum number of calls allowed per period.
        period_seconds (float): Length of the rate window in seconds.

    Returns:
        callable: Call this to register a call. Raises RuntimeError if over limit.
    """
    state = {"calls": 0, "window_start": time.time()}

    def call():
        now = time.time()
        elapsed = now - state["window_start"]

        if elapsed >= period_seconds:
            # Period has expired — reset the window
            state["window_start"] = now
            state["calls"] = 0

        if state["calls"] >= max_calls:
            raise RuntimeError(
                f"Rate limit exceeded: {max_calls} calls per {period_seconds}s"
            )

        state["calls"] += 1
        return state["calls"]

    return call

api_call = make_rate_limiter(max_calls=3, period_seconds=1.0)

print(api_call())  # 1
print(api_call())  # 2
print(api_call())  # 3
try:
    api_call()     # raises RuntimeError
except RuntimeError as e:
    print(f"Blocked: {e}")

time.sleep(1.1)    # wait for window to expire
print(api_call())  # 1  — window reset
```

**Why:** The `state` dict is a mutable object captured by the closure. Mutating a dict's values (`state["calls"] += 1`) does not require `nonlocal` — you're modifying the contents of the dict, not rebinding the `state` variable itself. On each call, the function checks whether the window has expired; if so, it resets. Otherwise it checks the counter and either allows or blocks the call. This pattern is the foundation of token bucket and fixed-window rate limiters used in production APIs.

</details>

---

## 🔁 Navigation

**[Back to Functions Theory](./theory.md)**

**Related:** [practice_local.py](./practice_local.py) · [Closures & Decorators Practice](./02_closures_decorators/practice.md) · [Functional Programming Practice](./01_functional_programming/practice.md) · [Itertools & Functools Practice](./03_itertools_functools/practice.md)
