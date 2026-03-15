"""
03_data_types/set_practice.py
===============================
CONCEPT: Python sets — unordered collections of UNIQUE elements with
O(1) average-case membership testing (backed by a hash table).

WHY THIS MATTERS: Sets are the right tool when you need:
  - Deduplication (remove duplicates instantly)
  - Membership testing at scale (x in large_set vs x in large_list)
  - Mathematical set operations (intersection, union, difference)
Sets appear in graph algorithms, data deduplication pipelines, permission
systems, and anywhere you need "have I seen this before?" logic.

LEARNING PATH:
  Part 1 (this module): all set operations using only Modules 01–03 knowledge
  Part 2 (bottom):      revisit AFTER Module 04 (Functions) for reusable helpers
"""

import time

# =============================================================================
# PART 1 — Requires only: Modules 01–03 (variables, loops, conditionals)
# =============================================================================

# =============================================================================
# SECTION 1: Set creation and basic operations
# =============================================================================

# CONCEPT: Sets use curly braces but contain no key-value pairs.
# Note: {} creates an EMPTY DICT, not an empty set — use set() for empty set.

print("=== Section 1: Set Creation ===")

# Literal
fruits = {"apple", "banana", "cherry", "apple"}   # duplicate auto-removed
print(f"Set literal:  {fruits}")   # only 3 items — apple deduplicated

# From iterable — instant deduplication
words = "the quick brown fox jumps over the lazy dog the".split()
unique_words = set(words)
print(f"Unique words: {sorted(unique_words)}")   # sorted for deterministic output
print(f"Total: {len(words)}, Unique: {len(unique_words)}")

# Empty set — MUST use set(), not {}
empty_set  = set()
empty_dict = {}
print(f"type(set()):  {type(empty_set)}")    # <class 'set'>
print(f"type({{}}):     {type(empty_dict)}")  # <class 'dict'>

# From range / comprehension
evens = {x for x in range(20) if x % 2 == 0}   # set comprehension
print(f"Even numbers 0-18: {sorted(evens)}")


# =============================================================================
# SECTION 2: O(1) membership testing — why sets beat lists for lookup
# =============================================================================

# CONCEPT: x in list is O(n) — Python checks each element until found.
# x in set  is O(1) average — hash table lookup, independent of size.
# For 1M items, set lookup is ~100,000x faster than list lookup.

print("\n=== Section 2: O(1) Membership Testing ===")

# Create large list and set with same data
large_data = list(range(1_000_000))
large_set  = set(large_data)

target = 999_999   # worst case for list (near end)

# List lookup
start = time.perf_counter()
found = target in large_data
list_time = time.perf_counter() - start

# Set lookup
start = time.perf_counter()
found = target in large_set
set_time = time.perf_counter() - start

print(f"List lookup (1M items): {list_time * 1000:.3f} ms")
print(f"Set  lookup (1M items): {set_time * 1000:.3f} ms")
print(f"Set is ~{int(list_time / max(set_time, 1e-9))}x faster")

# Real-world use: checking if a user ID is in a banned list
# Use a set, NOT a list — the check happens per request
BANNED_USERS = {1042, 2891, 3344, 9871, 12050}   # set literal — O(1) lookup

user_id = 2891
print(f"User {user_id} banned: {user_id in BANNED_USERS}")
user_id = 1234
print(f"User {user_id} banned: {user_id in BANNED_USERS}")


# =============================================================================
# SECTION 3: Set operations — math made practical
# =============================================================================

# CONCEPT: Sets support the four fundamental mathematical set operations.
# These have direct real-world applications: finding common elements,
# unique elements, elements in one group but not another.

print("\n=== Section 3: Set Operations ===")

python_devs = {"Alice", "Bob", "Carol", "Diana"}
java_devs   = {"Bob", "Carol", "Eve", "Frank"}

# Union (|) — all unique developers from both groups
all_devs = python_devs | java_devs
print(f"All developers: {sorted(all_devs)}")

# Intersection (&) — developers who know BOTH languages
both = python_devs & java_devs
print(f"Know both Python and Java: {sorted(both)}")

