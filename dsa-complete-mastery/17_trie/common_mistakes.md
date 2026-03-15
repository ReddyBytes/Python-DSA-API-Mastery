# Trie — Common Mistakes & Error Prevention

---

## Mistake 1: Confusing Node Existence with Word Existence

### The Bug

A trie stores words by sharing common prefixes. A node existing in the trie only means some word passes through that path — it does NOT mean a complete word ends there. For example, if "cat" is inserted, nodes for 'c', 'a', and 't' all exist. A search for "ca" should return False (it is only a prefix), but a naive implementation returns True because the node for 'a' exists.

### WRONG Code

```python
class TrieNodeWrong:
    def __init__(self):
        self.children = {}
        # No is_end flag!


class TrieWrong:
    def __init__(self):
        self.root = TrieNodeWrong()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNodeWrong()
            node = node.children[ch]
        # WRONG: no marker — we never record that a complete word ended here

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node is not None  # WRONG: this is True if the node exists at all
                                 # Conflates "prefix exists" with "word exists"

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for prefix_ch in prefix:
            if prefix_ch not in node.children:
                return False
            node = node.children[prefix_ch]
        return node is not None  # This is starts_with — CORRECT for prefix
                                 # But search() above is identical — both wrong for search
```

### CORRECT Code

```python
class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end: bool = False    # True only if a complete word ends at this node


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True           # CORRECT: mark the END of the word

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end           # CORRECT: node must exist AND be a word end

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True                  # node exists → prefix exists (regardless of is_end)
```

### Concrete Difference

```
Insert "cat"
Trie path: root → 'c' → 'a' → 't'   (is_end = True on 't' node)

search("ca"):
  WRONG: traverses to 'a' node, returns True  (node is not None)
  CORRECT: traverses to 'a' node, returns False (is_end is False)

starts_with("ca"):
  CORRECT: returns True  (path exists)

search("cat"):
  WRONG: True  (accidentally correct for this case)
  CORRECT: True  (is_end is True on 't' node)

search("cats"):
  WRONG: False  (no node for 's' — accidentally correct)
  CORRECT: False  (no node for 's')
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_search_returns_true_for_prefix():
    """After inserting 'cat', search('ca') should be False — wrong version returns True."""
    trie = TrieWrong()
    trie.insert("cat")
    # wrong: ca node exists, returns True
    assert trie.search("ca") == True, "WRONG version exposes the bug"


def test_correct_search_distinguishes_prefix_from_word():
    trie = Trie()
    trie.insert("cat")
    assert trie.search("ca") is False       # prefix only — not a word
    assert trie.search("cat") is True       # complete word
    assert trie.search("cats") is False     # not inserted
    assert trie.starts_with("ca") is True   # valid prefix
    assert trie.starts_with("dog") is False


def test_prefix_is_also_a_word():
    """Insert both 'ca' and 'cat'. Both should be found."""
    trie = Trie()
    trie.insert("ca")
    trie.insert("cat")
    assert trie.search("ca") is True
    assert trie.search("cat") is True
    assert trie.search("c") is False
    assert trie.starts_with("c") is True


def test_insert_same_word_twice():
    trie = Trie()
    trie.insert("hello")
    trie.insert("hello")
    assert trie.search("hello") is True
    assert trie.search("hell") is False


def test_empty_string():
    trie = Trie()
    trie.insert("")
    assert trie.search("") is True      # empty string is a valid word if inserted
    assert trie.search("a") is False


def test_search_on_empty_trie():
    trie = Trie()
    assert trie.search("anything") is False
    assert trie.starts_with("any") is False


def test_multiple_words_sharing_prefix():
    trie = Trie()
    for word in ["apple", "app", "application", "apply"]:
        trie.insert(word)
    assert trie.search("app") is True
    assert trie.search("appl") is False
    assert trie.search("apple") is True
    assert trie.starts_with("appl") is True


if __name__ == "__main__":
    trie = Trie()
    trie.insert("cat")
    print(f"search('cat')  = {trie.search('cat')}")    # True
    print(f"search('ca')   = {trie.search('ca')}")     # False
    print(f"starts_with('ca') = {trie.starts_with('ca')}")  # True

    bad = TrieWrong()
    bad.insert("cat")
    print(f"\nWRONG search('ca') = {bad.search('ca')}")   # True — bug!
```

