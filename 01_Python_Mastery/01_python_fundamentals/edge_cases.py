"""
01_python_fundamentals/edge_cases.py
=====================================
CONCEPT: Python's surprising, tricky, and interview-famous edge cases.
WHY THIS MATTERS: These are exactly the questions that separate "knows Python
syntax" from "understands Python internals." Every senior Python interview
includes at least two of these. Know them cold.

LEARNING PATH:
  Part 1 (this module): edge cases you can explore with just variables + loops
  Part 2 (bottom):      revisit AFTER completing Module 04 (Functions)
                        — covers edge cases that require def to demonstrate

Each section shows the surprising behavior AND the reason behind it.
"""

# =============================================================================
# PART 1 — Requires only: Module 01 knowledge (no def needed)
# =============================================================================

# =============================================================================
# EDGE CASE 1: Augmented assignment and mutability
# =============================================================================

# CONCEPT: `+=` behaves DIFFERENTLY for mutable vs immutable objects.
# For mutable (list): calls __iadd__ and mutates IN-PLACE
# For immutable (tuple/int/str): creates a NEW object, rebinds the name

print("=== Edge Case 1: += for Mutable vs Immutable ===")

# List (mutable): += mutates in-place
x = [1, 2]
y = x           # y points to same list
x += [3]        # __iadd__ mutates the shared object
print(f"x = {x}, y = {y}")   # BOTH show [1, 2, 3] — same object mutated

# Tuple (immutable): += creates a new object
a = (1, 2)
b = a           # b points to original tuple
a += (3,)       # creates NEW tuple, rebinds a; b unchanged
print(f"a = {a}, b = {b}")   # a=(1,2,3), b=(1,2) — different objects now

# Integer (immutable): += creates a new int
n = 10
m = n
n += 5          # creates NEW int 15, rebinds n; m unchanged
print(f"n = {n}, m = {m}")   # n=15, m=10

# String (immutable): += creates a new string
s1 = "hello"
s2 = s1
s1 += " world"  # creates NEW string, rebinds s1; s2 unchanged
print(f"s1 = '{s1}', s2 = '{s2}'")   # s1 changed, s2 = "hello"


# =============================================================================
# EDGE CASE 2: `is` with cached objects — don't use `is` for equality
# =============================================================================

# CONCEPT: CPython caches small integers (-5 to 256) and short identifier-like
# strings. `a is b` may return True for these, but NOT for larger values.
# RULE: Never use `is` for value comparison — only for None/True/False.

print("\n=== Edge Case 2: Object Caching / Interning ===")

# Small integers are cached
a, b = 100, 100
print(f"100 is 100: {a is b}")      # True (cached by CPython)

c, d = 1000, 1000
print(f"1000 is 1000: {c is d}")    # Often False (different objects)

# Short identifier-like strings are often interned
s1 = "hello"
s2 = "hello"
print(f"'hello' is 'hello': {s1 is s2}")       # Usually True

s3 = "hello world"
s4 = "hello world"
print(f"'hello world' is same: {s3 is s4}")    # Often False (not interned)

# CORRECT comparison — always use ==, not is
print(f"\nCorrect: use == for values")
print(f"  'hello' == 'hello': {s1 == s2}")
print(f"  1000 == 1000: {c == d}")

# The ONLY safe use of `is`:
x = None
print(f"  x is None (correct pattern): {x is None}")
x = True
print(f"  x is True (correct pattern): {x is True}")


# =============================================================================
# EDGE CASE 3: Single-element tuple — the trailing comma
# =============================================================================

# CONCEPT: Parentheses alone do NOT create a tuple.
# The COMMA is what creates a tuple, not the parentheses.

print("\n=== Edge Case 3: Single-Element Tuple ===")

not_a_tuple = (42)    # Just int 42 in parens — parens are grouping, not tuple
is_a_tuple  = (42,)   # Trailing comma makes it a tuple
also_tuple  = 42,     # Parentheses are optional — comma alone is enough

print(f"type((42)):  {type(not_a_tuple).__name__} = {not_a_tuple}")   # int
print(f"type((42,)): {type(is_a_tuple).__name__} = {is_a_tuple}")     # tuple
print(f"type(42,):   {type(also_tuple).__name__} = {also_tuple}")     # tuple

# This bites people when trying to create a single-item tuple in a list:
mistake = [(1), (2), (3)]    # list of ints, not list of tuples!
correct = [(1,), (2,), (3,)] # list of single-element tuples

print(f"\nmistake:  {mistake}")   # [1, 2, 3]
print(f"correct:  {correct}")    # [(1,), (2,), (3,)]

# Empty tuple is fine with just ():
empty = ()
print(f"empty tuple: {type(empty).__name__} = {empty}")