# Difference (-) — Python devs who DON'T know Java
python_only = python_devs - java_devs
print(f"Python only: {sorted(python_only)}")

# Symmetric difference (^) — in exactly one group, not both
exclusive = python_devs ^ java_devs
print(f"Know exactly one language: {sorted(exclusive)}")

# Subset / superset checks
junior = {"Alice", "Bob"}
print(f"\njunior ⊆ python_devs: {junior.issubset(python_devs)}")       # True
print(f"python_devs ⊇ junior: {python_devs.issuperset(junior)}")       # True
print(f"python_devs disjoint {{Zara}}: {python_devs.isdisjoint({'Zara'})}")  # True


# =============================================================================
# SECTION 4: Real-world deduplication patterns
# =============================================================================

# CONCEPT: Converting to set and back is the fastest way to deduplicate a list.
# Order is lost (sets are unordered), but if you need order, use dict.fromkeys().

print("\n=== Section 4: Deduplication Patterns ===")

# Basic deduplication (order not preserved)
raw_ids = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
unique_ids = list(set(raw_ids))
print(f"Deduplicated (unordered): {sorted(unique_ids)}")

# Order-preserving deduplication (Python 3.7+: dicts maintain insertion order)
# dict.fromkeys(items) creates a dict with items as keys — duplicates removed,
# order preserved. Convert back to list.
raw_ids_again = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
ordered_unique = list(dict.fromkeys(raw_ids_again))
print(f"Deduplicated (ordered):   {ordered_unique}")

# Deduplicating complex objects by a key — using a seen set
products = [
    {"id": 101, "name": "Widget A"},
    {"id": 102, "name": "Widget B"},
    {"id": 101, "name": "Widget A (duplicate)"},   # same id!
    {"id": 103, "name": "Widget C"},
]
seen_ids       = set()
unique_products = []
for p in products:
    if p["id"] not in seen_ids:   # O(1) lookup!
        unique_products.append(p)
        seen_ids.add(p["id"])

print(f"Unique products: {[p['name'] for p in unique_products]}")


# =============================================================================
# SECTION 5: Finding common / uncommon elements across collections
# =============================================================================

# CONCEPT: Set operations express common data problems in one line.
# These replace complex loop-based solutions.

print("\n=== Section 5: Common/Uncommon Element Problems ===")

# Find emails that appear in both lists (common subscribers)
list1_emails  = {"alice@x.com", "bob@x.com", "carol@x.com", "diana@x.com"}
list2_emails  = {"bob@x.com", "carol@x.com", "eve@x.com"}

common        = list1_emails & list2_emails          # in both
only_in_list1 = list1_emails - list2_emails          # churned / unsubscribed
only_in_list2 = list2_emails - list1_emails          # new subscribers
all_emails    = list1_emails | list2_emails           # total unique reach

print(f"Common emails:    {sorted(common)}")
print(f"Only in list 1:   {sorted(only_in_list1)}")
print(f"Only in list 2:   {sorted(only_in_list2)}")
print(f"Total unique:     {len(all_emails)}")

# Find features missing from a product tier
required_features = {"login", "logout", "dashboard", "reports", "export", "api"}
basic_tier        = {"login", "logout", "dashboard"}
missing = required_features - basic_tier
print(f"\nFeatures missing from basic tier: {sorted(missing)}")

# Find shared interests between two users (Jaccard similarity)
user_a_tags = {"python", "ml", "data", "fastapi", "docker"}
user_b_tags = {"python", "go", "docker", "kubernetes", "ml"}
shared      = user_a_tags & user_b_tags
similarity  = len(shared) / len(user_a_tags | user_b_tags)  # Jaccard
print(f"\nShared interests: {shared}")
print(f"Jaccard similarity: {similarity:.2f}")


# =============================================================================
# SECTION 6: Mutable set operations (in-place)
# =============================================================================

# CONCEPT: Sets support in-place versions of all operations.
# Use these when you have a running set you're updating.

print("\n=== Section 6: In-Place Set Operations ===")

active_sessions = {"user1", "user2", "user3"}

# add() — single element
active_sessions.add("user4")
print(f"After add user4: {sorted(active_sessions)}")