### Key Takeaway

- `node is not None` answers "does the path exist?" — this is `starts_with`.
- `node.is_end` answers "does a complete word end here?" — this is `search`.
- Every trie node needs an `is_end` (or `end_of_word`) boolean flag set to `True` only after the last character of an inserted word.

---

## Mistake 2: Array-Based Trie — Index Calculation Error

### The Bug

When using a fixed-size array (size 26 for lowercase letters) instead of a dict, the index for a character is `ord(char) - ord('a')`. Forgetting the `- ord('a')` offset and using `ord(char)` directly gives indices in the range 97–122, way beyond the array size of 26, causing `IndexError` or silent memory corruption in lower-level languages.

### WRONG Code

```python
class TrieNodeArray:
    def __init__(self):
        self.children = [None] * 26
        self.is_end = False


class TrieArrayWrong:
    def __init__(self):
        self.root = TrieNodeArray()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            idx = ord(ch)                # WRONG: 'a' gives 97, 'z' gives 122
            # self.children has 26 slots (indices 0..25)
            # idx=97 → IndexError in Python, silent out-of-bounds in C/Java
            if node.children[idx] is None:
                node.children[idx] = TrieNodeArray()
            node = node.children[idx]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            idx = ord(ch)                # WRONG: same offset error
            if node.children[idx] is None:
                return False
            node = node.children[idx]
        return node.is_end
```

### CORRECT Code

```python
class TrieNodeArrayCorrect:
    def __init__(self):
        self.children: list["TrieNodeArrayCorrect | None"] = [None] * 26
        self.is_end: bool = False


class TrieArrayCorrect:
    def __init__(self):
        self.root = TrieNodeArrayCorrect()

    def _char_index(self, ch: str) -> int:
        idx = ord(ch) - ord('a')        # CORRECT: 'a'→0, 'b'→1, ..., 'z'→25
        assert 0 <= idx <= 25, f"Character '{ch}' out of range for lowercase trie"
        return idx

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            idx = self._char_index(ch)
            if node.children[idx] is None:
                node.children[idx] = TrieNodeArrayCorrect()
            node = node.children[idx]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            idx = self._char_index(ch)
            if node.children[idx] is None:
                return False
            node = node.children[idx]
        return node.is_end

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            idx = self._char_index(ch)
            if node.children[idx] is None:
                return False
            node = node.children[idx]
        return True
```

### Character Index Reference

```
Character mapping for lowercase letters (array size = 26):
'a' → ord('a') - ord('a') = 97 - 97 = 0
'b' → ord('b') - ord('a') = 98 - 97 = 1
'm' → ord('m') - ord('a') = 109 - 97 = 12
'z' → ord('z') - ord('a') = 122 - 97 = 25

WRONG (no offset):
'a' → ord('a') = 97    ← IndexError: list index out of range (size=26)
'z' → ord('z') = 122   ← IndexError
```

### Variants for Different Alphabets

