# Practice — Python `collections` Module

Twelve questions covering Counter, defaultdict, namedtuple, deque, OrderedDict, and ChainMap.
Each question is self-contained — attempt it before opening the answer.

---


## 📋 Quick Index

| # | Concept | Level |
|---|---------|-------|
| [Q1](#q1) | counter-frequencies — Count Word Frequencies with Counter | 🟢 |
| [Q2](#q2) | counter-subtract — Subtract Two Counters | 🟡 |
| [Q3](#q3) | defaultdict-group — Group Words by First Letter | 🟢 |
| [Q4](#q4) | defaultdict-nested — Nested defaultdict for a 2D Grid | 🟡 |
| [Q5](#q5) | namedtuple-basic — Define a Point and Use `_asdict` | 🟢 |
| [Q6](#q6) | namedtuple-replace — Use `_replace` to Create a Modified Copy | 🟡 |
| [Q7](#q7) | deque-sliding-window — Implement a Sliding Window of Last N Items | 🟡 |
| [Q8](#q8) | deque-rotate — Rotate a Queue Efficiently | 🟡 |
| [Q9](#q9) | ordereddict-lru — Implement LRU Eviction with OrderedDict | 🟠 |
| [Q10](#q10) | chainmap-config — Implement Config Layering with ChainMap | 🟡 |
| [Q11](#q11) | pick-the-type — Pick the Right collections Type for Each Scenario | 🟡 |
| [Q12](#q12) | rewrite-grouping — Rewrite a Grouping Function Using defaultdict | 🟡 |

---

<a id="q1"></a>

### Q1 · counter-frequencies — Count Word Frequencies with Counter 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Given a list of words, use `Counter` to produce a frequency map and print the three most common
words with their counts.

```python
words = [
    "python", "is", "fast", "python", "is", "fun",
    "python", "fun", "fast", "fast", "is"
]
```

<details>
<summary>Hint</summary>
Pass the list directly to Counter. Then call one method to get the top N entries sorted by count.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter

words = [
    "python", "is", "fast", "python", "is", "fun",
    "python", "fun", "fast", "fast", "is"
]

freq = Counter(words)
# Counter({'fast': 3, 'python': 3, 'is': 3, 'fun': 2})

for word, count in freq.most_common(3):
    print(f"{word}: {count}")
# fast: 3
# python: 3
# is: 3

freq["missing"]   # 0  ← missing keys return 0, not KeyError
```

**Why:** `Counter` is a `dict` subclass with a default of 0. `most_common(n)` runs in O(n log n)
using a partial sort — faster than sorting the entire counter when n is small.
</details>

---

<a id="q2"></a>

### Q2 · counter-subtract — Subtract Two Counters 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


You have item counts before and after a sale. Use `Counter` arithmetic to find what was sold
(net decrease per item). Drop any items that ended up with zero or negative counts.

```python
before = Counter({"apples": 10, "bananas": 5, "cherries": 3})
after  = Counter({"apples":  4, "bananas": 5, "cherries": 7})
```

<details>
<summary>Hint</summary>
Counter subtraction with `-` drops non-positive results automatically. Use `.subtract()` if you
want to keep negatives.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter

before = Counter({"apples": 10, "bananas": 5, "cherries": 3})
after  = Counter({"apples":  4, "bananas": 5, "cherries": 7})

sold = before - after       # ← drops items with count <= 0
# Counter({'apples': 6})    — bananas: 0 dropped, cherries: -4 dropped

restocked = after - before
# Counter({'cherries': 4})  — items that increased

# For full signed diff, use subtract (modifies in place):
diff = Counter(before)
diff.subtract(after)
# Counter({'apples': 6, 'bananas': 0, 'cherries': -4})  — all values kept
```

**Why:** The `-` operator between Counters applies element-wise subtraction then filters out
non-positive values. `.subtract()` keeps negatives — useful when you need to see items that
were added, not just removed.
</details>

---

<a id="q3"></a>

### Q3 · defaultdict-group — Group Words by First Letter 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Given a list of words, group them into a dict where each key is a letter and each value is a list
of words starting with that letter. Use `defaultdict` — no `if key not in d` guards.

```python
words = ["apple", "avocado", "banana", "blueberry", "cherry", "apricot"]
```

<details>
<summary>Hint</summary>
`defaultdict(list)` creates an empty list for any new key automatically.
</details>

<details>
<summary>Answer</summary>

```python
from collections import defaultdict

words = ["apple", "avocado", "banana", "blueberry", "cherry", "apricot"]

groups = defaultdict(list)
for word in words:
    groups[word[0]].append(word)   # ← no KeyError on first access

# defaultdict(<class 'list'>, {
#   'a': ['apple', 'avocado', 'apricot'],
#   'b': ['banana', 'blueberry'],
#   'c': ['cherry']
# })

dict(groups)   # convert to plain dict if needed
```

**Why:** Without `defaultdict`, you would write `groups.setdefault(word[0], []).append(word)` or
an `if` guard on every iteration. `defaultdict(list)` eliminates that ceremony — the factory
function (`list`) is called automatically on first key access.
</details>

---

<a id="q4"></a>

### Q4 · defaultdict-nested — Nested defaultdict for a 2D Grid 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Create a nested `defaultdict` that lets you assign values to a 2D grid using `grid[row][col] = val`
without initialising any row first. Then read a value at a coordinate that was never written.

<details>
<summary>Hint</summary>
The outer `defaultdict` needs a factory that itself produces a `defaultdict`.
</details>

<details>
<summary>Answer</summary>

```python
from collections import defaultdict

# Outer: defaultdict whose missing keys create inner defaultdicts
grid = defaultdict(lambda: defaultdict(int))  # ← lambda returns new defaultdict(int)

grid[0][0] = 1
grid[0][1] = 2
grid[2][3] = 9

print(grid[0][0])    # 1
print(grid[2][3])    # 9
print(grid[5][5])    # 0  ← never set, returns int default (0)

# Practical: cell visit counter
visit_count = defaultdict(lambda: defaultdict(int))
events = [(0, 0), (1, 2), (0, 0), (1, 2), (1, 2)]
for r, c in events:
    visit_count[r][c] += 1
# {0: {0: 2}, 1: {2: 3}}
```

**Why:** Each missing outer key triggers the `lambda`, which instantiates a fresh `defaultdict(int)`
for that row. Accessing a missing inner key triggers `int` (returns 0). Two levels of auto-init
with zero boilerplate.
</details>

---

<a id="q5"></a>

### Q5 · namedtuple-basic — Define a Point and Use `_asdict` 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Define a `Point` namedtuple with fields `x` and `y`. Create an instance, access fields by name,
and convert it to a regular dict.

<details>
<summary>Hint</summary>
`namedtuple("TypeName", ["field1", "field2"])` defines the type. Instances support `.field` access
and `._asdict()`.
</details>

<details>
<summary>Answer</summary>

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])   # ← define the type once

p = Point(3, 7)

p.x        # 3   ← named access
p.y        # 7
p[0]       # 3   ← still a tuple: index access works
x, y = p   # unpacking works too

d = p._asdict()
# {'x': 3, 'y': 7}   ← plain dict, useful for JSON serialisation

print(p)
# Point(x=3, y=7)   ← readable repr, not (3, 7)
```

**Why:** `namedtuple` adds zero overhead compared to a plain tuple — it is a tuple subclass.
`_asdict()` returns an `OrderedDict` (Python < 3.8) or a regular `dict` (Python 3.8+).
</details>

---

<a id="q6"></a>

### Q6 · namedtuple-replace — Use `_replace` to Create a Modified Copy 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


You have an `Employee` namedtuple. An employee gets a promotion: same name and department, but a
new salary. Use `_replace` to produce the updated record without touching the original.

```python
Employee = namedtuple("Employee", ["name", "dept", "salary"])
alice = Employee("Alice", "Engineering", 95_000)
```

<details>
<summary>Hint</summary>
`_replace` returns a new instance — it does NOT modify the original. You must assign the result.
</details>

<details>
<summary>Answer</summary>

```python
from collections import namedtuple

Employee = namedtuple("Employee", ["name", "dept", "salary"])
alice = Employee("Alice", "Engineering", 95_000)

promoted = alice._replace(salary=110_000)   # ← returns NEW instance

print(alice)     # Employee(name='Alice', dept='Engineering', salary=95000)
print(promoted)  # Employee(name='Alice', dept='Engineering', salary=110000)

# Reassign if you want to "update" the variable:
alice = alice._replace(salary=110_000, dept="Senior Engineering")
```

Common mistake — forgetting to assign:

```python
alice._replace(salary=110_000)   # WRONG: result is discarded
alice.salary                     # still 95000
```

**Why:** namedtuples are immutable. `_replace` is the functional-style update: it copies all
fields into a new instance, substituting only the named fields you provide.
</details>

---

<a id="q7"></a>

### Q7 · deque-sliding-window — Implement a Sliding Window of Last N Items 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


Write a function `last_n(stream, n)` that consumes an iterable and returns the last `n` items seen.
Use `deque` with `maxlen`. Then demonstrate it on a sequence of 10 numbers keeping the last 3.

<details>
<summary>Hint</summary>
`deque(maxlen=n)` auto-discards the oldest item when a new one is appended to a full deque. No
manual eviction code needed.
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

def last_n(stream, n: int) -> list:
    window = deque(maxlen=n)    # ← fixed capacity; oldest dropped automatically
    for item in stream:
        window.append(item)
    return list(window)

result = last_n(range(10), 3)
# [7, 8, 9]

# Step-by-step trace for n=3:
window = deque(maxlen=3)
for i in range(6):
    window.append(i)
    print(list(window))
# [0]
# [0, 1]
# [0, 1, 2]
# [1, 2, 3]   ← 0 dropped
# [2, 3, 4]   ← 1 dropped
# [3, 4, 5]   ← 2 dropped
```

**Why:** `maxlen` makes the deque self-managing. There is no `if len > n: pop` logic. Every
`append` to a full deque atomically drops the leftmost (oldest) element — O(1) at both ends.
</details>

---

<a id="q8"></a>

### Q8 · deque-rotate — Rotate a Queue Efficiently 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Given the task queue below, rotate it so that the last two tasks move to the front (highest
priority). Do it with a single `deque` operation, not by slicing or rebuilding the list.

```python
tasks = ["email", "report", "backup", "cleanup", "deploy"]
# desired: ["backup", "cleanup", "deploy", "email", "report"]  — wait, that's rotate(3)
# actually: ["cleanup", "deploy", "email", "report", "backup"] — no, demonstrate rotate(2)
```

Show the result of `rotate(2)` and `rotate(-1)` on a simple example, then apply it to the task
queue.

<details>
<summary>Hint</summary>
`d.rotate(n)` shifts elements `n` positions to the right (last n move to front).
`d.rotate(-n)` shifts left (first n move to back).
</details>

<details>
<summary>Answer</summary>

```python
from collections import deque

# Simple example first
d = deque([1, 2, 3, 4, 5])
d.rotate(2)     # last 2 move to front
print(d)        # deque([4, 5, 1, 2, 3])

d.rotate(-1)    # first element moves to back
print(d)        # deque([5, 1, 2, 3, 4])

# Task queue: promote last 2 tasks to front
tasks = deque(["email", "report", "backup", "cleanup", "deploy"])
tasks.rotate(2)
print(list(tasks))
# ['cleanup', 'deploy', 'email', 'report', 'backup']
```

**Why:** `rotate(n)` is O(n) — each element shifts one step at a time — but it operates entirely
within the deque's internal doubly-linked structure without allocating new memory or copying the
whole sequence. It is more explicit and readable than `tasks = tasks[-2:] + tasks[:-2]`.
</details>

---

<a id="q9"></a>

### Q9 · ordereddict-lru — Implement LRU Eviction with OrderedDict 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Build a minimal `LRUCache` class with `get(key)` and `put(key, value)` methods using `OrderedDict`.
Capacity is fixed. On a `get`, mark the key as recently used. On a `put` that exceeds capacity,
evict the least recently used entry.

<details>
<summary>Hint</summary>
`move_to_end(key)` promotes a key to "most recently used" (back of order).
`popitem(last=False)` removes the front entry — the least recently used.
</details>

<details>
<summary>Answer</summary>

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()   # oldest at front, newest at back

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
            self.cache.popitem(last=False)   # ← evict LRU (front)

cache = LRUCache(3)
cache.put(1, "a"); cache.put(2, "b"); cache.put(3, "c")
cache.get(1)       # "a" — 1 moves to back (recently used)
cache.put(4, "d")  # capacity exceeded — evict 2 (LRU, now at front)
cache.get(2)       # -1  — 2 was evicted
```

**Why:** `move_to_end` is O(1) — it relinks pointers in the underlying doubly-linked list.
`popitem(last=False)` is O(1). The entire LRU implementation is O(1) per operation, which is
the optimal complexity for an LRU cache.
</details>

---

<a id="q10"></a>

### Q10 · chainmap-config — Implement Config Layering with ChainMap 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Build a config resolver that merges three layers: defaults (lowest priority), environment overrides
(medium), and runtime overrides (highest). Use `ChainMap` so that writing a new value only affects
the runtime layer — the defaults remain untouched.

<details>
<summary>Hint</summary>
`ChainMap(high_priority, medium, low_priority)` — lookups walk left to right. Writes go to the
first dict only.
</details>

<details>
<summary>Answer</summary>

```python
from collections import ChainMap

defaults = {"host": "localhost", "port": 8080, "debug": False, "timeout": 30}
env      = {"host": "prod.server.com", "debug": True}
runtime  = {"timeout": 60}

config = ChainMap(runtime, env, defaults)   # ← runtime wins, defaults loses

config["host"]     # 'prod.server.com'  — from env
config["timeout"]  # 60                 — from runtime
config["debug"]    # True               — from env
config["port"]     # 8080               — from defaults

# Write affects runtime layer only:
config["new_key"] = "value"
runtime   # {'timeout': 60, 'new_key': 'value'}   ← updated
defaults  # {'host': 'localhost', ...}             ← unchanged

# Inspect all layers:
config.maps    # [runtime, env, defaults]

# Temporarily add an even-higher-priority override:
scoped = config.new_child({"debug": False})
scoped["debug"]    # False  ← child layer wins
config["debug"]    # True   ← original config unchanged
```

**Why:** `ChainMap` holds references to the original dicts — no copying, no merging. This means
layered configs remain auditable (you can always inspect `config.maps[n]` to see which layer owns
a value), and reverting a layer is O(1) — just rebuild the ChainMap without that dict.
</details>

---

<a id="q11"></a>

### Q11 · pick-the-type — Pick the Right collections Type for Each Scenario 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


For each scenario below, name the best `collections` type and give a one-line reason.

1. Count how often each HTTP status code appears in a log file.
2. Group database rows by their `category` field without checking if the key exists first.
3. Store an (x, y, z) coordinate that should be readable by field name but never mutated.
4. Keep a fixed-size buffer of the last 100 log lines, auto-dropping older ones.
5. Build a configuration system where CLI args override environment, which overrides defaults.
6. Implement a cache that must evict the least recently used entry when full.

<details>
<summary>Hint</summary>
Match the access pattern to the type: counting → Counter, grouping → defaultdict, named immutable
record → namedtuple, bounded buffer → deque(maxlen), layered lookup → ChainMap, order-aware
eviction → OrderedDict.
</details>

<details>
<summary>Answer</summary>

| Scenario | Type | Reason |
|---|---|---|
| 1. HTTP status code counts | `Counter` | Counts hashable objects; missing keys return 0 |
| 2. Group rows by category | `defaultdict(list)` | Auto-init prevents KeyError on new categories |
| 3. Named (x, y, z) coordinate | `namedtuple` | Immutable, named fields, tuple performance |
| 4. Last 100 log lines | `deque(maxlen=100)` | Auto-drops oldest; O(1) append and eviction |
| 5. CLI / env / defaults config | `ChainMap` | Layered lookup, writes to first dict only |
| 6. LRU cache | `OrderedDict` | `move_to_end` + `popitem(last=False)` both O(1) |

**Why:** Each `collections` type encodes a specific access pattern. Matching the type to the
pattern eliminates boilerplate and often improves readability more than performance.
</details>

---

<a id="q12"></a>

### Q12 · rewrite-grouping — Rewrite a Grouping Function Using defaultdict 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Rewrite `group_by_dept` to use `defaultdict` instead of `setdefault`. Keep the same return type.

```python
def group_by_dept(employees: list[dict]) -> dict:
    result = {}
    for emp in employees:
        dept = emp["dept"]
        if dept not in result:
            result[dept] = []
        result[dept].append(emp["name"])
    return result
```

<details>
<summary>Hint</summary>
`defaultdict(list)` removes the need for the `if dept not in result` guard. The return type is
still a plain dict (convert with `dict()`).
</details>

<details>
<summary>Answer</summary>

```python
from collections import defaultdict

# Version 1: defaultdict replaces the if-guard
def group_by_dept(employees: list[dict]) -> dict:
    result = defaultdict(list)
    for emp in employees:
        result[emp["dept"]].append(emp["name"])   # ← no KeyError on new dept
    return dict(result)   # ← convert to plain dict for clean return type

# Version 2: setdefault (valid but verbose)
def group_by_dept_v2(employees: list[dict]) -> dict:
    result = {}
    for emp in employees:
        result.setdefault(emp["dept"], []).append(emp["name"])
    return result

# Test both
data = [
    {"name": "Alice", "dept": "Eng"},
    {"name": "Bob",   "dept": "Eng"},
    {"name": "Carol", "dept": "Sales"},
]
print(group_by_dept(data))
# {'Eng': ['Alice', 'Bob'], 'Sales': ['Carol']}
```

**Why prefer defaultdict:** The intent is clearer — `defaultdict(list)` declares up front "every
new key gets an empty list." `setdefault` achieves the same result but buries the initialisation
inside the append call, which is less readable at a glance.
</details>

---

## Navigation

- [Back to theory](./theory.md)
- [Practice locally](./practice_local.py)
- [Interview Q&A](./interview.md)
- [Parent folder practice](../practice.md)
