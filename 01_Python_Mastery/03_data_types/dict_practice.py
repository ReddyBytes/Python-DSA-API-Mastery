"""
03_data_types/dict_practice.py
================================
CONCEPT: Python dictionaries — hash maps with O(1) average-case lookup.
WHY THIS MATTERS: Dicts are the most-used data structure in Python backends.
Every API response, config file, database row, and JSON object becomes a dict.
Mastering dict patterns is the fastest way to write clean, fast Python.

Since Python 3.7+: dicts maintain INSERTION ORDER (guaranteed by spec).

LEARNING PATH:
  Part 1 (this module): all dict patterns using only Modules 01–03 knowledge
  Part 2 (bottom):      revisit AFTER completing Module 04 (Functions)
                        — advanced patterns that need def
"""

from collections import defaultdict, Counter
import json

# =============================================================================
# PART 1 — Requires only: Modules 01–03 (variables, loops, conditionals, dicts)
# =============================================================================

# =============================================================================
# SECTION 1: Dict creation patterns
# =============================================================================

# CONCEPT: Multiple ways to create dicts — choose based on where data comes from

print("=== Section 1: Creation Patterns ===")

# Literal — most readable, use when you know keys at write time
config = {"host": "localhost", "port": 5432, "db": "myapp"}

# dict() constructor — useful when building from keyword args
settings = dict(debug=True, timeout=30, max_retries=3)

# From two sequences (zip) — common when you have parallel lists
keys   = ["name", "age", "city"]
values = ["Alice", 30, "New York"]
person = dict(zip(keys, values))
print(f"From zip: {person}")

# Dict comprehension — transform/filter an existing mapping
prices   = {"apple": 1.2, "banana": 0.5, "cherry": 3.0}
expensive = {k: v for k, v in prices.items() if v > 1.0}
print(f"Expensive items: {expensive}")

# Nested dict from list of records (grouping pattern)
users = [
    {"id": 1, "name": "Alice", "role": "admin"},
    {"id": 2, "name": "Bob",   "role": "user"},
    {"id": 3, "name": "Carol", "role": "admin"},
]
# Index by id for O(1) lookup instead of O(n) list search
users_by_id = {u["id"]: u for u in users}
print(f"User 2: {users_by_id[2]}")


# =============================================================================
# SECTION 2: Access patterns — safe vs unsafe
# =============================================================================

# CONCEPT: Accessing a missing key with [] raises KeyError (crashes).
# .get() returns None (or a default) safely — always prefer .get() for
# optional keys. Use [] only when the key MUST be there.

print("\n=== Section 2: Safe Access Patterns ===")

user = {"name": "Alice", "email": "alice@example.com"}

# Unsafe — crashes if key missing
# print(user["age"])   # KeyError: 'age'

# Safe — returns None if missing
age = user.get("age")
print(f"age (missing): {age}")   # None

# Safe with default
age = user.get("age", 0)
print(f"age with default: {age}")   # 0

# setdefault — gets value if key exists, otherwise SETS the key AND returns default
cache = {}
cache.setdefault("users", []).append("Alice")
cache.setdefault("users", []).append("Bob")   # key exists, won't reset to []
print(f"After setdefault: {cache}")   # {'users': ['Alice', 'Bob']}

# pop — remove and return (with optional default to avoid KeyError)
removed = user.pop("email", "not found")
print(f"Popped email: {removed}")


# =============================================================================
# SECTION 3: Iteration patterns
# =============================================================================

# CONCEPT: Python dicts have 3 view objects: .keys(), .values(), .items()
# Always use .items() when you need both key and value — avoid d[k] in a loop.

print("\n=== Section 3: Iteration Patterns ===")

inventory = {"apples": 50, "bananas": 30, "cherries": 10}

# Iterate keys (default iteration)
print("Keys: ", end="")
for fruit in inventory:   # same as for fruit in inventory.keys()
    print(fruit, end=" ")
print()

# Iterate values
total = sum(inventory.values())
print(f"Total items: {total}")