```python
# Uppercase A-Z
idx = ord(ch) - ord('A')   # 0..25

# Digits 0-9
idx = ord(ch) - ord('0')   # 0..9

# All ASCII printable (size=95)
idx = ord(ch) - ord(' ')   # space=0, '~'=94

# Mixed alphanumeric: use a dict instead of array
self.children = {}
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_array_index_raises():
    trie = TrieArrayWrong()
    with pytest.raises(IndexError):
        trie.insert("hello")   # 'h' → ord('h') = 104, out of bounds for size-26 array


def test_correct_insert_and_search():
    trie = TrieArrayCorrect()
    trie.insert("hello")
    assert trie.search("hello") is True
    assert trie.search("hell") is False
    assert trie.starts_with("hell") is True


def test_correct_all_lowercase():
    trie = TrieArrayCorrect()
    for word in ["apple", "app", "banana", "band", "bandana"]:
        trie.insert(word)
    assert trie.search("app") is True
    assert trie.search("banana") is True
    assert trie.search("band") is True
    assert trie.search("ban") is False
    assert trie.starts_with("ban") is True


def test_correct_char_index_boundary():
    """'a' maps to 0, 'z' maps to 25."""
    trie = TrieArrayCorrect()
    trie.insert("az")
    assert trie.search("az") is True
    assert trie._char_index('a') == 0
    assert trie._char_index('z') == 25


def test_correct_uppercase_raises_assertion():
    trie = TrieArrayCorrect()
    with pytest.raises(AssertionError):
        trie.insert("Hello")   # 'H' = ord 72, idx = 72-97 = -25, caught by assert


def test_correct_single_char():
    trie = TrieArrayCorrect()
    trie.insert("a")
    assert trie.search("a") is True
    assert trie.search("b") is False


if __name__ == "__main__":
    try:
        wrong = TrieArrayWrong()
        wrong.insert("hello")
    except IndexError as e:
        print(f"WRONG (expected IndexError): {e}")

    correct = TrieArrayCorrect()
    correct.insert("hello")
    print(f"CORRECT search('hello') = {correct.search('hello')}")   # True
    print(f"CORRECT search('hell')  = {correct.search('hell')}")    # False
```

### Key Takeaway

- Always subtract the base character: `idx = ord(ch) - ord('a')` for lowercase.
- Add an assertion `0 <= idx < ALPHABET_SIZE` during development to catch this early.
- When the alphabet is not a contiguous range (e.g., mixed case + digits + symbols), use a `dict` instead of an array to avoid complex offset arithmetic.

---

## Mistake 3: Delete Not Pruning Empty Branches — Memory Leak

### The Bug

A naive trie delete implementation just clears the `is_end` flag of the target word's last node. This is logically correct (the word is no longer searchable) but leaves dead nodes — nodes with no children and no words ending at them — permanently consuming memory. In a long-running system with many inserts and deletes, this becomes a memory leak.

### WRONG Code

```python
class TrieDeleteWrong(Trie):
    def delete(self, word: str) -> None:
        """Only clears is_end — leaves dead branches."""
        node = self.root
        for ch in word:
            if ch not in node.children:
                return   # word not in trie, nothing to do
            node = node.children[ch]
        node.is_end = False   # WRONG: node and all its parents may now be dead weight
```

**Memory impact demonstration:**
- Insert 1,000,000 words of average length 10 → ~10,000,000 nodes.
- Delete all words using the wrong version → 10,000,000 nodes remain allocated.
- A correct pruning delete → trie returns to near-empty state.

### CORRECT Code — Recursive Delete with Pruning

```python
class TrieDeleteCorrect(Trie):
    def delete(self, word: str) -> bool:
        """
        Recursively delete a word and prune now-empty branches.
        Returns True if the current node should be deleted by its parent.
        """
        return self._delete(self.root, word, 0)

    def _delete(self, node: TrieNode, word: str, depth: int) -> bool:
        if node is None:
            return False

        if depth == len(word):
            # At the end of the word
            if not node.is_end:
                return False   # word was never inserted
            node.is_end = False
            # This node can be deleted if it has no children
            return len(node.children) == 0

        ch = word[depth]
        if ch not in node.children:
            return False   # word not in trie

        should_delete_child = self._delete(node.children[ch], word, depth + 1)

        if should_delete_child:
            del node.children[ch]   # prune the now-empty child
            # This node can be deleted if it has no remaining children and is not a word end
            return len(node.children) == 0 and not node.is_end

        return False

    def count_nodes(self) -> int:
        """Count total nodes for memory analysis."""
        return self._count(self.root)

    def _count(self, node: TrieNode | None) -> int:
        if node is None:
            return 0
        count = 1
        for child in node.children.values():
            count += self._count(child)
        return count
```

