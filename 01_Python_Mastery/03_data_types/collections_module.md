# Python's `collections` Module — Specialized Containers

> Python's built-in types (list, dict, tuple, set) are generalists — they handle almost any job adequately.
> The `collections` module provides specialists: containers that solve one pattern perfectly, with better
> expressiveness, cleaner code, or measurably faster performance.

Think of it as the difference between a Swiss Army knife and a professional kitchen. The Swiss Army knife
cuts bread, opens bottles, and files your nails — all adequately. A professional kitchen has a bread knife,
a corkscrew, a nail file. Each tool is purpose-built. When you need to fillet a fish, you reach for the
fillet knife — not the all-purpose blade.

---

## What the `collections` Module Provides

```
collections module
│
├── Counter        → frequency counting (dict subclass)
├── defaultdict    → dict that auto-initializes missing keys
├── namedtuple     → tuple with named fields (readable access)
├── deque          → double-ended queue (O(1) at both ends)
├── OrderedDict    → dict with order-aware equality and reordering ops
└── ChainMap       → multiple dicts viewed as one (no merging)
```

Import style — bring in only what you need:

```python
from collections import Counter, defaultdict, namedtuple, deque, OrderedDict, ChainMap
```

---

## Quick Reference: Counter and defaultdict

These two are covered in depth in `theory.md`. Short summaries here for completeness.

### Counter — Frequency Counting

**Counter** is a dict subclass that counts hashable objects. Missing keys return 0 instead of raising
`KeyError`. It is the go-to tool any time you need to answer "how many times does X appear?"

```python
from collections import Counter

words = ["apple", "banana", "apple", "cherry", "apple", "banana"]
c = Counter(words)
# Counter({'apple': 3, 'banana': 2, 'cherry': 1})

c.most_common(2)    # [('apple', 3), ('banana', 2)]   # ← top 2
c["missing"]        # 0  ← no KeyError

# Arithmetic on counts:
c1 = Counter(a=3, b=2)
c2 = Counter(a=1, b=4)
c1 + c2   # Counter({'b': 6, 'a': 4})   # ← add counts
c1 - c2   # Counter({'a': 2})            # ← subtract, drop negatives
```

---

### defaultdict — Auto-Initialize Missing Keys

**defaultdict** takes a factory function. When you access a missing key, it calls the factory and stores
the result — no `KeyError`, no `if key not in d` guard needed.

```python
from collections import defaultdict

# Group items without checking if key exists first
groups = defaultdict(list)
for word in ["cat", "car", "dog", "door", "cat"]:
    groups[word[0]].append(word)   # ← no KeyError even on first insert
# defaultdict(<class 'list'>, {'c': ['cat', 'car'], 'd': ['dog', 'door', 'cat']})
# Wait — 'cat' appears twice so:
# {'c': ['cat', 'car', 'cat'], 'd': ['dog', 'door']}

counts = defaultdict(int)   # default: 0
counts["missing"] += 1      # works cleanly
```

---

## namedtuple — Tuples With Named Fields

### The Problem It Solves

Imagine you write a function that returns a point in 2D space:

```python
def get_origin():
    return (0, 0)

p = get_origin()
print(p[0])   # x coordinate? y coordinate? You have to remember.
```

Index-based access is fragile. When you come back to this code in three weeks, `p[0]` vs `p[1]` tells
you nothing. **namedtuple** solves this by adding named fields to a regular tuple — without changing any
of tuple's performance characteristics.

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])   # ← define the type once
p = Point(3, 7)

p[0]     # 3   ← still works: index access
p.x      # 3   ← also works: named access
p.y      # 7
```

The class name (`"Point"`) and the variable name (`Point`) should match — this is convention, not a rule.

### Creation Patterns

```python
from collections import namedtuple

# Option 1: list of field names
Point = namedtuple("Point", ["x", "y"])

# Option 2: space-separated string (older style)
Point = namedtuple("Point", "x y")

