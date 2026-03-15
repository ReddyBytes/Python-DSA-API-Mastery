# Linked List — Real-World Usage

Linked lists are the backbone of several systems you use every day — your browser's
back button, your music player's previous track, and the LRU cache that makes Redis
fast. Here is where they actually appear in production code.

---

## 1. Browser History — Doubly Linked List for Back/Forward Navigation

Every browser (Chrome, Firefox, Safari) models the history of a single tab as a
doubly linked list. Each visited URL is a node. The "current" pointer sits somewhere
in the list. `back()` moves it left; `forward()` moves it right; visiting a new URL
inserts after the current node and discards everything to the right (you can no longer
go forward after navigating away).

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HistoryNode:
    url: str
    prev: Optional[HistoryNode] = field(default=None, repr=False)
    next: Optional[HistoryNode] = field(default=None, repr=False)


class BrowserHistory:
    """
    Mimics a single browser tab's history stack.
    Used by: Chrome, Firefox, Safari — any browser with back/forward buttons.
    """

    def __init__(self, homepage: str):
        self._current = HistoryNode(homepage)

    def visit(self, url: str) -> None:
        """Navigate to a new URL. Discards forward history."""
        node = HistoryNode(url, prev=self._current)
        self._current.next = node   # forward history beyond current is abandoned
        self._current = node

    def back(self, steps: int = 1) -> str:
        """Go back up to `steps` pages. Stops at the oldest entry."""
        for _ in range(steps):
            if self._current.prev is None:
                break
            self._current = self._current.prev
        return self._current.url

    def forward(self, steps: int = 1) -> str:
        """Go forward up to `steps` pages. Stops at the newest entry."""
        for _ in range(steps):
            if self._current.next is None:
                break
            self._current = self._current.next
        return self._current.url

    @property
    def current(self) -> str:
        return self._current.url


# --- Demo ---
browser = BrowserHistory("https://google.com")
browser.visit("https://github.com")
browser.visit("https://docs.python.org")
browser.visit("https://stackoverflow.com")

print(browser.back(1))      # https://docs.python.org
print(browser.back(1))      # https://github.com
print(browser.forward(1))   # https://docs.python.org

# Visiting a new page while mid-history discards forward entries
browser.visit("https://anthropic.com")
print(browser.forward(1))   # still https://anthropic.com — no forward history
print(browser.back(2))      # https://github.com
```

---

## 2. LRU Cache — Doubly Linked List + Hash Map

An LRU (Least Recently Used) cache evicts the item that was accessed least recently
when capacity is full. This is the exact eviction policy Redis uses by default
(`maxmemory-policy allkeys-lru`). CPU L1/L2 cache controllers implement hardware-level
LRU for the same reason: recently used data is likely to be needed again soon.

The trick: a doubly linked list orders items by recency (head = most recent,
tail = least recent). A hash map gives O(1) lookup. Together they give O(1) get and put.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class CacheNode:
    key: Any
    value: Any
    prev: Optional[CacheNode] = field(default=None, repr=False)
    next: Optional[CacheNode] = field(default=None, repr=False)


class LRUCache:
    """
    O(1) get and put.
    Used by: Redis (allkeys-lru policy), Memcached, CPU cache controllers,
             CDN edge nodes (Cloudflare, Fastly cache eviction).
    """

    def __init__(self, capacity: int):
        self._capacity = capacity
        self._map: Dict[Any, CacheNode] = {}

        # Sentinel head and tail — simplify edge cases (no null checks)
        self._head = CacheNode("HEAD", None)  # most-recently-used side
        self._tail = CacheNode("TAIL", None)  # least-recently-used side
        self._head.next = self._tail
        self._tail.prev = self._head

    # ---- internal helpers ------------------------------------------------

    def _remove(self, node: CacheNode) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_at_front(self, node: CacheNode) -> None:
        """Insert right after the head sentinel (most recently used position)."""
        node.next = self._head.next
        node.prev = self._head
        self._head.next.prev = node
        self._head.next = node

    # ---- public interface ------------------------------------------------

    def get(self, key: Any) -> Any:
        if key not in self._map:
            return -1
        node = self._map[key]
        self._remove(node)
        self._insert_at_front(node)   # mark as most recently used
        return node.value

    def put(self, key: Any, value: Any) -> None:
        if key in self._map:
            self._remove(self._map[key])
        node = CacheNode(key, value)
        self._map[key] = node
        self._insert_at_front(node)

        if len(self._map) > self._capacity:
            # Evict LRU: the node just before the tail sentinel
            lru = self._tail.prev
            self._remove(lru)
            del self._map[lru.key]

    def __repr__(self) -> str:
        items, node = [], self._head.next
        while node is not self._tail:
            items.append(f"{node.key}:{node.value}")
            node = node.next
        return f"LRUCache([{', '.join(items)}])  ← MRU ... LRU →"


# --- Demo: simulating a database query cache ---
cache = LRUCache(capacity=3)
cache.put("user:1", {"name": "Alice", "email": "alice@example.com"})
cache.put("user:2", {"name": "Bob",   "email": "bob@example.com"})
cache.put("user:3", {"name": "Carol", "email": "carol@example.com"})
print(cache)

cache.get("user:1")   # Alice accessed — moves to front
print(cache)

cache.put("user:4", {"name": "Dave", "email": "dave@example.com"})  # evicts user:2
print(cache)
print("user:2 →", cache.get("user:2"))   # -1, evicted
```