### Tracing the Pruning

```
Insert "cat", "car", "ca", "cab"
Trie: root → 'c'(F) → 'a'(T) → 't'(T)
                               → 'r'(T)
                               → 'b'(T)
(T = is_end, F = not is_end)

Delete "cat":
- _delete(root, "cat", 0): recurse to 'c'
- _delete(c_node, "cat", 1): recurse to 'a'
- _delete(a_node, "cat", 2): recurse to 't'
- _delete(t_node, "cat", 3): depth==len, set is_end=False, children={} → return True
- Back at a_node: delete 't' from children. a_node.children={'r','b'}, not empty → return False
- Trie: root → 'c' → 'a'(T) → 'r'(T)
                             → 'b'(T)

Delete "ca":
- Eventually reaches a_node: set is_end=False, children={'r','b'} not empty → return False
- Trie: root → 'c' → 'a'(F) → 'r'(T)
                             → 'b'(T)

Delete "car":
- reaches r_node: is_end=False, children={} → return True
- a_node deletes 'r'. a_node.children={'b'}, not empty → return False

Delete "cab":
- reaches b_node: is_end=False, children={} → return True
- a_node deletes 'b'. a_node.children={}, not is_end → return True
- c_node deletes 'a'. c_node.children={}, not is_end → return True
- root deletes 'c'. Trie is now completely empty (just root node).
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_leaves_dead_nodes():
    root_trie = Trie()
    root_trie.insert("cat")

    wrong_trie = TrieDeleteWrong.__new__(TrieDeleteWrong)
    wrong_trie.root = root_trie.root

    wrong_trie.delete("cat")
    assert wrong_trie.search("cat") is False   # logically correct

    # BUT the node for 't' still exists in memory
    c_node = wrong_trie.root.children.get("c")
    a_node = c_node.children.get("a") if c_node else None
    t_node = a_node.children.get("t") if a_node else None
    assert t_node is not None, "WRONG: dead node still allocated in memory"


def test_correct_prunes_empty_branch():
    trie = TrieDeleteCorrect()
    trie.insert("cat")
    nodes_before = trie.count_nodes()

    trie.delete("cat")
    nodes_after = trie.count_nodes()

    assert trie.search("cat") is False
    assert nodes_after < nodes_before   # nodes were actually freed


def test_correct_does_not_prune_shared_prefix():
    trie = TrieDeleteCorrect()
    trie.insert("cat")
    trie.insert("car")
    trie.delete("cat")

    assert trie.search("cat") is False
    assert trie.search("car") is True   # 'car' still intact
    assert trie.starts_with("ca") is True   # shared prefix preserved


def test_correct_prunes_all_after_full_delete():
    trie = TrieDeleteCorrect()
    words = ["cat", "car", "ca", "cab"]
    for w in words:
        trie.insert(w)
    for w in words:
        trie.delete(w)
    assert trie.count_nodes() == 1   # only root remains


def test_correct_delete_nonexistent_word():
    trie = TrieDeleteCorrect()
    trie.insert("cat")
    result = trie.delete("dog")   # should not crash
    assert trie.search("cat") is True   # cat still there


def test_correct_delete_prefix_only():
    """Deleting 'ca' should not affect 'cat'."""
    trie = TrieDeleteCorrect()
    trie.insert("cat")
    trie.delete("ca")   # 'ca' was never inserted
    assert trie.search("cat") is True


def test_correct_delete_then_reinsert():
    trie = TrieDeleteCorrect()
    trie.insert("hello")
    trie.delete("hello")
    assert trie.search("hello") is False
    trie.insert("hello")
    assert trie.search("hello") is True


if __name__ == "__main__":
    trie = TrieDeleteCorrect()
    words = ["cat", "car", "ca", "cab"]
    for w in words:
        trie.insert(w)
    print(f"Nodes after inserting {words}: {trie.count_nodes()}")

    for w in words:
        trie.delete(w)
        print(f"After deleting '{w}': {trie.count_nodes()} nodes, search('{w}')={trie.search(w)}")
```