# Both produce identical results
p = Point(x=10, y=20)   # keyword args
p = Point(10, 20)       # positional args
```

### All Tuple Operations Still Work

namedtuple IS a tuple — it inherits everything:

```python
p = Point(3, 7)

len(p)          # 2
p[0]            # 3      ← index access
x, y = p        # 3, 7   ← unpacking
list(p)         # [3, 7]
3 in p          # True
p + Point(1, 1) # Point(x=4, y=8)  ← concatenation (returns plain tuple)
```

### Named Access and Introspection

```python
from collections import namedtuple

Employee = namedtuple("Employee", ["name", "dept", "salary"])
emp = Employee("Alice", "Engineering", 95000)

emp.name      # 'Alice'          # ← named field access
emp.dept      # 'Engineering'
emp.salary    # 95000

emp._fields   # ('name', 'dept', 'salary')  # ← all field names
```

### Converting to dict

```python
emp._asdict()
# {'name': 'Alice', 'dept': 'Engineering', 'salary': 95000}
```

### Immutable "Updates" with `_replace`

Tuples are immutable. **`_replace`** creates a new namedtuple with one or more fields changed — the
original is untouched. Think of it like a "copy with modification":

```python
emp2 = emp._replace(salary=100000)   # ← returns NEW instance
# Employee(name='Alice', dept='Engineering', salary=100000)

emp.salary    # 95000   ← original unchanged
emp2.salary   # 100000  ← new instance has updated value
```

### Default Values

Python 3.6.1+ allows defaults for trailing fields:

```python
Point3D = namedtuple("Point3D", ["x", "y", "z"], defaults=[0])
# ↑ defaults apply from the right: z defaults to 0

Point3D(1, 2)     # Point3D(x=1, y=2, z=0)   ← z gets default
Point3D(1, 2, 3)  # Point3D(x=1, y=2, z=3)   ← z explicitly set
```

Multiple defaults fill from right to left:

```python
Config = namedtuple("Config", ["host", "port", "debug"], defaults=["localhost", 8080, False])
Config()                    # Config(host='localhost', port=8080, debug=False)
Config(host="prod.com")     # Config(host='prod.com', port=8080, debug=False)
```

### namedtuple vs dataclass

Both give you "a class with named attributes." The key difference is mutability and feature depth:

```
┌─────────────────────┬──────────────────────┬──────────────────────┐
│ Feature             │ namedtuple           │ dataclass            │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Mutable fields      │ No (immutable)       │ Yes (default)        │
│ Inherits tuple      │ Yes                  │ No                   │
│ Index access        │ Yes (p[0])           │ No                   │
│ Unpacking           │ Yes                  │ No                   │
│ Memory              │ Lower (tuple-based)  │ Higher (__dict__)    │
│ Methods             │ Limited              │ Any Python method    │
│ Default values      │ Yes (Python 3.6.1+)  │ Yes                  │
│ Type hints          │ Limited              │ Full support         │
│ __post_init__       │ No                   │ Yes                  │
│ Inheritance         │ Via subclassing      │ Yes                  │
└─────────────────────┴──────────────────────┴──────────────────────┘

Rule of thumb:
  - Data is read-only, lightweight, needs tuple ops → namedtuple
  - Data needs mutation, validation, methods, type hints → dataclass
```

### Common Use Cases

```python
# CSV row with meaningful field names
Row = namedtuple("Row", ["user_id", "username", "email", "created_at"])
rows = [Row(*line.split(",")) for line in csv_data]

# Database record
Record = namedtuple("Record", ["id", "title", "author", "year"])

# 2D/3D geometry
Point2D = namedtuple("Point2D", ["x", "y"])
Point3D = namedtuple("Point3D", ["x", "y", "z"])
Rect    = namedtuple("Rect", ["top_left", "bottom_right"])

# Function return value — better than returning a plain tuple
BoundingBox = namedtuple("BoundingBox", ["x", "y", "width", "height"])
def detect_face(image):
    ...
    return BoundingBox(x=100, y=50, width=80, height=90)