---

## 3. Undo / Redo in Text Editors

VS Code, Google Docs, and Vim all model edit history as a linked list of states (or
command objects). Each edit is a node. `Ctrl+Z` walks backward; `Ctrl+Y` / `Ctrl+Shift+Z`
walks forward. Making a new edit after an undo discards the redo branch, exactly like
browser history.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EditState:
    content: str
    prev: Optional[EditState] = field(default=None, repr=False)
    next: Optional[EditState] = field(default=None, repr=False)


class UndoManager:
    """
    Doubly linked list of document states.
    Used by: VS Code, Google Docs, Vim, Photoshop, any editor with Ctrl+Z.
    """

    def __init__(self):
        initial = EditState("")
        self._current = initial

    def type(self, text: str) -> None:
        """Append text and record a new state (discards redo history)."""
        new_content = self._current.content + text
        node = EditState(new_content, prev=self._current)
        self._current.next = node
        self._current = node

    def delete(self, n: int = 1) -> None:
        """Delete last n characters and record state."""
        new_content = self._current.content[:-n] if n > 0 else self._current.content
        node = EditState(new_content, prev=self._current)
        self._current.next = node
        self._current = node

    def undo(self) -> str:
        if self._current.prev is not None:
            self._current = self._current.prev
        return self._current.content

    def redo(self) -> str:
        if self._current.next is not None:
            self._current = self._current.next
        return self._current.content

    @property
    def content(self) -> str:
        return self._current.content


# --- Demo ---
editor = UndoManager()
editor.type("Hello")
editor.type(", World")
editor.type("!")
print(repr(editor.content))   # 'Hello, World!'

editor.undo()
print(repr(editor.content))   # 'Hello, World'
editor.undo()
print(repr(editor.content))   # 'Hello'

editor.redo()
print(repr(editor.content))   # 'Hello, World'

