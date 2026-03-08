# Binary Search Trees — Real-World Usage

A Binary Search Tree keeps every left child smaller and every right child larger than
its parent. That single invariant gives you O(log n) insert, delete, and search — and
crucially, **sorted iteration in O(n)**. The sorted-iteration property is what
distinguishes BSTs from hash maps and makes them irreplaceable in databases,
compilers, and scheduling systems.

---

## 1. Database Indexes — B-Trees Power Every SQL Query

The B-tree (a generalized, disk-friendly BST) is the default index type in PostgreSQL,
MySQL InnoDB, SQLite, and Oracle. Every `ORDER BY`, `BETWEEN`, `<`, `>` query uses a
B-tree index. Hash indexes exist too, but they cannot serve range queries.

**Real company example:** Every `SELECT * FROM orders WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'`
at Shopify, Amazon, or any e-commerce platform uses a B-tree index on `created_at`.

```python
import bisect
import time
import random


class SortedIndex:
    """
    Simulates a single-column B-tree index using Python's bisect module.
    bisect maintains a sorted list with O(log n) search and O(n) insert
    (array insert cost); a real B-tree gets O(log n) insert too, but
    bisect is the closest pure-Python equivalent.
    """

    def __init__(self):
        self._keys: list[int] = []
        self._row_ids: list[int] = []  # parallel array: row_id for each key

    def insert(self, key: int, row_id: int) -> None:
        pos = bisect.bisect_left(self._keys, key)
        self._keys.insert(pos, key)
        self._row_ids.insert(pos, row_id)

    def range_query(self, lo: int, hi: int) -> list[int]:
        """
        O(log n + k) where k = number of results.
        This is the operation that makes B-trees invaluable:
        a hash map cannot answer range queries at all.
        """
        left  = bisect.bisect_left(self._keys, lo)
        right = bisect.bisect_right(self._keys, hi)
        return self._row_ids[left:right]

    def point_query(self, key: int) -> int | None:
        pos = bisect.bisect_left(self._keys, key)
        if pos < len(self._keys) and self._keys[pos] == key:
            return self._row_ids[pos]
        return None


def benchmark_range_query() -> None:
    N = 1_000_000
    idx = SortedIndex()

    # Simulate building an index on 'order_total' column
    print(f"Building index on {N:,} rows...")
    data = sorted(random.randint(1, 1_000_000) for _ in range(N))
    for i, val in enumerate(data):
        idx._keys.append(val)     # fast bulk-load (already sorted)
        idx._row_ids.append(i)

    # Range query: find all orders where total is between 50000 and 50100
    start = time.perf_counter()
    results = idx.range_query(50_000, 50_100)
    elapsed = time.perf_counter() - start

    print(f"Range query [50000, 50100]: {len(results)} rows in {elapsed*1000:.3f} ms")
    print(f"O(log {N:,}) = ~{N.bit_length()} comparisons to find start position")


if __name__ == "__main__":
    benchmark_range_query()
```

---

## 2. Python's `sortedcontainers` — Production BST in Pure Python

The `sortedcontainers` library is used by Google, Instagram, and Palantir. It provides
`SortedList`, `SortedDict`, and `SortedSet` backed by a B-tree-like structure. It
outperforms naive sorted lists because it uses a list-of-lists (128-element buckets)
giving O(log n) amortised insert while keeping cache-friendly memory layout.

```python
# pip install sortedcontainers
from sortedcontainers import SortedList, SortedDict
import time
import random


def demo_sorted_list() -> None:
    sl = SortedList()
    words = ["banana", "apple", "cherry", "date", "elderberry", "fig", "grape"]
    for w in words:
        sl.add(w)

    print("SortedList after inserts:", list(sl))

    # bisect_left: position where 'cherry' would be inserted
    pos = sl.bisect_left("cherry")
    print(f"bisect_left('cherry') = {pos}  →  sl[{pos}] = '{sl[pos]}'")

    # irange: iterator over all words in alphabetical range [c, f]
    print("irange('c', 'f'):", list(sl.irange("c", "f")))

    # Remove
    sl.remove("banana")
    print("After removing 'banana':", list(sl))


def benchmark_vs_plain_list(n: int = 100_000) -> None:
    """
    Show the cost of keeping a plain list sorted vs SortedList.
    Plain list: insert is O(n) because of array shifting.
    SortedList: insert is O(log n) amortised.
    """
    vals = [random.randint(0, 1_000_000) for _ in range(n)]

    # Plain sorted list with bisect.insort
    import bisect
    plain: list[int] = []
    t0 = time.perf_counter()
    for v in vals:
        bisect.insort(plain, v)
    t_plain = time.perf_counter() - t0

    # SortedList
    sl = SortedList()
    t0 = time.perf_counter()
    for v in vals:
        sl.add(v)
    t_sorted = time.perf_counter() - t0

    print(f"\nInserting {n:,} elements:")
    print(f"  bisect.insort (plain list): {t_plain:.3f}s  — O(n) per insert due to shifting")
    print(f"  SortedList:                {t_sorted:.3f}s  — O(log n) amortised")


if __name__ == "__main__":
    demo_sorted_list()
    benchmark_vs_plain_list()
```