box = detect_face(img)
box.x       # much clearer than box[0]
box.width   # much clearer than box[2]
```

---

## deque — Double-Ended Queue

### The Problem It Solves

Imagine a line of people at a coffee shop. People join at the back and are served from the front. If you
model this as a Python list, removing from the front (`list.pop(0)`) forces Python to shift every remaining
element one position to the left. For a list of 10,000 people, that is 10,000 moves — **O(n)**.

**deque** (pronounced "deck") is a data structure designed for fast operations at both ends. Appending or
removing from either end is always **O(1)** — the coffee shop line never slows down as it grows.

```
list.insert(0, x)    → O(n)  — shifts all elements right
list.pop(0)          → O(n)  — shifts all elements left

deque.appendleft(x)  → O(1)  — constant time, no shifting
deque.popleft()      → O(1)  — constant time, no shifting
```

### Creation

```python
from collections import deque

d = deque([1, 2, 3])              # from iterable
d = deque()                       # empty deque
d = deque([1, 2, 3], maxlen=5)    # fixed-size sliding window
```

### Core Operations

```python
from collections import deque

d = deque([2, 3, 4])

d.append(5)         # deque([2, 3, 4, 5])   ← add to right  O(1)
d.appendleft(1)     # deque([1, 2, 3, 4, 5]) ← add to left   O(1)
d.pop()             # 5  → deque([1, 2, 3, 4]) ← remove right O(1)
d.popleft()         # 1  → deque([2, 3, 4])    ← remove left  O(1)

d.extend([5, 6])         # deque([2, 3, 4, 5, 6])  ← extend right
d.extendleft([1, 0])     # deque([0, 1, 2, 3, 4, 5, 6])  ← note: reversed

len(d)       # 7
d[0]         # 0   ← index access (O(1) for ends, O(n) for middle)
d[-1]        # 6
```

### rotate — Shift Elements Circularly

**`rotate(n)`** moves elements `n` positions to the right (positive n) or left (negative n):

```python
d = deque([1, 2, 3, 4, 5])

d.rotate(2)    # deque([4, 5, 1, 2, 3])  ← last 2 move to front
d.rotate(-1)   # deque([5, 1, 2, 3, 4])  ← first element moves to back
```

ASCII view of `rotate(2)`:

```
Before:  [1, 2, 3, 4, 5]
                   ↑  ↑  these two wrap to the front
After:   [4, 5, 1, 2, 3]
```

### maxlen — Fixed-Size Sliding Window

When `maxlen` is set, the deque never grows beyond that size. Adding to a full deque **automatically
drops the element from the opposite end** — the oldest item is discarded:

```python
recent = deque(maxlen=3)   # keeps only last 3 items

recent.append(1)   # deque([1], maxlen=3)
recent.append(2)   # deque([1, 2], maxlen=3)
recent.append(3)   # deque([1, 2, 3], maxlen=3)
recent.append(4)   # deque([2, 3, 4], maxlen=3)  ← 1 dropped automatically
recent.append(5)   # deque([3, 4, 5], maxlen=3)  ← 2 dropped automatically
```

This is the "sliding window" pattern — you always have the last N items, with zero bookkeeping.

### Use Cases

```python
# BFS queue — process nodes in order
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])     # ← deque as queue: append right, popleft
    while queue:
        node = queue.popleft()  # O(1) — efficient front removal
        if node not in visited:
            visited.add(node)
            queue.extend(graph[node])
    return visited

# Undo/redo history
history = deque(maxlen=50)   # keep last 50 actions only
history.append(current_state)

# Recent N log lines
last_100 = deque(maxlen=100)
for line in log_stream:
    last_100.append(line)
# After stream ends: last_100 has the final 100 lines

# Palindrome check using deque
def is_palindrome(s):
    d = deque(s.lower())
    while len(d) > 1:
        if d.popleft() != d.pop():
            return False
    return True