### Key Takeaway

- A simple `is_end = False` is correct for logical correctness but leaks memory.
- A proper recursive delete must propagate `should_delete` upward: a node is deletable when `not node.is_end and len(node.children) == 0`.
- Pruning is especially critical in production tries (e.g., autocomplete systems that rotate vocabulary).

---

## Mistake 4: Search Returning True for a Prefix

### The Bug

This is directly related to Mistake 1 but occurs as a standalone bug in implementations that are written without an `is_end` flag or where `search()` and `starts_with()` are accidentally implemented the same way. After inserting "cat", calling `search("ca")` returns True because the path "c→a" exists.

### WRONG Code

```python
class TrieSearchWrong:
    def __init__(self):
        self.root = {"children": {}, "end": False}

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node["children"]:
                node["children"][ch] = {"children": {}, "end": False}
            node = node["children"][ch]
        node["end"] = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node["children"]:
                return False
            node = node["children"][ch]
        return True   # WRONG: should be `return node["end"]`
                      # This is starts_with(), not search()
```

### CORRECT Code

```python
class TrieSearchCorrect:
    def __init__(self):
        self.root = {"children": {}, "end": False}

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node["children"]:
                node["children"][ch] = {"children": {}, "end": False}
            node = node["children"][ch]
        node["end"] = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node["children"]:
                return False
            node = node["children"][ch]
        return node["end"]   # CORRECT: must reach the node AND it must be a word end

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node["children"]:
                return False
            node = node["children"][ch]
        return True   # Any existing path is a valid prefix
```

### The Difference Explained

```
insert("cat")
Nodes: root → 'c'[end=F] → 'a'[end=F] → 't'[end=T]

search("cat"):
  Wrong:   reaches 't' node → return True  (correct by accident)
  Correct: reaches 't' node → return node["end"] = True

search("ca"):
  Wrong:   reaches 'a' node → return True  (BUG — "ca" was never inserted)
  Correct: reaches 'a' node → return node["end"] = False

starts_with("ca"):
  Correct: reaches 'a' node → return True  (path exists — this IS correct for prefix)
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_search_accepts_prefix():
    trie = TrieSearchWrong()
    trie.insert("apple")
    assert trie.search("app") is True   # BUG: "app" was never inserted


def test_wrong_search_identical_to_starts_with():
    trie = TrieSearchWrong()
    trie.insert("apple")
    # wrong search and starts_with behave identically — this is wrong for search
    assert trie.search("app") == True
    # This means wrong search is equivalent to starts_with — not search


def test_correct_search_rejects_prefix():
    trie = TrieSearchCorrect()
    trie.insert("apple")
    assert trie.search("app") is False    # prefix only — not a word
    assert trie.search("apple") is True   # complete word
    assert trie.starts_with("app") is True


def test_correct_prefix_inserted_explicitly():
    """When prefix IS inserted as a word, search must return True for it."""
    trie = TrieSearchCorrect()
    trie.insert("app")
    trie.insert("apple")
    assert trie.search("app") is True
    assert trie.search("apple") is True
    assert trie.search("ap") is False


def test_correct_search_empty_trie():
    trie = TrieSearchCorrect()
    assert trie.search("anything") is False


def test_correct_starts_with_vs_search():
    trie = TrieSearchCorrect()
    trie.insert("cat")
    words_to_check = ["c", "ca", "cat", "cats", "dog"]
    for word in words_to_check:
        sw = trie.starts_with(word)
        s = trie.search(word)
        print(f"  starts_with({word!r})={sw}, search({word!r})={s}")
    assert trie.starts_with("c") is True
    assert trie.search("c") is False


if __name__ == "__main__":
    bad = TrieSearchWrong()
    bad.insert("cat")
    print("=== WRONG ===")
    print(f"search('cat') = {bad.search('cat')}")   # True (accidentally right)
    print(f"search('ca')  = {bad.search('ca')}")    # True (BUG)
    print(f"search('c')   = {bad.search('c')}")     # True (BUG)

    good = TrieSearchCorrect()
    good.insert("cat")
    print("\n=== CORRECT ===")
    print(f"search('cat') = {good.search('cat')}")   # True
    print(f"search('ca')  = {good.search('ca')}")    # False
    print(f"search('c')   = {good.search('c')}")     # False
    print(f"starts_with('ca') = {good.starts_with('ca')}")  # True
```

