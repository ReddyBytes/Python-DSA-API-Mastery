"""
01_python_fundamentals/practice.py
===================================
CONCEPT: Python's reference model — variables point to objects, not store them.
WHY THIS MATTERS: This is the #1 source of bugs for developers coming from C/Java.
Misunderstanding references causes mysterious mutations, memory issues, and
"how did THAT change?" bugs in production.

LEARNING PATH:
  Part 1 (this module): reference model, rebinding vs mutation, copies — NO functions needed
  Part 2 (bottom):      revisit AFTER completing Module 04 (Functions)

Run this file top-to-bottom and observe every output carefully.
"""

import sys
import copy

# =============================================================================
# PART 1 — Requires only: Module 01 knowledge (variables, lists, dicts, print)
# =============================================================================

# =============================================================================
# SECTION 1: Variables are references, not boxes
# =============================================================================

# CONCEPT: When you write `a = [1, 2, 3]`, Python creates a list object in heap
# memory, and `a` is just a label pointing to that object. NOT a copy of data.

a = [1, 2, 3]
b = a            # b now points to the SAME list object — no new list created

print("=== Section 1: References ===")
print(f"id(a) = {id(a)}")    # memory address of the object
print(f"id(b) = {id(b)}")    # same address — same object!
print(f"a is b: {a is b}")   # True — they are literally the same object

# Watch what happens when we mutate through b:
b.append(4)
print(f"After b.append(4): a = {a}")  # a also shows [1, 2, 3, 4]
# WHY: There was never two lists. One list, two names pointing to it.


# =============================================================================
# SECTION 2: Rebinding vs Mutation (Critical distinction)
# =============================================================================

# CONCEPT: Rebinding a variable (=) NEVER affects the original object.
# Mutating an object (.append, .update) affects ALL names pointing to it.

print("\n=== Section 2: Rebinding vs Mutation ===")

x = [10, 20, 30]
y = x

# REBINDING: give x a new object entirely
x = [99, 100]   # x now points to a brand-new list

print(f"After x = [99, 100]:")
print(f"x = {x}")    # [99, 100]  — x moved to new object
print(f"y = {y}")    # [10, 20, 30] — y still points to original

# MUTATION: modify the shared object through y
y.append(40)
print(f"After y.append(40): y = {y}")   # [10, 20, 30, 40]
# x is unaffected since it's now pointing to a different object


# =============================================================================
# SECTION 3: Mutable vs Immutable — the other half of the story
# =============================================================================

# CONCEPT: Immutable objects (int, str, tuple, bool) cannot be changed in-place.
# Any "change" creates a new object. This makes sharing them safe.

print("\n=== Section 3: Mutable vs Immutable ===")

# --- Immutable (int) ---
n1 = 100
n2 = n1
n1 = n1 + 1   # This creates a NEW int object (101) — does NOT modify 100

print(f"n1 = {n1}, n2 = {n2}")  # n1=101, n2=100 — safe, no shared mutation

# --- Mutable (list) ---
list1 = [1, 2]
list2 = list1
list1.append(3)   # modifies the SHARED object

print(f"list1 = {list1}, list2 = {list2}")  # both show [1, 2, 3]

# --- String (immutable) ---
s1 = "hello"
s2 = s1
s1 = s1 + " world"   # creates a NEW string, s2 unchanged

print(f"s1 = '{s1}', s2 = '{s2}'")  # s1 changed, s2 unchanged


# =============================================================================
# SECTION 4: is vs == — identity vs equality
# =============================================================================

# CONCEPT: `==` compares values (what the objects contain).
#          `is` compares identity (are they the SAME object in memory?).
# These are different questions and have different answers.

print("\n=== Section 4: is vs == ===")

list_a = [1, 2, 3]
list_b = [1, 2, 3]   # same VALUE, but a different object

print(f"list_a == list_b: {list_a == list_b}")   # True — same content
print(f"list_a is list_b: {list_a is list_b}")   # False — different objects

# The ONLY safe use of `is` is to check against None/True/False singletons:
value = None
print(f"value is None: {value is None}")   # Correct pattern

# Small integer interning — Python caches small integers (-5 to 256)
# This is an implementation detail, never rely on it in production code
a = 100
b = 100
print(f"100 is 100: {a is b}")   # True (cached)

c = 1000
d = 1000
print(f"1000 is 1000: {c is d}")  # May be False (not cached) — CPython-specific


# =============================================================================
# SECTION 5: Shallow copy vs Deep copy — real production issue
# =============================================================================

# CONCEPT: When you copy a container (list/dict), there are two depths:
# SHALLOW: copies the outer container, inner objects still shared
# DEEP:    copies everything recursively — fully independent

print("\n=== Section 5: Shallow vs Deep Copy ===")

original = [[1, 2], [3, 4], [5, 6]]

# Assignment — NOT a copy, just another reference
alias = original

# Shallow copy — new outer list, but inner lists are still SHARED
shallow = copy.copy(original)     # also: original[:]  or  list(original)

# Deep copy — fully independent copy of everything
deep = copy.deepcopy(original)

# Mutate an inner list
original[0].append(99)

print(f"original:  {original}")   # [[1, 2, 99], [3, 4], [5, 6]]
print(f"alias:     {alias}")      # [[1, 2, 99], ...] — same object, same change
print(f"shallow:   {shallow}")    # [[1, 2, 99], ...] — inner list IS shared!
print(f"deep:      {deep}")       # [[1, 2], ...] — completely independent


# =============================================================================
# SECTION 6: Real-world config mutation bug — without functions
# =============================================================================