```

### deque vs list Performance

```
┌────────────────────┬──────────┬──────────┐
│ Operation          │ list     │ deque    │
├────────────────────┼──────────┼──────────┤
│ append (right)     │ O(1)*    │ O(1)     │
│ pop (right)        │ O(1)     │ O(1)     │
│ insert at front    │ O(n)     │ O(1)     │
│ pop from front     │ O(n)     │ O(1)     │
│ Index access [i]   │ O(1)     │ O(n)**   │
│ Slice [a:b]        │ O(k)     │ Not supp │
│ len()              │ O(1)     │ O(1)     │
│ Contains (in)      │ O(n)     │ O(n)     │
└────────────────────┴──────────┴──────────┘

* list.append is amortized O(1) — occasional resizing is O(n)
** deque middle access is O(n) — use list if you need random access
```

---

## OrderedDict — Dict That Remembers (and Cares About) Insertion Order

### The Surprise: Regular Dicts ARE Already Ordered (Python 3.7+)

Since Python 3.7, plain `dict` preserves insertion order. So `OrderedDict` might seem obsolete. It is not.
The difference is subtle but important: **OrderedDict has operations that regular dict simply does not offer.**

```python
# Regular dict: ordered but can't reorder
d = {"a": 1, "b": 2, "c": 3}
# No way to move "a" to the end, or "c" to the front.

from collections import OrderedDict
od = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
od.move_to_end("a")          # moves "a" to the back
# OrderedDict([('b', 2), ('c', 3), ('a', 1)])

od.move_to_end("a", last=False)  # moves "a" to the front
# OrderedDict([('a', 1), ('b', 2), ('c', 3)])
```

### `move_to_end` — Reorder Without Re-Creating

```python
from collections import OrderedDict

cache = OrderedDict()
cache["user:1"] = {"name": "Alice"}
cache["user:2"] = {"name": "Bob"}
cache["user:3"] = {"name": "Charlie"}

# Mark user:2 as recently used → move to end
cache.move_to_end("user:2")
# OrderedDict([('user:1', ...), ('user:3', ...), ('user:2', ...)])
# user:2 is now "most recently used"

# The least recently used is now at the front:
cache.move_to_end("user:1", last=False)
# Explicitly demote user:1 to "oldest" position
```

### `popitem` — FIFO or LIFO Removal

Regular dict's `popitem()` removes the last inserted item (LIFO). OrderedDict's version accepts a `last`
argument that enables FIFO — something a plain dict cannot do:

```python
od = OrderedDict([("first", 1), ("second", 2), ("third", 3)])

od.popitem(last=True)    # ("third", 3)   ← removes last  (LIFO, same as dict)
od.popitem(last=False)   # ("first", 1)   ← removes first (FIFO, unique to OrderedDict)
```

### Order-Aware Equality

This is the most surprising difference. Two regular dicts with the same keys and values are equal regardless
of insertion order. Two OrderedDicts are equal **only if the key order also matches**:

```python
# Regular dict — order doesn't matter for equality
{"a": 1, "b": 2} == {"b": 2, "a": 1}   # True

# OrderedDict — order DOES matter for equality
from collections import OrderedDict
od1 = OrderedDict([("a", 1), ("b", 2)])
od2 = OrderedDict([("b", 2), ("a", 1)])
od1 == od2   # False  ← same contents, different order = NOT equal
```

### LRU Cache Implementation

OrderedDict is the classic building block for a manual LRU (Least Recently Used) cache:

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()   # ← ordered: oldest at front, newest at back

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)  # ← mark as recently used
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)   # ← evict least recently used (front)
```

### Use Cases

```python
# Guaranteed key order in an API response (e.g., JSON field ordering)
from collections import OrderedDict

response = OrderedDict([
    ("status", "ok"),
    ("timestamp", "2025-01-01T00:00:00Z"),
    ("data", [1, 2, 3]),
])
# Serializing this to JSON preserves field order — important for spec-compliance

# Ordered config that can be reordered at runtime
config = OrderedDict([("timeout", 30), ("retries", 3), ("debug", False)])
config.move_to_end("debug", last=False)   # promote debug to first position
```