### Key Takeaway

- `search(word)` must return `node.is_end` — not just `True` for reaching the node.
- `starts_with(prefix)` should return `True` for any existing path.
- The two methods have different return conditions: `search` is strict (end of word), `starts_with` is permissive (path exists).

---

## Mistake 5: Autocomplete — Forgetting to Check `is_end` at the Starting Node

### The Bug

When collecting all words with a given prefix, the DFS starts at the prefix's last node. If the prefix itself is a complete word (`node.is_end == True`), it must be included in the results. A common mistake is to only recurse into children and never check `is_end` at the starting node, causing the prefix word to be omitted from suggestions.

### WRONG Code

```python
def autocomplete_wrong(trie: Trie, prefix: str) -> list[str]:
    """Collect all words with the given prefix."""
    # Find the node at the end of the prefix
    node = trie.root
    for ch in prefix:
        if ch not in node.children:
            return []
        node = node.children[ch]

    results = []
    _dfs_wrong(node, prefix, results)
    return results


def _dfs_wrong(node: TrieNode, current: str, results: list[str]) -> None:
    # WRONG: never checks node.is_end at this node
    # Only recurses into children — misses the case where current is itself a complete word
    for ch, child in node.children.items():
        if child.is_end:
            results.append(current + ch)
        _dfs_wrong(child, current + ch, results)
```

**Why it fails:** If the prefix is "app" and "app" is an inserted word, the DFS starts at the "app" node. The wrong version immediately dives into children (`children['l']` for "apple") without first checking `node.is_end`. So "app" itself never appears in the output.

### CORRECT Code

```python
def autocomplete_correct(trie: Trie, prefix: str) -> list[str]:
    """Collect all words with the given prefix, including the prefix itself if it's a word."""
    node = trie.root
    for ch in prefix:
        if ch not in node.children:
            return []
        node = node.children[ch]

    results = []
    _dfs_correct(node, prefix, results)
    return sorted(results)   # sorted for deterministic output


def _dfs_correct(node: TrieNode, current: str, results: list[str]) -> None:
    if node.is_end:
        results.append(current)   # CORRECT: check is_end at every visited node,
                                  # including the starting node

    for ch, child in node.children.items():
        _dfs_correct(child, current + ch, results)


# Alternative: iterative BFS version
from collections import deque


def autocomplete_bfs(trie: Trie, prefix: str) -> list[str]:
    node = trie.root
    for ch in prefix:
        if ch not in node.children:
            return []
        node = node.children[ch]

    results = []
    queue = deque([(node, prefix)])

    while queue:
        curr_node, curr_word = queue.popleft()
        if curr_node.is_end:
            results.append(curr_word)
        for ch, child in curr_node.children.items():
            queue.append((child, curr_word + ch))

    return sorted(results)
```

### Tracing the Bug

```
Insert: "app", "apple", "application", "apply"
Trie:
root → 'a' → 'p' → 'p'[end=T] → 'l' → 'e'[end=T]
                                       → 'i' → 'c' → 'a' → 't' → 'i' → 'o' → 'n'[end=T]
                                       → 'y'[end=T]

autocomplete("app"):
Start at 'p'[end=T] (the second 'p' node)

WRONG _dfs_wrong(p_node, "app"):
  Never checks p_node.is_end!
  Recurses into 'l' child:
    Checks l.children: 'e'[end=T] → appends "apple"
    Recurses into 'e', 'i':
      appends "application", "apply"
  Result: ["apple", "application", "apply"]   ← "app" MISSING

CORRECT _dfs_correct(p_node, "app"):
  node.is_end == True → append "app"
  Recurses into children: appends "apple", "application", "apply"
  Result: ["app", "apple", "application", "apply"]   ← CORRECT
```