editor.type(" — Python")      # new branch; '!' is gone from redo history
print(repr(editor.content))   # 'Hello, World — Python'
editor.redo()
print(repr(editor.content))   # still 'Hello, World — Python'
```

---

## 4. OS Memory Management — Free List

The Linux kernel's slab allocator and early `malloc` implementations manage free
memory blocks using a free list: a linked list where each node IS the free block
(the metadata is stored at the start of the block itself). When `malloc` is called,
the allocator walks the list to find a block of sufficient size.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class MemoryBlock:
    """Represents a free block of memory. In a real allocator this
    header lives in the first few bytes of the block itself."""
    start_address: int
    size: int          # bytes
    next: Optional[MemoryBlock] = None


class FreeList:
    """
    Simplified first-fit free list allocator.
    Mirrors what early malloc implementations (dlmalloc, ptmalloc) do.
    Modern allocators add segregated free lists, coalescing, etc.
    """

    def __init__(self, total_memory: int):
        self._head = MemoryBlock(start_address=0, size=total_memory)

    def allocate(self, size: int) -> Optional[int]:
        """First-fit: return the start address of the first block that fits."""
        prev, curr = None, self._head
        while curr:
            if curr.size >= size:
                address = curr.start_address
                remaining = curr.size - size
                if remaining > 0:
                    # Split: leave the remainder as a smaller free block
                    new_block = MemoryBlock(
                        start_address=curr.start_address + size,
                        size=remaining,
                        next=curr.next,
                    )
                    if prev:
                        prev.next = new_block
                    else:
                        self._head = new_block
                else:
                    if prev:
                        prev.next = curr.next
                    else:
                        self._head = curr.next
                return address
            prev, curr = curr, curr.next
        return None   # out of memory

    def free(self, address: int, size: int) -> None:
        """Return a block to the free list (simplified, no coalescing)."""
        block = MemoryBlock(start_address=address, size=size, next=self._head)
        self._head = block

    def dump(self) -> None:
        curr, blocks = self._head, []
        while curr:
            blocks.append(f"[{curr.start_address}..{curr.start_address+curr.size-1}]")
            curr = curr.next
        print("Free list:", " -> ".join(blocks) if blocks else "(empty)")


# --- Demo ---
heap = FreeList(total_memory=1024)
heap.dump()                              # [0..1023]

addr_a = heap.allocate(256)             # allocate 256 bytes
addr_b = heap.allocate(128)
heap.dump()                             # [384..1023]
print(f"Allocated A at {addr_a}, B at {addr_b}")

heap.free(addr_a, 256)                  # free block A
heap.dump()                             # [0..255] -> [384..1023]

addr_c = heap.allocate(100)             # fits in the freed block A
print(f"Allocated C at {addr_c}")
heap.dump()                             # [100..255] -> [384..1023]
```

---

## 5. Music Playlist — Doubly Linked List for Next / Previous

Spotify, Apple Music, and every media player model a playlist as a doubly linked
list. `play_next()` advances the pointer forward; `play_prev()` steps back;
shuffling relinks the nodes in a random order without copying data.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
import random


@dataclass
class TrackNode:
    title: str
    artist: str
    duration_secs: int
    prev: Optional[TrackNode] = field(default=None, repr=False)
    next: Optional[TrackNode] = field(default=None, repr=False)

    def __str__(self) -> str:
        m, s = divmod(self.duration_secs, 60)
        return f'"{self.title}" by {self.artist} ({m}:{s:02d})'


class Playlist:
    def __init__(self, name: str):
        self.name = name
        self._head: Optional[TrackNode] = None
        self._tail: Optional[TrackNode] = None
        self._current: Optional[TrackNode] = None
        self._size = 0

    def append(self, title: str, artist: str, duration_secs: int) -> None:
        node = TrackNode(title, artist, duration_secs)
        if self._tail:
            self._tail.next = node
            node.prev = self._tail
            self._tail = node
        else:
            self._head = self._tail = node
        if self._current is None:
            self._current = node
        self._size += 1

    def play_next(self) -> Optional[TrackNode]:
        if self._current and self._current.next:
            self._current = self._current.next
        return self._current

    def play_prev(self) -> Optional[TrackNode]:
        if self._current and self._current.prev:
            self._current = self._current.prev
        return self._current

    def shuffle(self) -> None:
        """Collect all nodes, shuffle, and relink — O(n)."""
        nodes: List[TrackNode] = []
        node = self._head
        while node:
            nodes.append(node)
            node = node.next
        random.shuffle(nodes)
        for i, n in enumerate(nodes):
            n.prev = nodes[i - 1] if i > 0 else None
            n.next = nodes[i + 1] if i < len(nodes) - 1 else None
        self._head, self._tail = nodes[0], nodes[-1]
        self._current = self._head

    @property
    def now_playing(self) -> Optional[TrackNode]:
        return self._current