# CONCEPT: In real apps, sharing mutable dicts causes silent data corruption.
# This is the same reference problem, just with a dict instead of a list.

print("\n=== Section 6: Config Mutation Bug (Direct) ===")

DEFAULT_CONFIG = {"timeout": 30, "retries": 3, "debug": False}

# WRONG: this is just another reference to DEFAULT_CONFIG
user_config = DEFAULT_CONFIG          # NOT a copy!
user_config["timeout"] = 60           # mutates DEFAULT_CONFIG too!
print(f"DEFAULT_CONFIG after mutation: {DEFAULT_CONFIG}")
# timeout is now 60! The global default is corrupted.

# Reset
DEFAULT_CONFIG = {"timeout": 30, "retries": 3, "debug": False}

# CORRECT: work with a copy
user_config = DEFAULT_CONFIG.copy()   # new dict, shared values (fine for primitives)
user_config["timeout"] = 60
print(f"DEFAULT_CONFIG after copy+modify: {DEFAULT_CONFIG}")
# Still {"timeout": 30, ...} — global default protected


# =============================================================================
# SECTION 7: Reference counting — how Python decides when to free memory
# =============================================================================

print("\n=== Section 7: Reference Counting ===")

data = {"key": "value"}
ref2 = data
ref3 = data

# sys.getrefcount always returns 1 extra (the temporary arg to getrefcount itself)
print(f"Ref count (3 names + 1 temp): {sys.getrefcount(data)}")
del ref2
print(f"After del ref2: {sys.getrefcount(data)}")
del ref3
print(f"After del ref3: {sys.getrefcount(data)}")

# When refcount hits 0, Python frees the object from memory automatically.
# You almost never need to call del manually — Python handles it.


print("\n=== Part 1 complete ===")
print("Core mental model: variable = label, object = the thing in memory")
print("One object can have many labels. Deleting a label doesn't destroy the object.")
print()
print(">>> Come back after Module 04 (Functions) for Part 2 below <<<")


# =============================================================================
# PART 2 — Requires: Module 04 (Functions) completed first
# =============================================================================
# These examples use `def` to demonstrate reference-model concepts that
# specifically apply to function calls. Study Module 04 first.
# =============================================================================

print("\n" + "="*60)
print("PART 2: Requires Module 04 (Functions)")
print("="*60)

# =============================================================================
# SECTION 8: The mutable default argument trap (function-specific)
# =============================================================================

# CONCEPT: Default argument values are evaluated ONCE when the function is
# defined, not each time it is called. Using a mutable default (like a list)
# means all calls share the SAME list object.

print("\n=== Section 8: Mutable Default Argument Trap ===")

def add_item_buggy(item, collection=[]):
    """
    BUG: `collection` is evaluated once at function definition.
    Every call that doesn't pass `collection` shares the same list.
    This is one of Python's most famous gotchas.
    """
    collection.append(item)
    return collection

print(add_item_buggy("apple"))    # ['apple'] — looks fine
print(add_item_buggy("banana"))   # ['apple', 'banana'] — NOT what we wanted!
print(add_item_buggy("cherry"))   # ['apple', 'banana', 'cherry'] — keeps growing!

# FIX: Use None as default, create fresh list inside function
def add_item_fixed(item, collection=None):
    """
    CORRECT: None is immutable and safe as default.
    Each call creates a fresh list when collection is not provided.
    """
    if collection is None:
        collection = []   # new list created every call
    collection.append(item)
    return collection

print(add_item_fixed("apple"))    # ['apple']
print(add_item_fixed("banana"))   # ['banana'] — correctly isolated


# =============================================================================
# SECTION 9: Config bug — the function version
# =============================================================================

print("\n=== Section 9: Config Bug via Function ===")

DEFAULT_CONFIG = {"timeout": 30, "retries": 3, "debug": False}

def get_user_config_broken(overrides=None):
    """WRONG — returns reference to global dict, mutations corrupt global state."""
    config = DEFAULT_CONFIG        # just another reference!
    if overrides:
        config.update(overrides)   # mutates DEFAULT_CONFIG!
    return config

get_user_config_broken({"timeout": 60})
print(f"DEFAULT_CONFIG after broken call: {DEFAULT_CONFIG}")
# timeout is now 60 in the global default!

# Reset and fix
DEFAULT_CONFIG = {"timeout": 30, "retries": 3, "debug": False}

def get_user_config_safe(overrides=None):
    """CORRECT — always work with a fresh copy."""
    config = DEFAULT_CONFIG.copy()
    if overrides:
        config.update(overrides)
    return config

get_user_config_safe({"timeout": 60})
print(f"DEFAULT_CONFIG after safe call: {DEFAULT_CONFIG}")
# Still {"timeout": 30, ...} — global default is protected


# =============================================================================
# SECTION 10: Pass-by-assignment in functions
# =============================================================================

# CONCEPT: Python passes references to functions:
# - Mutating the object inside a function AFFECTS the caller
# - Rebinding the parameter inside a function does NOT affect the caller

print("\n=== Section 10: Pass-by-Assignment ===")

def mutate(lst):
    """Mutates the shared object — caller sees this."""
    lst.append(999)

def rebind(lst):
    """Rebinds local name — caller's object is untouched."""
    lst = [1, 2, 3]   # local `lst` now points elsewhere; caller's list unchanged

my_list = [10, 20]
mutate(my_list)
print(f"After mutate(): {my_list}")   # [10, 20, 999]

my_list = [10, 20]
rebind(my_list)
print(f"After rebind(): {my_list}")   # [10, 20] — unchanged


print("\n=== All sections complete ===")