### Test Cases That Expose the Bug

```python
import pytest


def test_wrong_omits_prefix_word():
    trie = Trie()
    for word in ["app", "apple", "apply"]:
        trie.insert(word)
    result = autocomplete_wrong(trie, "app")
    assert "app" not in result, f"Expected 'app' to be missing in wrong version: {result}"


def test_correct_includes_prefix_word():
    trie = Trie()
    for word in ["app", "apple", "apply"]:
        trie.insert(word)
    result = autocomplete_correct(trie, "app")
    assert "app" in result
    assert "apple" in result
    assert "apply" in result
    assert len(result) == 3


def test_correct_prefix_not_a_word():
    """If prefix is not itself a word, it should not appear in results."""
    trie = Trie()
    for word in ["apple", "apply"]:
        trie.insert(word)
    result = autocomplete_correct(trie, "app")
    assert "app" not in result   # "app" was not inserted
    assert "apple" in result
    assert "apply" in result


def test_correct_exact_match_only():
    """Only one word in the trie, and prefix equals it."""
    trie = Trie()
    trie.insert("cat")
    result = autocomplete_correct(trie, "cat")
    assert result == ["cat"]


def test_correct_no_matches():
    trie = Trie()
    trie.insert("apple")
    assert autocomplete_correct(trie, "xyz") == []


def test_correct_empty_prefix():
    """Empty prefix should return all words in the trie."""
    trie = Trie()
    words = ["app", "apple", "bat", "ball"]
    for w in words:
        trie.insert(w)
    result = autocomplete_correct(trie, "")
    assert sorted(result) == sorted(words)


def test_bfs_matches_dfs():
    trie = Trie()
    for word in ["app", "apple", "application", "apply", "banana"]:
        trie.insert(word)
    dfs_result = autocomplete_correct(trie, "app")
    bfs_result = autocomplete_bfs(trie, "app")
    assert dfs_result == bfs_result


if __name__ == "__main__":
    trie = Trie()
    for word in ["app", "apple", "application", "apply"]:
        trie.insert(word)

    print("WRONG:", sorted(autocomplete_wrong(trie, "app")))    # missing "app"
    print("CORRECT:", autocomplete_correct(trie, "app"))         # includes "app"
    print("BFS:", autocomplete_bfs(trie, "app"))                 # includes "app"
```

### Key Takeaway

- In trie DFS/BFS traversal, always check `node.is_end` at every visited node — including the **starting node** of the traversal.
- A common pattern: check first, then recurse. Never skip the starting node's end check.
- This bug produces wrong but non-crashing output, making it particularly hard to spot without explicit test cases that include a word that equals a prefix of another word.

---

## Summary Table

| # | Mistake | Root Cause | Fix |
|---|---|---|---|
| 1 | `return node is not None` in search | Conflates path existence with word completion | `return node is not None and node.is_end` |
| 2 | `idx = ord(char)` in array trie | Missing base offset — indices way out of bounds | `idx = ord(char) - ord('a')` |
| 3 | Delete only clears `is_end` | Dead nodes never freed | Recursive delete that prunes empty branches |
| 4 | `return True` instead of `return node.is_end` | `search()` accidentally implements `starts_with()` | `return node.is_end` |
| 5 | DFS skips `is_end` at starting node | Prefix word omitted from autocomplete results | Check `is_end` at every visited node before recursing |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Real World Usage](./real_world_usage.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Patterns](./patterns.md) · [Real World Usage](./real_world_usage.md) · [Interview Q&A](./interview.md)