playlist = Playlist("Road Trip Mix")
playlist.append("Bohemian Rhapsody",  "Queen",        354)
playlist.append("Hotel California",   "Eagles",       391)
playlist.append("Stairway to Heaven", "Led Zeppelin", 482)
playlist.append("Smells Like Teen Spirit", "Nirvana", 301)

print("Now playing:", playlist.now_playing)
print("Next:",        playlist.play_next())
print("Next:",        playlist.play_next())
print("Previous:",    playlist.play_prev())
```

---

## 6. Polynomial Arithmetic — Each Term as a Node

Computer algebra systems (Mathematica, SymPy) represent sparse polynomials as linked
lists of (coefficient, exponent) pairs sorted by exponent. When adding two polynomials,
you merge two sorted linked lists — the same merge step as merge sort — in O(m + n).

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Term:
    coeff: float
    exp: int
    next: Optional[Term] = None

    def __str__(self) -> str:
        if self.exp == 0:
            return str(self.coeff)
        if self.exp == 1:
            return f"{self.coeff}x"
        return f"{self.coeff}x^{self.exp}"


class Polynomial:
    """Sparse polynomial stored as a sorted (descending exponent) linked list."""

    def __init__(self):
        self._head: Optional[Term] = None

    def insert_term(self, coeff: float, exp: int) -> None:
        if coeff == 0:
            return
        node = Term(coeff, exp)
        if self._head is None or exp > self._head.exp:
            node.next = self._head
            self._head = node
            return
        curr = self._head
        while curr.next and curr.next.exp >= exp:
            if curr.next.exp == exp:
                curr.next.coeff += coeff
                if curr.next.coeff == 0:
                    curr.next = curr.next.next
                return
            curr = curr.next
        node.next = curr.next
        curr.next = node

    def __add__(self, other: Polynomial) -> Polynomial:
        """Merge two sorted lists — O(m + n), same as merge sort's merge step."""
        result = Polynomial()
        a, b = self._head, other._head
        while a and b:
            if a.exp > b.exp:
                result.insert_term(a.coeff, a.exp); a = a.next
            elif b.exp > a.exp:
                result.insert_term(b.coeff, b.exp); b = b.next
            else:
                result.insert_term(a.coeff + b.coeff, a.exp)
                a, b = a.next, b.next
        while a:
            result.insert_term(a.coeff, a.exp); a = a.next
        while b:
            result.insert_term(b.coeff, b.exp); b = b.next
        return result

    def __str__(self) -> str:
        if self._head is None:
            return "0"
        parts, curr = [], self._head
        while curr:
            parts.append(str(curr))
            curr = curr.next
        return " + ".join(parts)


# p1 = 5x^3 + 4x^2 + 2x
# p2 = -5x^3 + 7x^2 + 3
p1 = Polynomial()
for c, e in [(5, 3), (4, 2), (2, 1)]:
    p1.insert_term(c, e)

p2 = Polynomial()
for c, e in [(-5, 3), (7, 2), (3, 0)]:
    p2.insert_term(c, e)

print("p1     =", p1)          # 5x^3 + 4x^2 + 2x
print("p2     =", p2)          # -5x^3 + 7x^2 + 3
print("p1+p2  =", p1 + p2)     # 11x^2 + 2x + 3  (x^3 terms cancel)
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