---

## ChainMap — Multiple Dicts as a Single Unified View

### The Problem It Solves

Imagine a configuration system with three layers:
1. Built-in defaults (lowest priority)
2. Environment variables (medium priority)
3. Command-line arguments (highest priority)

The naive approach: merge them with `{**defaults, **env, **cli}`. But merging creates a new dict — the
layers lose their identity. You can't tell which layer a value came from. You can't add a new layer at
runtime without re-merging everything.

**ChainMap** holds references to the original dicts and presents them as one view. No merging, no copying.
When you look up a key, it walks the chain in order and returns the first match.

```
ChainMap([cli_args, env_vars, defaults])
         │           │          │
         │           │          └─ searched third (lowest priority)
         │           └─ searched second
         └─ searched first (highest priority)
```

### Creation and Lookup

```python
from collections import ChainMap

defaults = {"color": "blue",  "debug": False, "timeout": 30}
env_vars = {"debug": True,    "host": "prod.server.com"}
cli_args = {"timeout": 60}

config = ChainMap(cli_args, env_vars, defaults)
# Lookup order: cli_args first, then env_vars, then defaults

config["timeout"]   # 60        ← from cli_args (highest priority)
config["debug"]     # True      ← from env_vars (cli_args doesn't have it)
config["color"]     # 'blue'    ← from defaults (neither cli nor env has it)
config["host"]      # 'prod.server.com'  ← from env_vars
```

### Writes Go to the First Dict Only

ChainMap does not merge — it only ever writes to the **first dict in the chain**. The lower layers remain
untouched:

```python
config["new_key"] = "value"   # ← writes to cli_args only
cli_args   # {'timeout': 60, 'new_key': 'value'}  ← updated
env_vars   # {'debug': True, 'host': 'prod.server.com'}  ← unchanged
defaults   # {'color': 'blue', 'debug': False, 'timeout': 30}  ← unchanged
```

### `.maps` — Access the Underlying Dicts

```python
config.maps
# [{'timeout': 60}, {'debug': True, 'host': 'prod.server.com'}, {'color': 'blue', ...}]

config.maps[0]   # cli_args dict — the first / highest priority layer
config.maps[-1]  # defaults dict — the last / lowest priority layer
```

### `.new_child` — Push a New Layer on Top

**`.new_child(m={})`** creates a new ChainMap with an empty dict (or provided dict) prepended. The
original ChainMap is unchanged — this is like entering a new scope:

```python
# Add a temporary override layer
scoped = config.new_child({"debug": False, "timeout": 5})
scoped["debug"]     # False  ← from the new child layer
scoped["color"]     # 'blue' ← falls through to defaults

config["debug"]     # True   ← original config unchanged
```

### `.parents` — ChainMap Without the First Dict

**`.parents`** is the inverse of `.new_child` — it returns the ChainMap with the first dict removed:

```python
config.parents
# ChainMap({'debug': True, 'host': 'prod.server.com'}, {'color': 'blue', ...})
# cli_args is gone; env_vars is now highest priority

config.parents["timeout"]   # 30  ← cli_args override is gone, defaults kicks in
```

### Layered Config Pattern

```python
from collections import ChainMap
import os
import argparse

# Built-in defaults
defaults = {
    "host": "localhost",
    "port": 8080,
    "debug": False,
    "workers": 4,
}

# Environment overrides
env_config = {
    k.lower().replace("app_", ""): v
    for k, v in os.environ.items()
    if k.startswith("APP_")
}

# CLI overrides
parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int)
parser.add_argument("--debug", action="store_true")
cli_config = {k: v for k, v in vars(parser.parse_args()).items() if v is not None}

# Combine — cli wins over env wins over defaults
config = ChainMap(cli_config, env_config, defaults)

config["port"]    # CLI port if provided, else env APP_PORT if set, else 8080
```

### Template Variable Scoping