# Iterate key-value pairs — most common
for fruit, count in inventory.items():
    print(f"  {fruit}: {count} units")

# Sorted iteration (by key) — no lambda needed
for fruit in sorted(inventory):
    print(f"  {fruit}: {inventory[fruit]}")

# Sorted by value: use a list of (value, key) tuples, sort, unpack
items_by_count = sorted(
    [(count, fruit) for fruit, count in inventory.items()],
    reverse=True
)
print("  Sorted by count (descending):")
for count, fruit in items_by_count:
    print(f"    {fruit}: {count}")


# =============================================================================
# SECTION 4: Merging and updating dicts
# =============================================================================

# CONCEPT: Multiple ways to merge dicts depending on Python version and intent.
# Python 3.9+: `|` operator (cleanest). Earlier: `{**a, **b}` or .update().

print("\n=== Section 4: Merging Dicts ===")

defaults = {"timeout": 30, "retries": 3, "debug": False}
user_overrides = {"timeout": 60, "debug": True}

# Python 3.9+: | operator (non-destructive, creates new dict)
merged = defaults | user_overrides
print(f"Merged (| operator): {merged}")
# RIGHT side wins on conflicts: timeout=60, debug=True

# Earlier Python / mutate in place: .update()
config = dict(defaults)   # copy first!
config.update(user_overrides)
print(f"Merged (.update): {config}")

# Spread operator merge (works on all Python 3.5+)
merged2 = {**defaults, **user_overrides}
print(f"Merged (**spread): {merged2}")

# Manual deep merge (nested dicts) using just a loop — no def needed
# for simple two-level nesting
nested_base     = {"db": {"host": "localhost", "port": 5432}, "app": {"debug": False}}
nested_override = {"db": {"port": 5433},                      "app": {"debug": True}}

# Build the deep merge result manually:
deep_merged = {}
for key in set(list(nested_base.keys()) + list(nested_override.keys())):
    base_val     = nested_base.get(key, {})
    override_val = nested_override.get(key, {})
    if isinstance(base_val, dict) and isinstance(override_val, dict):
        deep_merged[key] = {**base_val, **override_val}
    else:
        deep_merged[key] = override_val if key in nested_override else base_val

print(f"Deep merged: {deep_merged}")


# =============================================================================
# SECTION 5: defaultdict — automatic default values
# =============================================================================

# CONCEPT: defaultdict(factory) automatically creates a default value when
# you access a missing key, using the factory function (list, int, set, etc.)
# Eliminates the "if key not in d: d[key] = []" boilerplate everywhere.

print("\n=== Section 5: defaultdict ===")

# GROUP BY pattern — grouping items by category
transactions = [
    ("Alice", 100), ("Bob", 200), ("Alice", 150),
    ("Carol", 300), ("Bob", 50),  ("Alice", 75),
]

# Without defaultdict — boilerplate
totals_manual = {}
for user, amount in transactions:
    if user not in totals_manual:
        totals_manual[user] = 0
    totals_manual[user] += amount

# With defaultdict(int) — clean and idiomatic
totals = defaultdict(int)
for user, amount in transactions:
    totals[user] += amount   # no need to initialize to 0!
print(f"User totals: {dict(totals)}")

# Group items into lists
by_user = defaultdict(list)
for user, amount in transactions:
    by_user[user].append(amount)
print(f"Transactions per user: {dict(by_user)}")

# Build graph (adjacency list)
edges = [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]
graph = defaultdict(set)   # use set to avoid duplicate edges
for u, v in edges:
    graph[u].add(v)
    graph[v].add(u)   # undirected
print(f"Graph neighbors of 1: {graph[1]}")


# =============================================================================
# SECTION 6: Counter — frequency counting
# =============================================================================

# CONCEPT: Counter is a dict subclass specialized for counting.
# .most_common(n) returns top-n items. Arithmetic operations work between counters.

print("\n=== Section 6: Counter ===")

# Character frequency
text = "the quick brown fox jumps over the lazy dog"
char_counts = Counter(text.replace(" ", ""))
print(f"Top 5 characters: {char_counts.most_common(5)}")

