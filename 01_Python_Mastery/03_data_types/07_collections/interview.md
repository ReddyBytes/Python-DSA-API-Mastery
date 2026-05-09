# Interview Q&A — `collections` Module

---

## Basic (0–2 yr)

**Q: What is Counter and when would you use it?**

A: `Counter` is a `dict` subclass that counts hashable objects. You use it any time you need to
answer "how many times does X appear?" — word frequencies, character counts, histogram-building.
Missing keys return `0` instead of raising `KeyError`, and `most_common(n)` returns the top n
entries sorted by count. It also supports arithmetic: adding two Counters merges counts, and
subtracting drops non-positive results.

---

**Q: What is defaultdict? How is it different from dict.get()?**

A: `defaultdict` takes a factory function and calls it automatically when a missing key is first
accessed, storing the result. `dict.get(key, default)` returns a fallback value but does not store
it in the dict. The practical difference: with `defaultdict(list)` you can write
`d[key].append(val)` on a brand-new key without any guard; with `dict.get()` you would need
`d.setdefault(key, []).append(val)` or an explicit `if` check. `defaultdict` is cleaner for
grouping and accumulation patterns.

---

**Q: What is namedtuple and why use it instead of a plain tuple?**

A: `namedtuple` is a tuple subclass with named fields. `p = Point(3, 7)` lets you write `p.x`
instead of `p[0]` — the code is self-documenting and harder to break when field order changes.
It has identical memory usage and performance to a regular tuple because it is still a tuple
under the hood. Use it for lightweight read-only records where a full class would be overkill.

---

## Intermediate (2–5 yr)

**Q: When would you use deque instead of a list?**

A: Use `deque` when you need fast insertions or removals at both ends of the sequence.
`list.pop(0)` and `list.insert(0, x)` are O(n) because they shift all elements. `deque.popleft()`
and `deque.appendleft()` are O(1) because deque uses a doubly-linked structure internally.
Common use cases: BFS queues, undo/redo stacks, and bounded sliding windows via `maxlen`.
Avoid deque if you need random index access in the middle — that is O(n) on a deque but O(1) on
a list.

---

**Q: What is ChainMap used for?**

A: `ChainMap` holds references to multiple dicts and presents them as one unified view. Lookups
walk the chain in order and return the first match. Writes go to the first dict only — the other
layers are never modified. It is ideal for layered configuration (CLI args override env vars,
which override defaults), variable scoping in template engines, and any situation where you need
to merge configs without losing the ability to inspect or remove individual layers.

---

**Q: What is the difference between OrderedDict and a regular dict in Python 3.7+?**

A: Since Python 3.7, plain `dict` preserves insertion order. `OrderedDict` adds two operations
that `dict` does not have: `move_to_end(key, last=True/False)` reorders entries in O(1) without
re-creating the dict, and `popitem(last=False)` removes the first-inserted item (FIFO), which
plain `dict.popitem()` cannot do. `OrderedDict` also has order-aware equality — two
`OrderedDict` instances with identical key/value pairs but different insertion orders are not
equal, whereas two plain dicts would be.

---

## Advanced (5+ yr)

**Q: Implement an LRU cache using OrderedDict.**

A: The key insight is that `OrderedDict` maintains insertion order and exposes O(1) reordering.
The "most recently used" end is the back; the "least recently used" end is the front.

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)      # ← promote to MRU position
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)   # ← evict LRU
```

Both `get` and `put` are O(1). `move_to_end` relinks doubly-linked-list pointers without copying.
`functools.lru_cache` is the idiomatic choice for function-level caching, but this pattern is
required when you need a cache with custom logic (e.g., cache invalidation, metrics, TTL).

---

**Q: How does ChainMap differ from merging dicts with `{**a, **b}`?**

A: `{**a, **b}` creates a new dict — a snapshot. The original dicts are not referenced, so
changes to `a` or `b` after the merge are invisible. ChainMap holds live references, so mutations
to any underlying dict are immediately visible through the ChainMap. ChainMap also preserves layer
identity: `config.maps[0]` lets you inspect or replace exactly the CLI layer without touching the
others. The merge approach is simpler when you just need a final config snapshot; ChainMap is the
right choice when layers are dynamic or auditable.

---

[Back to theory](./theory.md) · [Practice](./practice.md)