---

## 3. Auto-Complete / Type-Ahead — Sorted Iteration for Prefix Search

Every search box that shows suggestions as you type ("type-ahead") must efficiently
find all words that start with a given prefix. A BST gives this for free: an in-order
range query `[prefix, prefix + '\xff']` returns all matching words in alphabetical
order without scanning the entire dictionary.

**Real company example:** Elasticsearch's "search-as-you-type" field type and Redis's
sorted sets (backed by a skip list — probabilistic BST equivalent) both power
auto-complete at companies like GitHub, Stack Overflow, and Slack.

```python
from sortedcontainers import SortedList


class AutoComplete:
    """
    BST-backed auto-complete dictionary.
    Supports O(log n) insert and O(log n + k) prefix search
    where k = number of results returned.
    """

    def __init__(self, words: list[str] | None = None):
        self._sl = SortedList(words or [])

    def add_word(self, word: str) -> None:
        self._sl.add(word.lower())

    def suggest(self, prefix: str, limit: int = 5) -> list[str]:
        """
        Return up to `limit` words that start with `prefix`.

        The trick: all words starting with 'app' lie in the
        BST range ['app', 'apq') — the next string after 'app'
        when you increment the last character.
        """
        prefix = prefix.lower()
        # Upper bound: increment last character (e.g. 'app' → 'apq')
        upper = prefix[:-1] + chr(ord(prefix[-1]) + 1) if prefix else None
        if upper:
            matches = self._sl.irange(prefix, upper, exclusive=(False, True))
        else:
            matches = iter(self._sl)
        return [w for _, w in zip(range(limit), matches)]

    def in_range(self, start: str, end: str) -> list[str]:
        """Return all words alphabetically between start and end (inclusive)."""
        return list(self._sl.irange(start, end))


if __name__ == "__main__":
    dictionary = [
        "apple", "application", "apply", "apt", "banana", "band",
        "bandwidth", "cherry", "chart", "chapter", "append", "approach",
    ]
    ac = AutoComplete(dictionary)
    ac.add_word("appetizer")

    print("Suggestions for 'app':", ac.suggest("app"))
    print("Suggestions for 'ban':", ac.suggest("ban"))
    print("Alphabetical range ['ap', 'aq'):", ac.in_range("ap", "aq"))
```

---

## 4. Calendar Booking — Interval Tree / BST for Conflict Detection

Any booking or reservation system must check whether a new time slot overlaps with
existing bookings. Storing events in a BST sorted by start time lets you find
potential conflicts in O(log n) instead of scanning every existing booking.

**Real company example:** Google Calendar, Calendly, and healthcare scheduling systems
at companies like Epic all use interval-tree variants to detect double-bookings.