# =============================================================================
# EDGE CASE 4: Falsy values — when 0, "", [] are valid data
# =============================================================================

# CONCEPT: Many values are falsy in Python. Using `if not val` when 0 or ""
# are valid data leads to silent logic bugs.

print("\n=== Edge Case 4: Falsy Values Trap ===")

# These are ALL falsy:
for val in [None, False, 0, 0.0, "", [], {}, set(), ()]:
    print(f"  bool({repr(val):12}) = {bool(val)}")

# THE BUG: checking for "missing value" with `if not x`
user_score = 0    # user scored zero — a valid, meaningful value

if not user_score:
    print("\nBug: treated 0 as 'no score'")   # prints incorrectly!

# CORRECT: check explicitly for None
if user_score is None:
    print("No score recorded")
else:
    print(f"Score: {user_score}")   # prints correctly with 0


# =============================================================================
# EDGE CASE 5: Exception variable scope (Python 3)
# =============================================================================

# CONCEPT: In Python 3, the `as e` variable in `except` is DELETED when the
# block exits. Save anything you need before leaving the except block.

print("\n=== Edge Case 5: Exception Variable Scope ===")

try:
    raise ValueError("payment failed: insufficient funds")
except ValueError as e:
    message = str(e)    # save to a regular variable before block ends
    code = 402
    print(f"Inside except: {e}")

# `e` no longer exists here
try:
    print(e)   # NameError!
except NameError:
    print("e is not defined after except block (Python 3 behavior)")

print(f"Saved message: {message}")   # `message` is still accessible
print(f"Saved code:    {code}")


# =============================================================================
# EDGE CASE 6: Chained comparisons
# =============================================================================

# CONCEPT: Python supports `a < b < c` as mathematical chaining.
# It evaluates as `(a < b) and (b < c)` — not as `((a < b) < c)`.

print("\n=== Edge Case 6: Chained Comparisons ===")

x = 5
print(f"1 < {x} < 10:  {1 < x < 10}")    # True
print(f"1 < {x} < 4:   {1 < x < 4}")     # False
print(f"10 > {x} > 1:  {10 > x > 1}")    # True (works both directions)

# You can chain multiple comparisons
age = 25
print(f"18 <= age <= 65: {18 <= age <= 65}")   # True (working age range)

# WARNING: mixing == in a chain is valid syntax but can be confusing
# 1 == 1 == 1 → True (both (1==1) and (1==1))
# 1 == 1 == 2 → False (1==1 is True, but 1==2 is False)
print(f"1 == 1 == 1: {1 == 1 == 1}")   # True
print(f"1 == 1 == 2: {1 == 1 == 2}")   # False


# =============================================================================
# EDGE CASE 7: Multiple assignment and tuple unpacking
# =============================================================================

# CONCEPT: Python evaluates the RIGHT side FULLY before assigning to the LEFT.
# This enables elegant simultaneous assignment (e.g., swap, Fibonacci).

print("\n=== Edge Case 7: Multiple Assignment ===")

# Swap without temp variable
a, b = 10, 20
a, b = b, a   # right side (b, a) = (20, 10) is evaluated FIRST, then assigned
print(f"After swap: a={a}, b={b}")   # a=20, b=10

# This is different from:
# a = b    # a gets b's old value
# b = a    # b gets a's (now changed) value — WRONG

# Fibonacci — both sides evaluated before any assignment
n1, n2 = 0, 1
for _ in range(8):
    print(n1, end=" ")
    n1, n2 = n2, n1 + n2   # both n2 and n1+n2 computed before either is updated
print()

# Extended unpacking (Python 3)
first, *middle, last = [1, 2, 3, 4, 5]
print(f"first={first}, middle={middle}, last={last}")

# Underscore for values you don't need
_, important, *_ = [10, 99, 30, 40, 50]
print(f"important={important}")   # 99


# =============================================================================
# EDGE CASE 8: Mutable objects inside "immutable" containers
# =============================================================================

# CONCEPT: A tuple is immutable — you can't change which objects it holds.
# But if those objects are mutable, their CONTENTS can still change.
# This surprises people who assume "tuple = fully frozen."

print("\n=== Edge Case 8: Mutability Inside Immutable Containers ===")

frozen_outside = ([1, 2, 3], [4, 5, 6])  # tuple of two lists

# Can't reassign tuple positions:
try:
    frozen_outside[0] = [99]
except TypeError as e:
    print(f"Can't reassign tuple element: {e}")

# CAN mutate the list objects the tuple holds:
frozen_outside[0].append(99)
print(f"Inner list mutated through tuple: {frozen_outside}")
# The tuple still holds the same two list OBJECTS — we just changed what's
# inside those objects.

# WHY THIS MATTERS: frozen_outside is not hashable despite being a tuple
try:
    d = {frozen_outside: "value"}
