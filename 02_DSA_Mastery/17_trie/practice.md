# 💻 Trie — Practice

> 25 questions covering trie node structure, core operations, classic interview problems, and design tradeoffs — from inserting a single word to building a full autocomplete system.

---

## Quick Index

| # | Difficulty | Topic |
|---|---|---|
| [Q1](#q1) | 🟢 Basic | Trie node structure — dict approach |
| [Q2](#q2) | 🟢 Basic | Trie node structure — array approach |
| [Q3](#q3) | 🟢 Basic | Insert a word |
| [Q4](#q4) | 🟢 Basic | Search for an exact word |
| [Q5](#q5) | 🟢 Basic | startsWith — prefix check |
| [Q6](#q6) | 🟢 Basic | search vs startsWith — the is_end distinction |
| [Q7](#q7) | 🟢 Basic | Handling the empty string |
| [Q8](#q8) | 🟢 Basic | Why trie wins over hashmap on prefix queries |
| [Q9](#q9) | 🟡 Intermediate | Count words with a given prefix |
| [Q10](#q10) | 🟡 Intermediate | Delete a word with branch pruning |
| [Q11](#q11) | 🟡 Intermediate | Autocomplete system |
| [Q12](#q12) | 🟡 Intermediate | Longest common prefix |
| [Q13](#q13) | 🟡 Intermediate | Replace words with root |
| [Q14](#q14) | 🟡 Intermediate | Memory usage — dict vs array node |
| [Q15](#q15) | 🟡 Intermediate | Trie vs hashmap — prefix search benchmark |
| [Q16](#q16) | 🟡 Intermediate | Implement full Trie class from scratch |
| [Q17](#q17) | 🟡 Intermediate | Wildcard search with dot (.) |
| [Q18](#q18) | 🟡 Intermediate | Count distinct words in a trie |
| [Q19](#q19) | 🟡 Intermediate | Lexicographic order — collect all words |
| [Q20](#q20) | 🟡 Intermediate | Trie from a stream of strings |
| [Q21](#q21) | 🔴 Advanced | Word search in grid — trie + DFS |
| [Q22](#q22) | 🔴 Advanced | Top-K autocomplete with frequency ranking |
| [Q23](#q23) | 🔴 Advanced | Trie memory analysis — when trie uses more than hashmap |
| [Q24](#q24) | 🔴 Advanced | Design a search suggestion system |
| [Q25](#q25) | 🔴 Advanced | Common mistake gauntlet |

---

<a id="q1"></a>
### Q1 🟢 · Trie node structure — dict approach

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

**Problem:** Define a `TrieNode` class using a Python `dict` for children. Explain what the `is_end` flag does and why it is required. Then manually build the trie for words `["cat", "car"]` by creating nodes and linking them — no insert method, just direct node construction.

<details>
<summary>💡 Hint</summary>

Each node needs two things: a `children` dict mapping `char → TrieNode`, and `is_end: bool`. The node for `'t'` at the end of "cat" should have `is_end = True`. The node for `'a'` (shared between "cat" and "car") should have `is_end = False`.
</details>

<details>
<summary>✅ Answer</summary>

```python
class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end: bool = False

# Manual construction for ["cat", "car"]
root = TrieNode()
c = TrieNode(); root.children['c'] = c
a = TrieNode(); c.children['a'] = a
t = TrieNode(); t.is_end = True; a.children['t'] = t
r = TrieNode(); r.is_end = True; a.children['r'] = r

# Verify
assert root.children['c'].children['a'].children['t'].is_end is True   # "cat"
assert root.children['c'].children['a'].children['r'].is_end is True   # "car"
assert root.children['c'].children['a'].is_end is False                # "ca" is not a word
```

**Why:** `is_end` is the critical marker that distinguishes a complete word from a prefix that happens to exist in the trie. Without it, searching for "ca" would incorrectly return True. The `children` dict uses only as many slots as characters that actually exist, making it memory-efficient for large or sparse alphabets.

**Time:** O(1) node creation. **Space:** O(total characters) for the full trie.
</details>

---

<a id="q2"></a>
### Q2 🟢 · Trie node structure — array approach

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

**Problem:** Define a `TrieNode` class using a fixed-size array of 26 slots (lowercase English only). Implement a helper `_idx(ch)` that converts a character to its array index. Show what index `'a'`, `'m'`, and `'z'` map to. Explain when to prefer array over dict.

<details>
<summary>💡 Hint</summary>

The index formula is `ord(ch) - ord('a')`. This gives `'a' → 0`, `'b' → 1`, ..., `'z' → 25`. Each slot is either `None` (child absent) or a `TrieNode`. The array approach is O(1) guaranteed and cache-friendly, but always allocates 26 slots even if a node has only one child.
</details>

<details>
<summary>✅ Answer</summary>

```python
class TrieNode:
    def __init__(self):
        self.children: list = [None] * 26
        self.is_end: bool = False

def _idx(ch: str) -> int:
    return ord(ch) - ord('a')

# Index mapping
assert _idx('a') == 0
assert _idx('m') == 12
assert _idx('z') == 25

# Using the array node
root = TrieNode()
root.children[_idx('c')] = TrieNode()   # create 'c' child at index 2
print(root.children[2])                 # TrieNode object
print(root.children[0])                 # None — 'a' child doesn't exist
```

**Why:** Array nodes give guaranteed O(1) lookup (direct indexing, no hash computation) and are cache-friendly since all 26 pointers sit in contiguous memory. Use array when the alphabet is fixed and small (e.g., lowercase English in LeetCode problems). Use dict when the alphabet is large (Unicode, URLs, mixed case) to avoid wasting 26 × node_size bytes per node on empty slots.

**Time:** O(1) index lookup. **Space:** O(26) = O(1) per node, but 26× wasteful for sparse nodes.
</details>

---

<a id="q3"></a>
### Q3 🟢 · Insert a word

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

**Problem:** Implement `insert(word: str)` on a `Trie` class. Walk character by character, creating nodes when they don't exist, and mark `is_end = True` after the last character. Insert `["apple", "app", "apt"]` and verify the trie is correct.

<details>
<summary>💡 Hint</summary>

The pattern is always the same: `node = self.root`, then for each character check if it's in `node.children` — create if missing — then advance. After the loop, set `node.is_end = True`. The loop touches exactly L nodes for a word of length L.
</details>

<details>
<summary>✅ Answer</summary>

```python
class TrieNode:
    def __init__(self):
        self.children = {}
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

trie = Trie()
for w in ["apple", "app", "apt"]:
    trie.insert(w)

# "app" and "apple" share a→p→p; "apt" branches at the second level
pp_node = trie.root.children['a'].children['p'].children['p']
assert pp_node.is_end is True      # "app" ends here
assert pp_node.children['l']       # "apple" continues from here

pt_node = trie.root.children['a'].children['p'].children['t']
assert pt_node.is_end is True      # "apt" ends here
```

**Why:** Creating nodes on-demand (rather than pre-allocating) keeps the trie lean — only characters that actually appear in inserted words create nodes. Inserting "apple" after "app" reuses the `a→p→p` path and just extends it with `l→e`.

**Time:** O(L) per insert (L = word length). **Space:** O(L) new nodes in the worst case per insert (all characters are new).
</details>

---

<a id="q4"></a>
### Q4 🟢 · Search for an exact word

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

**Problem:** Implement `search(word: str) -> bool` that returns `True` only if the exact word was inserted. After inserting `["cat", "car"]`, verify that `search("cat")` is `True`, `search("ca")` is `False`, and `search("cab")` is `False`.

<details>
<summary>💡 Hint</summary>

Walk the trie following the characters. If any character is missing from `node.children`, return `False` immediately. After consuming all characters, return `node.is_end` — not `True`. The node existing is not enough; the word must have ended there.
</details>

<details>
<summary>✅ Answer</summary>

```python
def search(self, word: str) -> bool:
    node = self.root
    for ch in word:
        if ch not in node.children:
            return False
        node = node.children[ch]
    return node.is_end   # must be a word-end, not just a path

trie = Trie()
trie.insert("cat")
trie.insert("car")

assert trie.search("cat") is True    # complete word
assert trie.search("ca") is False    # prefix only
assert trie.search("cab") is False   # path breaks at 'b'
assert trie.search("cats") is False  # path breaks at 's'
```

**Why:** `node.is_end` is what separates "cat" from "ca". Both paths exist in the trie (after inserting "cat"), but only the `'t'` node has `is_end = True`. Returning `True` just because the node exists is the single most common trie bug — it turns `search()` into `starts_with()`.

**Time:** O(L). **Space:** O(1).
</details>

---

<a id="q5"></a>
### Q5 🟢 · startsWith — prefix check

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

**Problem:** Implement `starts_with(prefix: str) -> bool` that returns `True` if any inserted word starts with the given prefix. After inserting `["cat", "car", "dog"]`, verify `starts_with("ca")` is `True`, `starts_with("do")` is `True`, and `starts_with("dx")` is `False`. Explain how this differs from `search()`.

<details>
<summary>💡 Hint</summary>

The traversal is identical to `search()` — walk the characters. The only difference is the return value: for `starts_with`, return `True` the moment you've consumed all prefix characters and a node exists at that position. You do NOT check `is_end`.
</details>

<details>
<summary>✅ Answer</summary>

```python
def starts_with(self, prefix: str) -> bool:
    node = self.root
    for ch in prefix:
        if ch not in node.children:
            return False
        node = node.children[ch]
    return True   # path exists → some word starts with this prefix

trie = Trie()
for w in ["cat", "car", "dog"]:
    trie.insert(w)

assert trie.starts_with("ca") is True
assert trie.starts_with("cat") is True    # full word is also a valid prefix
assert trie.starts_with("do") is True
assert trie.starts_with("dx") is False
assert trie.starts_with("") is True       # empty prefix matches everything

# Key difference from search:
assert trie.search("ca") is False         # "ca" was never inserted
assert trie.starts_with("ca") is True     # but "ca" is a valid prefix
```

**Why:** `search` checks whether the word was explicitly inserted (node exists AND `is_end = True`). `starts_with` only asks whether any word begins with the given characters (node exists, period). The empty string edge case: since no characters fail to match, the loop exits immediately and returns `True` — every word trivially starts with the empty string.

**Time:** O(P) where P = prefix length. **Space:** O(1).
</details>

---

<a id="q6"></a>
### Q6 🟢 · search vs startsWith — the is_end distinction

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

**Problem:** Insert `["app", "apple"]` into a trie. For each string in `["a", "ap", "app", "appl", "apple", "applet"]`, print whether `search()` and `starts_with()` return `True` or `False`. Explain every case.

<details>
<summary>💡 Hint</summary>

Build a truth table. A key case: `search("app")` should be `True` because "app" was explicitly inserted. `search("appl")` should be `False` — the path exists (as part of "apple") but no word ends at `'l'`. `starts_with("appl")` is `True` because the path `a→p→p→l` exists.
</details>

<details>
<summary>✅ Answer</summary>

```python
trie = Trie()
trie.insert("app")
trie.insert("apple")

checks = ["a", "ap", "app", "appl", "apple", "applet"]
for word in checks:
    s = trie.search(word)
    sw = trie.starts_with(word)
    print(f"  {word!r:8s}  search={s!s:5}  starts_with={sw}")

# a        search=False  starts_with=True
# ap       search=False  starts_with=True
# app      search=True   starts_with=True   ← "app" was inserted
# appl     search=False  starts_with=True   ← path exists but no is_end
# apple    search=True   starts_with=True   ← "apple" was inserted
# applet   search=False  starts_with=False  ← 't' node doesn't exist
```

**Why:** The pattern: `search = True` only at exact insertion points. `starts_with = True` for any prefix of any inserted word. `starts_with = False` only when the path breaks (a character is not present in `node.children`). The node for `'l'` in "appl" exists (it's the path to "apple") but `is_end` is `False` there — no word was explicitly marked as ending at that node.

**Time:** O(L) per operation. **Space:** O(1).
</details>

---

<a id="q7"></a>
### Q7 🟢 · Handling the empty string

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

**Problem:** Show what happens when you `insert("")` into a trie, then call `search("")` and `starts_with("")`. Does the implementation handle it correctly without any special-case code? Explain why.

<details>
<summary>💡 Hint</summary>

Trace through `insert("")`: the `for ch in word` loop iterates zero times, so execution goes directly to `node.is_end = True`. The root node itself gets marked as a word-end. The same happens with `search("")`: the loop does nothing, and `return node.is_end` returns `True` because root is now marked. For `starts_with("")`, the loop does nothing and `return True` fires immediately.
</details>

<details>
<summary>✅ Answer</summary>

```python
trie = Trie()
trie.insert("")

assert trie.search("") is True      # root.is_end = True after insert
assert trie.starts_with("") is True # always True — trivially correct

# Before inserting empty string:
trie2 = Trie()
trie2.insert("cat")
assert trie2.search("") is False        # root.is_end is still False
assert trie2.starts_with("") is True    # starts_with always returns True for ""
```

**Why:** The standard implementation handles `""` naturally with no special-case code. `insert("")` sets `root.is_end = True`. `search("")` returns `root.is_end`. `starts_with("")` returns `True` always (the loop body never executes). The important distinction: `starts_with("")` is `True` regardless of whether `""` was inserted, because every string trivially starts with the empty string.

**Time:** O(1) for all operations on `""`. **Space:** O(1) — no new nodes created.
</details>

---

<a id="q8"></a>
### Q8 🟢 · Why trie wins over hashmap on prefix queries

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

**Problem:** Given a list of 10 words starting with "ca" and 90 other words, count how many words start with "ca" using (a) a Python `set` and (b) a trie. For the set approach, iterate through all words and check each. For the trie, navigate to the "ca" node and count. Compare the complexity of each approach and explain when the trie advantage grows.

<details>
<summary>💡 Hint</summary>

The set must scan all N words and check whether each starts with "ca" — that's O(N × P) where P = prefix length. The trie navigates to the "ca" node in O(P) steps, then counts from there. The counting DFS is O(words_with_prefix). When N is large (millions of words) and P is short (2 characters), the trie is dramatically faster.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time

words = ["cat", "car", "cab", "cake", "call", "camp", "cape", "card", "care", "cart"] + \
        [f"word{i}" for i in range(90)]

# Approach A: set — O(N × P)
word_set = set(words)
def count_prefix_set(word_list, prefix):
    return sum(1 for w in word_list if w.startswith(prefix))

# Approach B: trie — O(P + result_count)
def count_prefix_trie(trie, prefix):
    node = trie.root
    for ch in prefix:
        if ch not in node.children:
            return 0
        node = node.children[ch]
    return _count_subtree(node)

def _count_subtree(node):
    count = 1 if node.is_end else 0
    for child in node.children.values():
        count += _count_subtree(child)
    return count

trie = Trie()
for w in words:
    trie.insert(w)

assert count_prefix_set(words, "ca") == 10
assert count_prefix_trie(trie, "ca") == 10
```

**Why:** The set approach scans all 100 words for every query. At 1 million words and a 2-character prefix, that's 1 million string comparisons per query. The trie jumps directly to the "ca" node in 2 steps, then counts only the matching 10 — it never looks at the 90 non-matching words. The trie wins whenever: (a) prefix is short, (b) the word count is large, (c) prefix queries are frequent. The hashmap's O(1) exact-lookup advantage becomes irrelevant when the operation is prefix-based, not exact-lookup.

**Time:** Set O(N × P), Trie O(P + K) where K = matching words. **Space:** Both O(N × L) to store words.
</details>

---

<a id="q9"></a>
### Q9 🟡 · Count words with a given prefix

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

**Problem:** Implement `count_words_with_prefix(prefix: str) -> int` on a Trie. After inserting `["apple", "app", "apt", "banana", "band"]`, verify that `count("app") == 2` (matches "app" and "apple"), `count("ban") == 2` (matches "banana" and "band"), and `count("xyz") == 0`.

<details>
<summary>💡 Hint</summary>

Navigate to the node at the end of the prefix first. If that node doesn't exist, return 0. From the prefix node, do a DFS (or BFS) counting every node where `is_end is True`. The key: the DFS must check `is_end` at the prefix node itself — the prefix might also be a word.
</details>

<details>
<summary>✅ Answer</summary>

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

trie = Trie()
for w in ["apple", "app", "apt", "banana", "band"]:
    trie.insert(w)

assert trie.count_words_with_prefix("app") == 2   # "app", "apple"
assert trie.count_words_with_prefix("apt") == 1   # "apt" only
assert trie.count_words_with_prefix("ban") == 2   # "banana", "band"
assert trie.count_words_with_prefix("xyz") == 0
assert trie.count_words_with_prefix("") == 5      # all words
```

**Why:** The `_count_all` DFS traverses the entire subtree rooted at the prefix node. It checks `is_end` at every node including the starting node — this handles the case where the prefix itself is also an inserted word (e.g., "app" when counting words with prefix "app"). The empty-prefix case returns a count of all inserted words.

**Time:** O(P + K) where P = prefix length, K = nodes in the subtree. **Space:** O(depth) for DFS recursion stack.
</details>

---

<a id="q10"></a>
### Q10 🟡 · Delete a word with branch pruning

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

**Problem:** Implement `delete(word: str)` with proper branch pruning. After inserting `["cat", "car", "ca"]`, deleting "cat" should not affect "car" or "ca". After deleting all three, only the root node should remain. Explain why simply clearing `is_end` is not enough.

<details>
<summary>💡 Hint</summary>

Use a recursive helper `_delete(node, word, depth) -> bool` that returns `True` if the current node should be removed by its parent. At the base case (depth == len(word)), clear `is_end` and return `True` only if the node has no children. Going back up, delete the child if it returned `True`, then return `True` yourself only if you now have no children and are not a word-end.
</details>

<details>
<summary>✅ Answer</summary>

```python
def delete(self, word: str) -> None:
    self._delete(self.root, word, 0)

def _delete(self, node, word: str, depth: int) -> bool:
    if depth == len(word):
        if not node.is_end:
            return False          # word not in trie
        node.is_end = False
        return len(node.children) == 0   # prune if leaf

    ch = word[depth]
    if ch not in node.children:
        return False              # word not in trie

    should_delete = self._delete(node.children[ch], word, depth + 1)
    if should_delete:
        del node.children[ch]
        return not node.is_end and len(node.children) == 0
    return False

trie = Trie()
for w in ["cat", "car", "ca"]:
    trie.insert(w)

trie.delete("cat")
assert trie.search("cat") is False
assert trie.search("car") is True    # shared prefix preserved
assert trie.search("ca") is True

trie.delete("car")
trie.delete("ca")
assert len(trie.root.children) == 0  # trie is empty
```

**Why:** Simply clearing `is_end` marks the word as gone logically but leaves the nodes in memory — a memory leak. At scale (millions of inserts and deletes), this can exhaust memory. The recursive approach propagates a "should I be deleted?" signal upward: a node is safe to remove only when it has no children and is not itself a word-end. This avoids pruning shared prefixes.

**Time:** O(L). **Space:** O(L) recursion stack.
</details>

---

<a id="q11"></a>
### Q11 🟡 · Autocomplete system

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

**Problem:** Implement an `AutocompleteTrie` with `insert(word)` and `autocomplete(prefix) -> list[str]`. After inserting `["cat", "car", "card", "care", "dog"]`, `autocomplete("ca")` should return all four "ca" words. Verify that `autocomplete("do")` returns `["dog"]` and `autocomplete("xyz")` returns `[]`.

<details>
<summary>💡 Hint</summary>

Two phases: (1) navigate to the prefix node — if it doesn't exist return `[]`; (2) DFS from that node and collect every word (every `is_end = True` node). Store the full word at each terminal node (`node.word = word` during insert) to avoid reconstructing strings from the path.
</details>

<details>
<summary>✅ Answer</summary>

```python
class AutocompleteTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True
        node.word = word   # store full word to avoid reconstruction

    def autocomplete(self, prefix: str) -> list[str]:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        results = []
        self._dfs(node, results)
        return sorted(results)

    def _dfs(self, node, results: list) -> None:
        if node.is_end:
            results.append(node.word)     # check is_end at EVERY node including start
        for child in node.children.values():
            self._dfs(child, results)

ac = AutocompleteTrie()
for w in ["cat", "car", "card", "care", "dog"]:
    ac.insert(w)

assert sorted(ac.autocomplete("ca")) == ["car", "card", "care", "cat"]
assert ac.autocomplete("do") == ["dog"]
assert ac.autocomplete("xyz") == []
assert ac.autocomplete("car") == ["car", "card", "care"]   # "car" itself included
```

**Why:** Checking `is_end` at the DFS starting node is critical — if "car" is inserted and you autocomplete "car", the starting node itself must be included. Storing the word at `node.word` avoids the overhead of reconstructing strings by concatenating characters as you go deeper.

**Time:** O(P + W) where P = prefix length, W = total characters in all matching words. **Space:** O(W) for results.
</details>

---

<a id="q12"></a>
### Q12 🟡 · Longest common prefix

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

**Problem:** Given a list of words, find their longest common prefix using a trie. For `["flower", "flow", "flight"]` the answer is `"fl"`. For `["dog", "racecar", "car"]` the answer is `""`. Implement `longest_common_prefix(words: list[str]) -> str`.

<details>
<summary>💡 Hint</summary>

Build a trie from all words. Then walk from the root, following the path as long as: (1) the current node has exactly one child, and (2) `is_end` is `False` at the current node (a word ending here means a shorter word exists, so we can't go further). Accumulate the characters as you walk.
</details>

<details>
<summary>✅ Answer</summary>

```python
def longest_common_prefix(words: list[str]) -> str:
    if not words:
        return ""

    root = TrieNode()
    for word in words:
        node = root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    # Walk from root as long as single child and not a word-end
    prefix = []
    node = root
    while len(node.children) == 1 and not node.is_end:
        ch = next(iter(node.children))
        prefix.append(ch)
        node = node.children[ch]

    return "".join(prefix)

assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"
assert longest_common_prefix(["dog", "racecar", "car"]) == ""
assert longest_common_prefix(["interview", "interact", "inter"]) == "inter"
assert longest_common_prefix(["a"]) == "a"
```

**Why:** The common prefix is the unbroken single-child chain at the top of the trie. As soon as a node has two children (words diverge) or `is_end = True` (a word ends here — it's shorter than the others), the common prefix is over. The condition `len(node.children) == 1 and not node.is_end` elegantly captures both stopping conditions.

**Time:** O(N × L) to build + O(LCP length) to traverse. **Space:** O(N × L) for the trie.
</details>

---

<a id="q13"></a>
### Q13 🟡 · Replace words with root

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

**Problem:** Given a dictionary of root words and a sentence, replace each word in the sentence with its shortest matching root from the dictionary. If no root matches, keep the original word. `replaceWords(["cat", "bat", "rat"], "the cattle was rattled by the battery")` should return `"the cat was rat by the bat"`.

<details>
<summary>💡 Hint</summary>

Build a trie from the dictionary roots. For each word in the sentence, walk the trie and stop the moment you hit `is_end = True` — that's the shortest root. If you exhaust the word without hitting a root-end, keep the original. This is O(L) per word vs O(L²) with a set.
</details>

<details>
<summary>✅ Answer</summary>

```python
def replace_words(dictionary: list[str], sentence: str) -> str:
    root = TrieNode()
    for word in dictionary:
        node = root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True
        node.word = word

    def find_root(word: str) -> str:
        node = root
        for ch in word:
            if ch not in node.children:
                break
            node = node.children[ch]
            if node.is_end:
                return node.word   # shortest root found — stop immediately
        return word               # no root matched

    return " ".join(find_root(w) for w in sentence.split())

assert replace_words(
    ["cat", "bat", "rat"],
    "the cattle was rattled by the battery"
) == "the cat was rat by the bat"

# When a root is a prefix of another root, shortest wins:
assert replace_words(["ca", "cat"], "cattle") == "ca"
```

**Why:** Walking the trie and stopping at the first `is_end = True` naturally finds the shortest root — shorter roots appear at shallower nodes. With a hash set, you'd need to check all prefixes of each word (O(L²)). The trie checks them in one O(L) pass by walking character by character and stopping early.

**Time:** O(D × L) to build + O(S × L) to process sentence where D = dict size, S = sentence word count. **Space:** O(D × L).
</details>

---

<a id="q14"></a>
### Q14 🟡 · Memory usage — dict vs array node

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

**Problem:** Build the same trie for 5 words using (a) dict-based nodes and (b) array-based nodes. Count the number of node slots used by each. Explain the memory tradeoff and state when each approach is preferred.

<details>
<summary>💡 Hint</summary>

For the dict approach, count how many child entries exist across all nodes — only actual children use memory. For the array approach, every node has exactly 26 slots regardless of how many children it has. A node with 2 children uses 2 slots with dict vs 26 slots with array.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Dict-based node: only stores actual children
class DictNode:
    def __init__(self):
        self.children = {}     # only actual children
        self.is_end = False

# Array-based node: always 26 slots
class ArrayNode:
    def __init__(self):
        self.children = [None] * 26  # 26 slots always
        self.is_end = False

def count_dict_slots(node) -> int:
    return len(node.children) + sum(count_dict_slots(c) for c in node.children.values())

def count_array_slots(node) -> int:
    return 26 + sum(count_array_slots(c) for c in node.children if c is not None)

# Words: ["cat", "car", "cab", "dog", "dot"]
# Unique nodes (excluding root): c-a-t, c-a-r, c-a-b, d-o-g, d-o-t
# Node 'a' has 3 children (t,r,b); node 'o' has 2 children (g,t)

# Dict: root(2) + c(1) + a(3) + t(0) + r(0) + b(0) + d(1) + o(2) + g(0) + t(0) = 9 slots
# Array: 10 nodes × 26 slots = 260 slots total

print("Dict approach: only stores actual edges → memory-efficient for sparse nodes")
print("Array approach: 26 slots per node → wastes space but gives O(1) guaranteed lookup")
# Breakeven: when avg children per node > ~13 (half of 26), array uses less overhead
```

**Why:** The dict approach uses memory proportional to the actual branching factor. For a typical English-word trie where most nodes have 1-3 children, dict nodes use dramatically less memory. The array approach pre-allocates 26 pointers per node, which wastes ~23 slots for a typical node with 3 children. However, array nodes are faster due to direct indexing and better cache locality. Rule of thumb: use array for LeetCode lowercase-only problems; use dict for production systems with large/variable alphabets.

**Time:** Dict O(1) average child lookup, Array O(1) guaranteed. **Space:** Dict O(actual edges), Array O(26 × nodes).
</details>

---

<a id="q15"></a>
### Q15 🟡 · Trie vs hashmap — prefix search benchmark

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

**Problem:** Build a trie and a set from the same 1000 words. For prefix `"pre"`, measure and compare how long each takes to find all matching words. Describe three scenarios where trie clearly wins over hashmap, and one scenario where hashmap is the better choice.

<details>
<summary>💡 Hint</summary>

Trie: navigate to prefix node (O(P)), then DFS to collect. Set: iterate all N words and check `w.startswith(prefix)` — O(N × P). The trie advantage grows as N increases and P decreases. For exact-match-only operations (no prefix needed), hashmap wins on simplicity and memory.
</details>

<details>
<summary>✅ Answer</summary>

```python
import time, random, string

def random_word(length=6):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

words = [random_word() for _ in range(1000)]
prefix = "pre"

# Hashmap approach
word_set = set(words)
t0 = time.perf_counter()
set_matches = [w for w in words if w.startswith(prefix)]
set_time = time.perf_counter() - t0

# Trie approach
trie = AutocompleteTrie()
for w in words:
    trie.insert(w)
t0 = time.perf_counter()
trie_matches = trie.autocomplete(prefix)
trie_time = time.perf_counter() - t0

print(f"Set:  {set_time*1e6:.1f}μs, {len(set_matches)} matches")
print(f"Trie: {trie_time*1e6:.1f}μs, {len(trie_matches)} matches")

# When trie wins:
# 1. Prefix queries on a large dictionary (millions of words)
# 2. Frequent autocomplete / search-suggestion queries
# 3. Multiple prefix queries — trie is built once, each query is fast

# When hashmap wins:
# 1. Exact-match only (no prefix queries needed) — O(1) vs O(L), simpler, less memory
```

**Why:** At 1000 words the difference is small. At 10 million words, the set iterates all 10M strings per query — even checking the first 3 characters of each. The trie hops to the "pre" node in 3 steps and only touches the matching subtree. The hashmap's O(1) exact-lookup advantage is irrelevant when the operation is fundamentally prefix-based.

**Time:** Set O(N × P) per query, Trie O(P + K) per query where K = matches. **Space:** Set O(N × L), Trie O(N × L) roughly equal.
</details>

---

<a id="q16"></a>
### Q16 🟡 · Implement full Trie class from scratch

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

**Problem:** From memory, implement a complete `Trie` class with `insert`, `search`, `starts_with`, `count_words_with_prefix`, and `autocomplete`. This is the LeetCode 208 "Implement Trie" problem extended. Test with `["apple", "app", "apt", "banana"]`.

<details>
<summary>💡 Hint</summary>

This is a synthesis question. Start with `TrieNode`, then `Trie.__init__`, then each method. The pattern for all traversal methods is identical: walk the trie following characters, handle the missing-character early return, then return the appropriate value based on what the operation needs at the end.
</details>

<details>
<summary>✅ Answer</summary>

```python
class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end: bool = False
        self.word: str | None = None

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node.children.setdefault(ch, TrieNode())
            node = node.children[ch]
        node.is_end = True
        node.word = word

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children: return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.children: return False
            node = node.children[ch]
        return True

    def count_words_with_prefix(self, prefix: str) -> int:
        node = self.root
        for ch in prefix:
            if ch not in node.children: return 0
            node = node.children[ch]
        def _count(n): return (1 if n.is_end else 0) + sum(_count(c) for c in n.children.values())
        return _count(node)

    def autocomplete(self, prefix: str) -> list[str]:
        node = self.root
        for ch in prefix:
            if ch not in node.children: return []
            node = node.children[ch]
        res = []
        def _dfs(n):
            if n.is_end: res.append(n.word)
            for c in n.children.values(): _dfs(c)
        _dfs(node)
        return sorted(res)

trie = Trie()
for w in ["apple", "app", "apt", "banana"]:
    trie.insert(w)
assert trie.search("app") is True
assert trie.search("ap") is False
assert trie.starts_with("ap") is True
assert trie.count_words_with_prefix("ap") == 3   # app, apple, apt
assert sorted(trie.autocomplete("ap")) == ["app", "apple", "apt"]
```

**Why:** `setdefault` is a Pythonic alternative to the `if ch not in / create` pattern — it creates the node only if missing, then returns the node for that key. All five methods share the same "walk then act" structure, which makes the implementation easy to remember under interview pressure.

**Time:** All operations O(L). **Space:** O(total characters) for the trie.
</details>

---

<a id="q17"></a>
### Q17 🟡 · Wildcard search with dot (.)

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

**Problem:** Implement `search_wildcard(pattern: str) -> bool` where `.` matches any single character. After inserting `["bad", "dad", "mad"]`, `search_wildcard(".ad")` should return `True`, `search_wildcard("b..")` should return `True`, and `search_wildcard("b.d")` should return `True`. This is LeetCode 211.

<details>
<summary>💡 Hint</summary>

Use a recursive DFS. When the character is `.`, try all children — recurse into every child node at the current depth. When the character is a regular letter, follow the specific child. Base case: when you've consumed all characters, check `node.is_end`.
</details>

<details>
<summary>✅ Answer</summary>

```python
def search_wildcard(self, word: str) -> bool:
    def dfs(node, i: int) -> bool:
        if i == len(word):
            return node.is_end
        ch = word[i]
        if ch == '.':
            return any(dfs(child, i + 1) for child in node.children.values())
        if ch not in node.children:
            return False
        return dfs(node.children[ch], i + 1)
    return dfs(self.root, 0)

trie = Trie()
for w in ["bad", "dad", "mad"]:
    trie.insert(w)

assert trie.search_wildcard(".ad") is True    # matches bad/dad/mad
assert trie.search_wildcard("b..") is True    # matches bad
assert trie.search_wildcard("b.d") is True    # matches bad
assert trie.search_wildcard("..x") is False   # nothing ends in x
assert trie.search_wildcard("...") is True    # matches all 3-letter words
```

**Why:** The `.` wildcard requires branching — you must try every possible character at that position. DFS handles this naturally: `any(dfs(child, i+1) for child in node.children.values())` tries all branches and short-circuits as soon as one returns `True`. This is why the problem requires a trie (or brute-force) rather than a hashmap — a hashmap can't do wildcard matching without scanning all keys.

**Time:** O(M × 26^k) where M = pattern length and k = number of dots (worst case). **Space:** O(M) recursion stack.
</details>

---

<a id="q18"></a>
### Q18 🟡 · Count distinct words in a trie

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

**Problem:** Implement `count_words(trie) -> int` that counts total distinct words in the trie. Inserting the same word twice should only count it once. Verify with `["apple", "app", "apple", "banana"]` — should return 3.

<details>
<summary>💡 Hint</summary>

DFS the entire trie and count every node where `is_end is True`. Since inserting the same word twice only re-marks `is_end = True` on the same node, duplicates are automatically handled.
</details>

<details>
<summary>✅ Answer</summary>

```python
def count_words(self) -> int:
    def _count(node) -> int:
        total = 1 if node.is_end else 0
        for child in node.children.values():
            total += _count(child)
        return total
    return _count(self.root)

trie = Trie()
for w in ["apple", "app", "apple", "banana"]:
    trie.insert(w)

assert trie.count_words() == 3   # apple, app, banana (apple inserted twice = 1)
```

**Why:** Inserting "apple" twice calls `node.is_end = True` twice on the same node — a no-op. The structure doesn't change. The DFS counts `is_end = True` nodes, which is exactly the number of distinct words. The root node is excluded from the count since no word ends at the root (unless `""` was inserted).

**Time:** O(N × L) to build, O(N × L) to count. **Space:** O(depth) for DFS stack.
</details>

---

<a id="q19"></a>
### Q19 🟡 · Lexicographic order — collect all words

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

**Problem:** Implement `all_words_sorted(trie) -> list[str]` that returns all words in lexicographic order without sorting the results. Explain why a trie DFS that iterates sorted children produces words in alphabetical order naturally.

<details>
<summary>💡 Hint</summary>

Sort the children keys at each node before iterating. Since a dict preserves insertion order in Python 3.7+, you can either insert in sorted order or sort during iteration. A DFS that visits children in alphabetical order naturally produces words in lexicographic order — no post-sort needed.
</details>

<details>
<summary>✅ Answer</summary>

```python
def all_words_sorted(self) -> list[str]:
    results = []
    def _dfs(node, path: list[str]) -> None:
        if node.is_end:
            results.append("".join(path))
        for ch in sorted(node.children.keys()):   # sorted children = lex order
            path.append(ch)
            _dfs(node.children[ch], path)
            path.pop()
    _dfs(self.root, [])
    return results

trie = Trie()
for w in ["banana", "apple", "apt", "app", "cat"]:
    trie.insert(w)

words = trie.all_words_sorted()
assert words == sorted(words)                # must be in sorted order
assert words == ["app", "apple", "apt", "banana", "cat"]
```

**Why:** A trie's structure mirrors lexicographic ordering — nodes at the same depth represent the same character position, and sibling nodes differ only in their character. Visiting siblings in alphabetical order during DFS produces a depth-first traversal that matches the dictionary order. This is more efficient than collecting all words and sorting (O(N log N)) — the trie DFS is O(N × L) with no sort step.

**Time:** O(N × L) for DFS. **Space:** O(depth) stack + O(N × L) for results.
</details>

---

<a id="q20"></a>
### Q20 🟡 · Trie from a stream of strings

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

**Problem:** You receive words one at a time (a stream). After each insertion, answer "how many words currently have the prefix 'py'?". Simulate with the stream `["python", "pytorch", "pypi", "java", "javascript", "pylint"]` and print the prefix count after each insertion.

<details>
<summary>💡 Hint</summary>

A trie handles online (streaming) insertions naturally — each `insert` call is O(L) and immediately makes the word queryable. After each insert, call `count_words_with_prefix("py")`. No rebuild needed.
</details>

<details>
<summary>✅ Answer</summary>

```python
trie = Trie()
stream = ["python", "pytorch", "pypi", "java", "javascript", "pylint"]

for word in stream:
    trie.insert(word)
    count = trie.count_words_with_prefix("py")
    print(f"After inserting '{word}': {count} words with prefix 'py'")

# After inserting 'python':     1
# After inserting 'pytorch':    2
# After inserting 'pypi':       3
# After inserting 'java':       3
# After inserting 'javascript': 3
# After inserting 'pylint':     4
```

**Why:** This is the key advantage of tries over sorted arrays for dynamic datasets. A sorted array requires O(log N + K) binary search after O(N) re-sorting on each insert. A trie inserts in O(L) and queries in O(P + K) — both independent of N. For a live search-suggestion system receiving thousands of new queries per second, the trie's O(L) per insert makes it practical; re-sorting is not.

**Time:** O(L) per insert, O(P + K) per prefix query. **Space:** O(total characters inserted so far).
</details>

---

<a id="q21"></a>
### Q21 🔴 · Word search in grid — trie + DFS

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

**Problem:** Given an m×n grid and a list of words, find all words that can be formed by visiting adjacent (4-directional) cells without reusing cells. This is LeetCode 212 "Word Search II". Implement the solution using a trie to prune the DFS. Test with the classic 4×4 grid example.

<details>
<summary>💡 Hint</summary>

Build a trie from all words first. Then DFS from every cell. At each step, check if the current cell's character exists in the current trie node's children. If not, prune immediately — no word in the dictionary can start with the current path. When a word-end node is reached, add the word to results. Mark cells as visited with `'#'` and restore them after recursion.
</details>

<details>
<summary>✅ Answer</summary>

```python
from typing import List

def find_words(board: List[List[str]], words: List[str]) -> List[str]:
    root = TrieNode()
    for word in words:
        node = root
        for ch in word:
            node.children.setdefault(ch, TrieNode())
            node = node.children[ch]
        node.is_end = True
        node.word = word

    ROWS, COLS = len(board), len(board[0])
    found = set()

    def dfs(r: int, c: int, node: TrieNode) -> None:
        ch = board[r][c]
        if ch not in node.children:
            return                          # prune: no word continues from here
        next_node = node.children[ch]
        if next_node.is_end:
            found.add(next_node.word)
            next_node.is_end = False        # avoid re-adding the same word

        board[r][c] = '#'                   # mark visited
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] != '#':
                dfs(nr, nc, next_node)
        board[r][c] = ch                    # restore

        # Prune exhausted branches
        if not next_node.children:
            del node.children[ch]

    for r in range(ROWS):
        for c in range(COLS):
            dfs(r, c, root)

    return list(found)

board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]]
words = ["oath","pea","eat","rain"]
result = find_words(board, words)
assert set(result) == {"eat", "oath"}
```

**Why:** Without a trie, you'd run a separate DFS for each word — O(W × R × C × 4^L). With the trie, one DFS over the grid checks all words simultaneously — O(R × C × 4^L) regardless of W. The pruning (`if ch not in node.children: return`) cuts off entire subtrees of the grid as soon as no dictionary word can continue through the current path. The branch-pruning optimization (`del node.children[ch]`) additionally removes trie branches that have been fully found, speeding up subsequent DFS calls.

**Time:** O(W × L) to build trie + O(R × C × 4^L) for grid DFS. **Space:** O(W × L) for trie + O(L) recursion stack.
</details>

---

<a id="q22"></a>
### Q22 🔴 · Top-K autocomplete with frequency ranking

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

**Problem:** Design a `RankedAutocompleteTrie` where each word is inserted with a frequency score. `get_top_k(prefix, k)` returns the k most frequent words matching the prefix. Test with search query data: insert `[("python", 95000), ("pytorch", 88000), ("pypi", 22000), ("pylint", 15000)]` and verify `get_top_k("py", 2)` returns `["python", "pytorch"]`.

<details>
<summary>💡 Hint</summary>

Store `(frequency, word)` tuples in a list at each terminal node. Collect all matching words with their frequencies via DFS, then use `heapq.nlargest(k, ...)` or sort descending. For production systems, you'd store a sorted top-K list at each node — but for an interview, DFS + sort is clean and correct.
</details>

<details>
<summary>✅ Answer</summary>

```python
import heapq

class RankedTrieNode:
    def __init__(self):
        self.children: dict[str, "RankedTrieNode"] = {}
        self.is_end: bool = False
        self.frequency: int = 0
        self.word: str = ""

class RankedAutocompleteTrie:
    def __init__(self):
        self.root = RankedTrieNode()

    def insert(self, word: str, frequency: int) -> None:
        node = self.root
        for ch in word:
            node.children.setdefault(ch, RankedTrieNode())
            node = node.children[ch]
        node.is_end = True
        node.frequency = frequency
        node.word = word

    def get_top_k(self, prefix: str, k: int) -> list[str]:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]

        # Collect all (frequency, word) pairs in subtree
        candidates = []
        def dfs(n: RankedTrieNode) -> None:
            if n.is_end:
                candidates.append((-n.frequency, n.word))  # negative for min-heap behavior
            for child in n.children.values():
                dfs(child)
        dfs(node)

        candidates.sort()   # sort by -frequency ascending = by frequency descending
        return [word for _, word in candidates[:k]]

trie = RankedAutocompleteTrie()
for word, freq in [("python", 95000), ("pytorch", 88000), ("pypi", 22000), ("pylint", 15000)]:
    trie.insert(word, freq)

assert trie.get_top_k("py", 2) == ["python", "pytorch"]
assert trie.get_top_k("py", 4) == ["python", "pytorch", "pypi", "pylint"]
assert trie.get_top_k("pyt", 2) == ["python", "pytorch"]
```

**Why:** Storing frequency at the terminal node and sorting candidates after DFS collection is the clean interview solution. Production systems optimize this by maintaining a top-K sorted list at every prefix node (updated on insert), so `get_top_k` returns in O(P + K) without any DFS. The tradeoff: O(K) extra space per node vs O(P + K × L) DFS per query.

**Time:** O(P + W) per query where W = words in subtree. **Space:** O(W × L) for trie.
</details>

---

<a id="q23"></a>
### Q23 🔴 · Trie memory analysis — when trie uses more than hashmap

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

**Problem:** Analyze when a trie uses MORE memory than a hashmap, not less. Given a list of 5 words with NO common prefixes (e.g., `["abc", "def", "ghi", "jkl", "mno"]`), count: (a) total characters in all words, (b) total trie nodes created (excluding root). Compare to a hashmap storing the same words. When does trie waste memory?

<details>
<summary>💡 Hint</summary>

When words share no prefixes, every character needs its own node — no sharing occurs. Total nodes = total characters across all words. A hashmap stores each word as a string (one allocation per word). A trie node typically costs more memory than a single character due to the children dict overhead. The trie only "wins" on memory when prefix sharing is high enough to compensate for the per-node overhead.
</details>

<details>
<summary>✅ Answer</summary>

```python
import sys

words_no_prefix = ["abc", "def", "ghi", "jkl", "mno"]
words_shared    = ["app", "apple", "application", "apply", "apt"]

def count_trie_nodes(trie_root) -> int:
    def _count(node):
        return 1 + sum(_count(c) for c in node.children.values())
    return _count(trie_root)

# No shared prefixes: every char is a unique node
trie1 = Trie()
for w in words_no_prefix:
    trie1.insert(w)

total_chars_no_prefix = sum(len(w) for w in words_no_prefix)
nodes_no_prefix = count_trie_nodes(trie1.root) - 1  # exclude root
print(f"No prefix sharing: {total_chars_no_prefix} chars, {nodes_no_prefix} nodes (same)")

# Shared prefixes: nodes < total chars
trie2 = Trie()
for w in words_shared:
    trie2.insert(w)

total_chars_shared = sum(len(w) for w in words_shared)
nodes_shared = count_trie_nodes(trie2.root) - 1
print(f"Shared prefixes: {total_chars_shared} chars, {nodes_shared} nodes (fewer)")

# Memory analysis
node_overhead = sys.getsizeof({}) + sys.getsizeof(False)  # dict + bool
str_overhead = sys.getsizeof("")
print(f"Trie node overhead: ~{node_overhead} bytes. Python str overhead: ~{str_overhead} bytes.")
print("Conclusion: trie wins on memory ONLY when prefix sharing reduces nodes enough to")
print("overcome the per-node dict overhead (~200+ bytes) vs per-character cost.")
```

**Why:** A Python dict has significant overhead (~200-300 bytes). Each trie node wraps a dict, so in the worst case (no shared prefixes), a trie uses ~200× more memory than storing the words as strings. The trie trades memory for fast prefix operations. It wins on memory only when words share long common prefixes (e.g., a dictionary of English words starting with "re-", "un-", "pre-"). For short words with diverse first characters, the hashmap wins on memory.

**Time:** O(N × L) analysis. **Space:** trie O(unique_chars × node_overhead), hashmap O(N × L × str_overhead).
</details>

---

<a id="q24"></a>
### Q24 🔴 · Design a search suggestion system

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

**Problem:** LeetCode 1268. Given a list of products and a search word, for each prefix of the search word (after each character is typed), return the 3 lexicographically smallest products that start with that prefix. `products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"]`, `searchWord = "mouse"` should produce suggestions after each character is typed.

<details>
<summary>💡 Hint</summary>

Build a trie from the products. For each prefix (length 1, 2, 3, ... up to len(searchWord)), call `autocomplete(prefix)` and return the first 3 results. Since you want lexicographic order, use the sorted-children DFS from Q19 and stop after collecting 3 results.
</details>

<details>
<summary>✅ Answer</summary>

```python
def suggested_products(products: list[str], search_word: str) -> list[list[str]]:
    # Build trie
    root = TrieNode()
    for product in sorted(products):  # pre-sort so DFS returns lex order
        node = root
        for ch in product:
            node.children.setdefault(ch, TrieNode())
            node = node.children[ch]
        node.is_end = True
        node.word = product

    def get_top3(node) -> list[str]:
        results = []
        def dfs(n):
            if len(results) == 3: return
            if n.is_end: results.append(n.word)
            for ch in sorted(n.children.keys()):
                if len(results) == 3: return
                dfs(n.children[ch])
        dfs(node)
        return results

    result = []
    node = root
    for ch in search_word:
        if node and ch in node.children:
            node = node.children[ch]
            result.append(get_top3(node))
        else:
            node = None          # no more matches possible
            result.append([])
    return result

products = ["mobile", "mouse", "moneypot", "monitor", "mousepad"]
output = suggested_products(products, "mouse")
# m     -> ["mobile", "moneypot", "monitor"]
# mo    -> ["mobile", "moneypot", "monitor"]
# mou   -> ["mouse", "mousepad"]
# mous  -> ["mouse", "mousepad"]
# mouse -> ["mouse", "mousepad"]
assert output[0] == ["mobile", "moneypot", "monitor"]
assert output[2] == ["mouse", "mousepad"]
```

**Why:** Pre-sorting the products before inserting ensures the trie's children are in lexicographic order at each node (Python dicts are insertion-ordered since 3.7). The early-exit DFS (`if len(results) == 3: return`) avoids traversing the entire subtree when only 3 results are needed. Setting `node = None` after a character is not found short-circuits all subsequent prefixes — once a prefix fails, all longer prefixes also fail.

**Time:** O(N × L log N) to build + O(P + 3L) per prefix query. **Space:** O(N × L).
</details>

---

<a id="q25"></a>
### Q25 🔴 · Common mistake gauntlet

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

**Problem:** Each snippet below contains a trie bug. For each one, identify the bug, explain what goes wrong, and write the fix. There are 5 bugs covering the most common trie mistakes.

<details>
<summary>💡 Hint</summary>

The five classic trie mistakes: (1) forgetting `is_end` flag — search returns True for any prefix; (2) using `ord(ch)` instead of `ord(ch) - ord('a')` in array trie; (3) delete only clears `is_end` without pruning dead branches; (4) autocomplete DFS misses `is_end` check at the starting node; (5) confusing search and startsWith return conditions.
</details>

<details>
<summary>✅ Answer</summary>

```python
# BUG 1: Missing is_end check in search
# Wrong: return True    (same as starts_with)
# Fix:   return node.is_end
def search_wrong(self, word):
    node = self.root
    for ch in word:
        if ch not in node.children: return False
        node = node.children[ch]
    return True           # BUG: returns True for prefixes too

def search_correct(self, word):
    node = self.root
    for ch in word:
        if ch not in node.children: return False
        node = node.children[ch]
    return node.is_end    # FIX: only True if word was inserted

# BUG 2: Array index off by base in array trie
# Wrong: idx = ord(ch)              -> 'a' gives 97, IndexError
# Fix:   idx = ord(ch) - ord('a')   -> 'a' gives 0, 'z' gives 25
idx_wrong = lambda ch: ord(ch)              # 'a' -> 97 -> IndexError
idx_correct = lambda ch: ord(ch) - ord('a')  # 'a' -> 0  -> correct

# BUG 3: Delete doesn't prune empty branches (memory leak)
# Wrong: only sets node.is_end = False, leaves dead nodes
# Fix: recursive delete that removes nodes with no children and no is_end
# (See Q10 for full correct implementation)

# BUG 4: Autocomplete DFS doesn't check is_end at starting node
# Wrong version — never appends the prefix itself if it's a word:
def autocomplete_wrong(node, prefix, results):
    for ch, child in node.children.items():  # BUG: skips node.is_end check at start
        if child.is_end: results.append(prefix + ch)
        autocomplete_wrong(child, prefix + ch, results)

# Correct version — checks is_end at every node including start:
def autocomplete_correct(node, prefix, results):
    if node.is_end: results.append(prefix)   # FIX: check at this node first
    for ch, child in node.children.items():
        autocomplete_correct(child, prefix + ch, results)

# BUG 5: starts_with accidentally implemented as search (checks is_end)
# Wrong: return node.is_end   (would return False for valid prefix "ca" when "cat" inserted)
# Fix:   return True
def starts_with_wrong(self, prefix):
    node = self.root
    for ch in prefix:
        if ch not in node.children: return False
        node = node.children[ch]
    return node.is_end   # BUG: "ca" after inserting "cat" returns False

def starts_with_correct(self, prefix):
    node = self.root
    for ch in prefix:
        if ch not in node.children: return False
        node = node.children[ch]
    return True           # FIX: path exists = prefix exists

print("All 5 bugs identified and fixed")
```

**Why:** These 5 bugs share a common theme: confusing "node exists" with "word ends here". Bug 1 and 5 are mirror images — Bug 1 makes `search` behave like `starts_with` (too permissive); Bug 5 makes `starts_with` behave like `search` (too strict). Bug 4 is the autocomplete variant of Bug 1. Bugs 2 and 3 are implementation bugs (index offset, memory management) rather than conceptual bugs.

**Time:** All checks O(L). **Space:** O(1) per check.
</details>

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Graphs — Theory →](../18_graphs/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