ChainMap naturally models lexical scoping — inner scopes shadow outer scopes:

```python
from collections import ChainMap

global_scope  = {"x": 10, "y": 20}
outer_scope   = {"x": 99}            # ← shadows global x
inner_scope   = {"z": 5}

# "Enter" outer scope
env = ChainMap(outer_scope, global_scope)
env["x"]   # 99   ← outer_scope shadows global

# "Enter" inner scope
env = env.new_child(inner_scope)
env["x"]   # 99   ← still outer_scope (inner doesn't define x)
env["z"]   # 5    ← inner_scope

# "Exit" inner scope
env = env.parents
env["z"]   # KeyError — z is no longer in scope
```

---

## Performance Comparison — All collections Types

```
┌──────────────┬─────────────┬─────────────┬───────────────────────────────────────┐
│ Type         │ Insert      │ Lookup      │ Notes                                 │
├──────────────┼─────────────┼─────────────┼───────────────────────────────────────┤
│ Counter      │ O(1)        │ O(1)        │ Missing keys return 0                 │
│ defaultdict  │ O(1)        │ O(1)        │ Missing keys auto-initialize          │
│ namedtuple   │ O(1)        │ O(1) name   │ Immutable; index and name access      │
│ deque        │ O(1) ends   │ O(1) ends   │ O(n) for middle index access          │
│              │ O(n) middle │ O(n) middle │                                       │
│ OrderedDict  │ O(1)        │ O(1)        │ move_to_end is O(1)                   │
│ ChainMap     │ O(1)*       │ O(k)**      │ Writes to first dict only             │
└──────────────┴─────────────┴─────────────┴───────────────────────────────────────┘

* ChainMap insert is O(1) — goes to first dict
** ChainMap lookup is O(k * m) where k = number of dicts, m = lookup cost per dict
   In practice: O(k) for string keys in small configs (k is typically 2–5)
```

---

## Common Mistakes

```
┌─────────────────────────────────────┬─────────────────────────────────────────────────┐
│ Mistake                             │ Explanation                                     │
├─────────────────────────────────────┼─────────────────────────────────────────────────┤
│ Mutating deque while iterating      │ Causes RuntimeError (same as list mutation).    │
│                                     │ Collect changes, apply after iteration.         │
├─────────────────────────────────────┼─────────────────────────────────────────────────┤
│ Confusing namedtuple with dataclass │ namedtuple is immutable and tuple-based.        │
│                                     │ If you need to set fields after creation,       │
│                                     │ use @dataclass instead.                         │
├─────────────────────────────────────┼─────────────────────────────────────────────────┤
│ Expecting ChainMap mutation to      │ ChainMap writes ONLY to the first dict.         │
│ update all underlying dicts         │ config["x"] = 1 does NOT update lower layers.  │
├─────────────────────────────────────┼─────────────────────────────────────────────────┤
│ Assuming OrderedDict equality is    │ od1 == od2 is False if key order differs,       │
│ same as dict equality               │ even with identical contents.                   │
├─────────────────────────────────────┼─────────────────────────────────────────────────┤
│ Using deque when you need random    │ deque[n] is O(n). Use list if you frequently    │
│ index access                        │ access elements by index in the middle.         │
├─────────────────────────────────────┼─────────────────────────────────────────────────┤
│ namedtuple._replace misunderstood   │ _replace does NOT modify in place.              │
│                                     │ It returns a NEW namedtuple. Assign it.         │
│                                     │ p._replace(x=5)  →  p is still unchanged.      │
│                                     │ p = p._replace(x=5)  →  correct.               │
└─────────────────────────────────────┴─────────────────────────────────────────────────┘
```

---

## Navigation

- Previous: [theory.md](./theory.md) — Counter, defaultdict, deque, all built-in data types
- Next: [itertools_functools.md](./itertools_functools.md) — functional iteration tools
- Related: [01_python_fundamentals/theory.md](../01_python_fundamentals/theory.md) — Python foundations