```python
from sortedcontainers import SortedList
from dataclasses import dataclass


@dataclass
class Event:
    start: int   # minutes since midnight for simplicity
    end:   int
    title: str

    def overlaps(self, other: "Event") -> bool:
        return self.start < other.end and other.start < self.end


class CalendarBooking:
    """
    Booking system using a SortedList (BST) keyed by start time.
    - add_event: O(log n) insert + O(k) overlap scan (k = nearby events)
    - is_free:   O(log n + k)

    A production system would use a full interval tree (augmented BST
    storing max_end at each node) for O(log n) overlap detection.
    """

    def __init__(self):
        # SortedList of (start, end, title) tuples
        self._events: SortedList = SortedList(key=lambda e: e.start)

    def is_free(self, start: int, end: int) -> bool:
        candidate = Event(start, end, "")
        # Only events whose start < candidate.end can possibly overlap.
        # Find first event that starts at or after candidate.start - max_duration.
        # For simplicity: scan backwards from first event starting after candidate.start.
        idx = self._events.bisect_key_left(start)
        # Check overlaps going forward
        for i in range(max(0, idx - 1), len(self._events)):
            ev = self._events[i]
            if ev.start >= end:
                break          # no more overlaps possible
            if candidate.overlaps(ev):
                return False
        return True

    def add_event(self, start: int, end: int, title: str) -> bool:
        if not self.is_free(start, end):
            print(f"  CONFLICT: '{title}' ({start}-{end}) overlaps an existing booking.")
            return False
        self._events.add(Event(start, end, title))
        print(f"  BOOKED:   '{title}' ({start}-{end})")
        return True

    def events_on_day(self) -> list[Event]:
        return list(self._events)


def fmt(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


if __name__ == "__main__":
    cal = CalendarBooking()
    # Times in minutes since midnight
    cal.add_event(540,  600,  "Team standup")         # 09:00–10:00
    cal.add_event(600,  660,  "Architecture review")  # 10:00–11:00
    cal.add_event(660,  720,  "Lunch")                # 11:00–12:00
    cal.add_event(570,  630,  "Conflicting meeting")  # 09:30–10:30 → conflict!
    cal.add_event(720,  780,  "1:1 with manager")     # 12:00–13:00

    print("\nCalendar for today:")
    for ev in cal.events_on_day():
        print(f"  {fmt(ev.start)}–{fmt(ev.end)}  {ev.title}")
```

---

## 5. Symbol Tables in Compilers — Scoped Variable Lookup

Compilers and interpreters use a **stack of symbol tables** — one per scope — where
each table is an ordered map (BST). When you declare a variable it is inserted into
the current scope's BST. Lookup walks the stack from innermost to outermost scope.
Python's `locals()` / `globals()` / built-ins chain is exactly this structure.

**Real company example:** CPython's frame objects implement this stack. The V8
JavaScript engine (used in Node.js / Chrome) uses scope chains backed by ordered maps.

```python
from sortedcontainers import SortedDict


class SymbolTable:
    """
    Lexically-scoped symbol table backed by SortedDict (BST).
    Supports nested scopes (function bodies, if blocks, loops).

    Operations:
      push_scope()  — enter a new block
      pop_scope()   — leave current block
      define(name)  — add symbol to current scope
      lookup(name)  — search from innermost scope outward  O(S * log n)
    """

    def __init__(self):
        self._scopes: list[SortedDict] = [SortedDict()]  # global scope

    def push_scope(self) -> None:
        self._scopes.append(SortedDict())

    def pop_scope(self) -> SortedDict:
        if len(self._scopes) == 1:
            raise RuntimeError("Cannot pop global scope")
        return self._scopes.pop()

    def define(self, name: str, value) -> None:
        self._scopes[-1][name] = value

    def lookup(self, name: str):
        """Walk from innermost scope outward — same as Python's LEGB rule."""
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        raise NameError(f"'{name}' is not defined")

    def all_visible_names(self) -> list[str]:
        """
        Returns sorted list of all names visible in the current scope.
        Sorted order comes for free because each scope is a SortedDict (BST).
        """
        seen = set()
        names = []
        for scope in reversed(self._scopes):
            for name in scope:
                if name not in seen:
                    names.append(name)
                    seen.add(name)
        return sorted(names)

    def scope_depth(self) -> int:
        return len(self._scopes)


if __name__ == "__main__":
    st = SymbolTable()

    # Global scope
    st.define("PI", 3.14159)
    st.define("MAX_SIZE", 1024)

    # Enter function scope
    st.push_scope()
    st.define("x", 10)
    st.define("y", 20)

    # Enter inner block scope
    st.push_scope()
    st.define("x", 99)   # shadows outer x
    st.define("z", 30)

    print(f"Scope depth: {st.scope_depth()}")
    print(f"lookup('x')        = {st.lookup('x')}")    # 99  (inner)
    print(f"lookup('y')        = {st.lookup('y')}")    # 20  (function scope)
    print(f"lookup('PI')       = {st.lookup('PI')}")   # 3.14159 (global)
    print(f"All visible names: {st.all_visible_names()}")

    st.pop_scope()   # leave inner block
    print(f"\nAfter pop — lookup('x') = {st.lookup('x')}")  # 10 (outer x restored)

    try:
        st.lookup("z")
    except NameError as e:
        print(f"NameError: {e}")   # z no longer in scope
```

