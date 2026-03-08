# Trie — Quick Reference Cheatsheet

## Core Structure

```
Trie storing: ["apple", "app", "apt", "bat"]

root
├── 'a' → node
│        └── 'p' → node
│                  ├── 'p' → node (end=True)  ← "app"
│                  │        └── 'l' → node
│                  │                  └── 'e' → node (end=True)  ← "apple"
│                  └── 't' → node (end=True)  ← "apt"
└── 'b' → node
         └── 'a' → node
                   └── 't' → node (end=True)  ← "bat"
```

Each node has:
- children: dict or array[26]
- is_end: bool (marks complete word)

---

## Complexity Table

| Operation     | Time   | Space  | Notes                          |
|---------------|--------|--------|--------------------------------|
| insert(word)  | O(m)   | O(m)   | m = word length                |
| search(word)  | O(m)   | O(1)   | Exact match                    |
| startsWith(p) | O(m)   | O(1)   | m = prefix length              |
| delete(word)  | O(m)   | O(1)   | Prune empty branches           |
| Build trie    | O(W*m) | O(W*m) | W = num words, m = avg length  |

Space: O(ALPHABET_SIZE * m * n) worst case — can be large.

---

## Implementation Templates

### Dict-Based (Flexible, Pythonic)

```python
class TrieNode:
    def __init__(self):
        self.children = {}          # char → TrieNode
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end               # must be complete word

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True                      # any word with this prefix exists
```

### Array-Based (26 Lowercase Letters — Faster)

```python
class TrieNode:
    def __init__(self):
        self.children = [None] * 26     # index = ord(ch) - ord('a')
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def _idx(self, ch):
        return ord(ch) - ord('a')

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            i = self._idx(ch)
            if not node.children[i]:
                node.children[i] = TrieNode()
            node = node.children[i]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            i = self._idx(ch)
            if not node.children[i]:
                return False
            node = node.children[i]
        return node.is_end

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            i = self._idx(ch)
            if not node.children[i]:
                return False
            node = node.children[i]
        return True
```

---

## Word Deletion Template

```python
def delete(self, word: str) -> None:
    def _delete(node, word, depth):
        if depth == len(word):
            if not node.is_end:
                return False            # word not in trie
            node.is_end = False
            return len(node.children) == 0  # can delete if no children

        ch = word[depth]
        if ch not in node.children:
            return False                # word not found
        should_delete_child = _delete(node.children[ch], word, depth + 1)

        if should_delete_child:
            del node.children[ch]
            return not node.is_end and len(node.children) == 0
        return False

    _delete(self.root, word, 0)
```

---

## Count Words with Prefix Template

```python
def count_words_with_prefix(self, prefix: str) -> int:
    node = self.root
    for ch in prefix:
        if ch not in node.children:
            return 0
        node = node.children[ch]
    return self._count_all(node)

def _count_all(self, node) -> int:
    count = 1 if node.is_end else 0
    for child in node.children.values():
        count += self._count_all(child)
    return count
```

---

## Word Search in Trie (with Wildcard '.')

```python
def search_with_wildcard(self, word: str) -> bool:
    def dfs(node, i):
        if i == len(word):
            return node.is_end
        ch = word[i]
        if ch == '.':
            return any(dfs(child, i+1) for child in node.children.values())
        if ch not in node.children:
            return False
        return dfs(node.children[ch], i+1)
    return dfs(self.root, 0)
```

---

## Auto-Complete Template

```python
def autocomplete(self, prefix: str) -> list:
    node = self.root
    for ch in prefix:
        if ch not in node.children:
            return []
        node = node.children[ch]
    results = []
    self._dfs_collect(node, prefix, results)
    return results

def _dfs_collect(self, node, current, results):
    if node.is_end:
        results.append(current)
    for ch, child in node.children.items():
        self._dfs_collect(child, current + ch, results)
```

---

## Compact Trie Using defaultdict

```python
# Ultra-compact: nested defaultdict (good for quick prototyping)
def make_trie():
    from collections import defaultdict
    return defaultdict(make_trie)

WORD_END = '#'
root = make_trie()

def insert(root, word):
    node = root
    for ch in word:
        node = node[ch]
    node[WORD_END] = {}

def search(root, word):
    node = root
    for ch in word:
        if ch not in node:
            return False
        node = node[ch]
    return WORD_END in node
```

---

## Trie vs HashMap Decision Guide

| Need                              | Use       | Reason                              |
|-----------------------------------|-----------|-------------------------------------|
| Exact match only                  | HashMap   | O(1) lookup, simpler                |
| Prefix queries (startsWith)       | Trie      | HashMap can't do prefix efficiently |
| Auto-complete / suggestions       | Trie      | Natural prefix traversal            |
| Count words with given prefix     | Trie      | DFS from prefix node                |
| Spell check / closest word        | Trie      | Explore neighbors during traversal  |
| IP routing / longest prefix match | Trie      | Bit-by-bit trie traversal           |
| Word frequency only               | HashMap   | Counter is O(1) per lookup          |
| Sorted word retrieval             | Trie      | DFS gives lexicographic order       |

---

## Trie Applications Quick List

```
- Auto-complete / search suggestions
- Spell checker
- IP routing (longest prefix match — binary trie)
- Word games (Boggle, Scrabble valid word check)
- DNS lookup
- Phone directory
- T9 keyboard prediction
- Genome / DNA sequence matching
- Aho-Corasick multi-pattern string search
```

---

## Common Mistakes

```
MISTAKE 1: Forgetting is_end flag
  "app" and "apple" share prefix — is_end distinguishes them
  search("app") must check is_end, not just path existence

MISTAKE 2: Confusing search() vs starts_with()
  search()      → must reach is_end=True
  starts_with() → only needs path to exist

MISTAKE 3: Using Trie when HashMap suffices
  If no prefix queries needed → use set/dict for O(1) lookup

MISTAKE 4: Memory overhead for sparse tries
  Array-based node wastes space if alphabet is large
  Use dict-based for Unicode or large character sets

MISTAKE 5: Not handling empty string
  insert("") → root.is_end = True
  Make sure your loop handles len(word) == 0

MISTAKE 6: Forgetting to prune in deletion
  Not removing empty nodes causes memory leak
  Check: no children AND not is_end → safe to delete
```

---

## Interview Signals → Use Trie

```
"autocomplete"                   → Trie + DFS collect
"prefix search / starts with"    → Trie startsWith
"word dictionary with search"    → Trie with wildcard DFS
"longest common prefix"          → Trie (find deepest single-child path)
"count words with prefix"        → Trie + count DFS
"replace words with root"        → Trie + greedy shortest prefix match
"stream of words, prefix queries" → Build Trie incrementally
```