# Word frequency
word_counts = Counter(text.split())
print(f"Top 3 words: {word_counts.most_common(3)}")

# Arithmetic on counters
basket1 = Counter({"apples": 3, "oranges": 1})
basket2 = Counter({"apples": 1, "bananas": 4})
combined   = basket1 + basket2
difference = basket1 - basket2   # removes negative/zero counts
print(f"Combined baskets: {combined}")
print(f"Basket1 minus Basket2: {difference}")


# =============================================================================
# SECTION 7: JSON ↔ dict — real-world API pattern
# =============================================================================

# CONCEPT: JSON IS a dict in Python. Every API response you receive or send
# is converted to/from a Python dict. Mastering this is non-negotiable.

print("\n=== Section 7: JSON ↔ Dict ===")

# Simulate an API response (JSON string → Python dict)
api_response_json = """
{
    "status": "success",
    "data": {
        "users": [
            {"id": 1, "name": "Alice", "active": true},
            {"id": 2, "name": "Bob",   "active": false}
        ],
        "total": 2
    }
}
"""

data = json.loads(api_response_json)
print(f"Status: {data['status']}")
print(f"Total users: {data['data']['total']}")

# Filter active users — using list comprehension (no def needed)
active = [u for u in data["data"]["users"] if u["active"]]
print(f"Active users: {[u['name'] for u in active]}")

# Python dict → JSON string (for sending back to an API)
response_payload = {"result": "ok", "processed": len(active)}
json_output = json.dumps(response_payload, indent=2)
print(f"JSON response:\n{json_output}")


print("\n=== Part 1 complete ===")
print("Mental model: dict = hash map = O(1) lookup by key")
print("Key patterns:")
print("  1. .get(key, default)         — never crash on missing key")
print("  2. .items()                   — always use when you need key AND value")
print("  3. defaultdict(list/int/set)  — eliminates init-if-missing boilerplate")
print("  4. Counter                    — instant frequency counting")
print("  5. dict | other               — clean merge, right side wins (Python 3.9+)")
print()
print(">>> Come back after Module 04 (Functions) for Part 2 below <<<")


# =============================================================================
# PART 2 — Requires: Module 04 (Functions) completed first
# =============================================================================

print("\n" + "="*60)
print("PART 2: Requires Module 04 (Functions)")
print("="*60)

# =============================================================================
# SECTION 8: Deep merge with recursion
# =============================================================================

print("\n=== Section 8: Recursive Deep Merge ===")

def deep_merge(base, override):
    """Recursively merge override into base. Override wins on conflicts."""
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = deep_merge(result[key], val)
        else:
            result[key] = val
    return result

nested_base     = {"db": {"host": "localhost", "port": 5432}, "app": {"debug": False}}
nested_override = {"db": {"port": 5433},                      "app": {"debug": True}}
print(f"Deep merged: {deep_merge(nested_base, nested_override)}")


# =============================================================================
# SECTION 9: Dispatch table (dict of functions)
# =============================================================================

# CONCEPT: A dict of functions eliminates long if-elif-elif chains.
# Adding a new case = adding one line to the dict. No touching the logic.
# This pattern is used in command parsers, event handlers, routing systems.

print("\n=== Section 9: Dispatch Table Pattern ===")

def handle_create(data):
    return f"Created: {data}"

def handle_read(data):
    return f"Read: {data}"

def handle_update(data):
    return f"Updated: {data}"

def handle_delete(data):
    return f"Deleted: {data}"

# Dispatch table: maps operation name → handler function
OPERATIONS = {
    "create": handle_create,
    "read":   handle_read,
    "update": handle_update,
    "delete": handle_delete,
}

def dispatch(operation, data):
    handler = OPERATIONS.get(operation)
    if not handler:
        return f"Unknown operation: {operation}"
    return handler(data)

print(dispatch("create", {"name": "Alice"}))
print(dispatch("read",   {"id": 42}))
print(dispatch("delete", {"id": 99}))
print(dispatch("magic",  {}))


print("\n=== All sections complete ===")