---

## 6. `SortedDict` as Python's TreeMap Equivalent

Java's `TreeMap` and C++'s `std::map` are ordered BSTs that give O(log n) on all
operations. Python's built-in `dict` is a hash map — unordered, O(1) average, but
no range queries. `sortedcontainers.SortedDict` fills this gap.

**Real company example:** Apache Kafka's log segment index and RocksDB's memtable use
ordered maps exactly like `TreeMap` for offset lookups. Redis's `ZRANGEBYSCORE`
is implemented with a skip list (same asymptotic complexity as a BST).

```python
from sortedcontainers import SortedDict
import time
import random


def demo_sorted_dict() -> None:
    # Simulates a Redis ZSET — score → member mapping
    leaderboard: SortedDict = SortedDict()

    players = {"alice": 4200, "bob": 3800, "carol": 5100,
               "dave": 4900, "eve": 3200, "frank": 4500}
    for player, score in players.items():
        leaderboard[score] = player

    # Top-3 players: iterate in reverse O(k)
    print("Top-3 players:")
    for score, name in reversed(leaderboard.items()):
        print(f"  {name}: {score}")
        if score <= leaderboard.peekitem(-3)[0]:
            break

    # Range query: players with scores between 4000 and 5000
    from sortedcontainers import SortedKeysView
    keys_in_range = leaderboard.irange(4000, 5000)
    print("\nPlayers scoring 4000–5000:")
    for score in keys_in_range:
        print(f"  {leaderboard[score]}: {score}")

    # O(log n) rank lookup: what rank is alice?
    alice_score = players["alice"]
    rank = leaderboard.bisect_left(alice_score)
    print(f"\nalice's rank (0-indexed from bottom): {rank}")
    print(f"alice's rank (from top): {len(leaderboard) - rank}")


def compare_dict_vs_sorted_dict(n: int = 50_000) -> None:
    """
    Demonstrate what regular dict CANNOT do that SortedDict can.
    """
    data = {random.randint(0, 1_000_000): f"item_{i}" for i in range(n)}

    sd = SortedDict(data)

    # Range scan — impossible with dict without converting to sorted list first
    lo, hi = 400_000, 401_000
    t0 = time.perf_counter()
    result = list(sd.irange(lo, hi))
    t_bst = time.perf_counter() - t0

    t0 = time.perf_counter()
    result_dict = [k for k in data if lo <= k <= hi]
    t_dict = time.perf_counter() - t0

    print(f"\nRange scan [{lo}, {hi}] over {n:,} items:")
    print(f"  dict  (full scan): {t_dict*1000:.2f} ms  — O(n)")
    print(f"  SortedDict (BST):  {t_bst*1000:.2f} ms  — O(log n + k)")
    print(f"  Matches: {len(result)}")


if __name__ == "__main__":
    demo_sorted_dict()
    compare_dict_vs_sorted_dict()
```

---

## Summary Table

| Use Case | Data Structure | Key Operation | Real Product |
|---|---|---|---|
| Database index | B-tree (BST generalisation) | Range query O(log n + k) | PostgreSQL, MySQL, SQLite |
| Sorted collections | SortedList (BST) | Add/remove/irange | Instagram, Palantir |
| Auto-complete | SortedList | Prefix range O(log n + k) | Elasticsearch, Redis ZSET |
| Calendar booking | SortedList + interval logic | Overlap check O(log n) | Google Calendar, Calendly |
| Symbol tables | Stack of SortedDict | Scoped lookup O(S log n) | CPython, V8, GCC |
| Ordered map | SortedDict (TreeMap equiv.) | Range scan / rank | Kafka, RocksDB, Redis |

The unifying theme: **whenever you need both fast lookup AND sorted/range access, a
BST is the answer**. Hash maps give O(1) lookup but cannot answer "give me everything
between X and Y". BSTs give O(log n) for all three: insert, delete, and range query.