except TypeError as e:
    print(f"Not hashable because contains mutable: {e}")

# Only tuples containing ONLY hashable elements can be dict keys:
hashable_tuple = (1, 2, "hello")
d = {hashable_tuple: "works fine"}
print(f"Hashable tuple as key: {d}")


print("\n=== Part 1 complete ===")
print("Interview-critical gotchas (no functions required):")
print("  1. += mutates lists, creates new object for tuples/ints/strings")
print("  2. `is` only for None/True/False — use `==` for everything else")
print("  3. (42) is int, (42,) is tuple — the COMMA makes a tuple")
print("  4. 0, '', [] are falsy — use `is None` when they're valid values")
print("  5. Exception variable `e` is deleted after except block in Python 3")
print("  6. a, b = b, a evaluates right side fully before assigning")
print("  7. Mutable objects inside tuples can still be mutated in-place")
print()
print(">>> Come back after Module 04 (Functions) for Part 2 below <<<")


# =============================================================================
# PART 2 — Requires: Module 04 (Functions) completed first
# =============================================================================
# These edge cases specifically involve function behavior.
# They can't be demonstrated without def statements.
# =============================================================================

print("\n" + "="*60)
print("PART 2: Requires Module 04 (Functions)")
print("="*60)

# =============================================================================
# EDGE CASE 9: Mutable default argument (the most famous Python gotcha)
# =============================================================================

# CONCEPT: Default values are evaluated ONCE at function definition, not per call.
# A mutable default is shared across ALL calls — it accumulates state.

print("\n=== Edge Case 9: Mutable Default Argument ===")

def broken_accumulator(value, history=[]):
    # `history` is the SAME list object on every call (unless passed explicitly)
    history.append(value)
    return history

print(broken_accumulator(1))   # [1]      — looks fine
print(broken_accumulator(2))   # [1, 2]   — surprise! 1 is still there
print(broken_accumulator(3))   # [1, 2, 3] — grows forever

# FIX: use None as sentinel, create fresh list each call
def fixed_accumulator(value, history=None):
    if history is None:
        history = []
    history.append(value)
    return history

print(fixed_accumulator(1))    # [1]
print(fixed_accumulator(2))    # [2] — correctly isolated


# =============================================================================
# EDGE CASE 10: Late binding closures
# =============================================================================

# CONCEPT: Closures capture the VARIABLE, not the value at creation time.
# When the inner function runs, it reads the variable's CURRENT value.

print("\n=== Edge Case 10: Late Binding Closures ===")

# BROKEN: every lambda returns 4 (the final value of i after the loop)
funcs_broken = [lambda: i for i in range(5)]
print("Broken:", [f() for f in funcs_broken])   # [4, 4, 4, 4, 4]

# FIX: capture the value with a default argument (evaluated at creation time)
funcs_fixed = [lambda i=i: i for i in range(5)]
print("Fixed: ", [f() for f in funcs_fixed])    # [0, 1, 2, 3, 4]

# FIX 2: factory function — cleaner for complex closures
def make_multiplier(n):
    return lambda x: x * n   # n is a local variable, its value is bound here

double = make_multiplier(2)
triple = make_multiplier(3)
print(f"double(5)={double(5)}, triple(5)={triple(5)}")   # 10, 15


# =============================================================================
# EDGE CASE 11: UnboundLocalError — the assignment-makes-it-local trap
# =============================================================================

# CONCEPT: If you ASSIGN to a variable ANYWHERE in a function, Python treats
# that variable as LOCAL throughout the ENTIRE function, even before the
# assignment line. Reading it before assignment causes UnboundLocalError.

print("\n=== Edge Case 11: UnboundLocalError ===")

counter = 10

def broken():
    # Python sees `counter = ...` → marks `counter` as local
    # But then tries to READ `counter` (on the right side) before it's assigned
    try:
        counter = counter + 1   # UnboundLocalError: read before assign
    except UnboundLocalError as e:
        print(f"  UnboundLocalError: {e}")

broken()

# FIX 1: `global` keyword — tells Python to use the module-level variable
def with_global():
    global counter
    counter += 1

with_global()
print(f"  counter after with_global(): {counter}")   # 11

# FIX 2: Better design — pass value in, return result out (no global state)
def pure_increment(n):
    return n + 1

counter = pure_increment(counter)
print(f"  counter after pure_increment: {counter}")  # 12
# This is preferred — pure functions are testable and predictable


print("\n=== All edge cases complete ===")
print("Part 2 additions (function-specific):")
print("  9.  Mutable defaults are shared across calls — always use None")
print("  10. Closures capture variables, not values — use default args to fix")
print("  11. Any assignment in a function makes that variable local everywhere")