# update() — add multiple elements from any iterable
new_logins = ["user5", "user6", "user1"]   # user1 is duplicate
active_sessions.update(new_logins)
print(f"After update:    {sorted(active_sessions)}")

# discard() — remove if present, no error if missing (safe remove)
active_sessions.discard("user2")    # removed
active_sessions.discard("user99")   # silently ignored — user99 wasn't there
print(f"After discard user2: {sorted(active_sessions)}")

# remove() — like discard but raises KeyError if missing
try:
    active_sessions.remove("user99")
except KeyError:
    print("remove() raises KeyError for missing element")

# In-place operations
admin_users = {"user1", "user3", "user5"}
active_sessions &= admin_users   # keep only admins in active sessions
print(f"Active admin sessions: {sorted(active_sessions)}")


# =============================================================================
# SECTION 7: frozenset — immutable sets (hashable, usable as dict keys)
# =============================================================================

# CONCEPT: frozenset is an immutable set. Like tuple vs list.
# Because it's immutable, it's HASHABLE — can be used as a dict key or
# stored in a regular set. Regular sets CANNOT be used as dict keys.

print("\n=== Section 7: frozenset ===")

# Graph: represent each edge as a frozenset so {A, B} == {B, A}
edges = {frozenset({"A", "B"}), frozenset({"B", "C"}), frozenset({"A", "C"})}
print(f"Edges: {edges}")

# Check if edge exists (both directions work!)
print(f"A-B edge exists: {frozenset({'A', 'B'}) in edges}")   # True
print(f"B-A edge exists: {frozenset({'B', 'A'}) in edges}")   # True — same frozenset!

# Use frozensets as dict keys (regular sets are not hashable)
permission_map = {
    frozenset({"read"}):                   "viewer",
    frozenset({"read", "write"}):          "editor",
    frozenset({"read", "write", "admin"}): "admin",
}

user_perms = frozenset({"read", "write"})
role = permission_map.get(user_perms, "unknown")
print(f"Role for {{read, write}}: {role}")


print("\n=== Part 1 complete ===")
print("When to reach for a set:")
print("  1. Membership testing at any scale → O(1) vs O(n) for list")
print("  2. Deduplication → set(items) or dict.fromkeys(items)")
print("  3. Common elements → intersection (&)")
print("  4. Missing elements → difference (-)")
print("  5. All unique elements combined → union (|)")
print("  6. As dict key or inside another set → frozenset")
print()
print(">>> Come back after Module 04 (Functions) for Part 2 below <<<")


# =============================================================================
# PART 2 — Requires: Module 04 (Functions) completed first
# =============================================================================

print("\n" + "="*60)
print("PART 2: Requires Module 04 (Functions)")
print("="*60)

# =============================================================================
# SECTION 8: Reusable set utility functions
# =============================================================================

print("\n=== Section 8: Set Utility Functions ===")

def deduplicate_ordered(items):
    """Remove duplicates while preserving first-occurrence order."""
    return list(dict.fromkeys(items))


def jaccard_similarity(set_a, set_b):
    """Jaccard similarity: |A ∩ B| / |A ∪ B| — measures how similar two sets are."""
    if not set_a and not set_b:
        return 1.0
    return len(set_a & set_b) / len(set_a | set_b)


def find_duplicates(items):
    """Return items that appear more than once, preserving order of first duplicate."""
    seen = set()
    duplicates = []
    seen_dups = set()
    for item in items:
        if item in seen and item not in seen_dups:
            duplicates.append(item)
            seen_dups.add(item)
        seen.add(item)
    return duplicates


# Test them
print(deduplicate_ordered([3, 1, 4, 1, 5, 9, 2, 6, 5]))   # [3, 1, 4, 5, 9, 2, 6]

tags_a = {"python", "ml", "data", "docker"}
tags_b = {"python", "go", "docker", "kubernetes"}
print(f"Jaccard similarity: {jaccard_similarity(tags_a, tags_b):.2f}")

print(f"Duplicates in [1,2,1,3,2,4,5,3]: {find_duplicates([1,2,1,3,2,4,5,3])}")


print("\n=== All sections complete ===")
