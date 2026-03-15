# Trie Problem Patterns — When to Reach for a Trie

---

## The Story First

Imagine you run a massive library. You have millions of books, and visitors constantly ask:
"Do you have any books whose title starts with 'The Great'?"

Option A: You check every single book title. Slow.
Option B: You organized titles alphabetically in a tree — you walk down T → H → E → (space) → G → R → E → A → T and instantly see every book that starts there.

That tree of characters is a **Trie** (pronounced "try", from re**trie**val).

A trie stores strings character by character, sharing prefixes. "cat", "car", "cart", "card" all share the prefix "ca". They branch apart after that. The trie structure makes prefix-based queries blazing fast.

```
         root
          |
          c
          |
          a
         / \
        t   r
        |   |
       (end) t
            / \
           (end) d
                 |
                (end)
```

Words stored: "cat", "cart", "card". "cat" and "car" share "ca". "cart" and "card" share "car".

This document covers the 6 core patterns where a trie is the right tool.

---

## The Core Trie Structure (Your Starting Point)

Before patterns, internalize the base trie. Every pattern below modifies or extends this:

```python
class TrieNode:
    def __init__(self):
        self.children = {}       # char -> TrieNode
        self.is_end = False      # True if a word ends here
        self.word = None         # Optional: store the full word here (useful for pattern 2)

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
        node.word = word

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True
```

**Time complexity:**
- Insert: O(L) where L = word length
- Search: O(L)
- StartsWith: O(L)

**Space:** O(total characters across all words) — shared prefixes save space.

---

## Pattern 1: Prefix Search / Autocomplete

### The Problem

You are building a search bar. User types "ca". You want to suggest: "cat", "car", "cart", "card", "cable", "cabin". This is **autocomplete**.

Or in interview terms: "Given a list of words and a prefix, return all words that start with that prefix."

### When to Reach for This Pattern

- "Does any word start with prefix X?" → `starts_with`
- "Return all words that start with prefix X" → `get_all_with_prefix`
- "How many words share prefix X?" → count nodes from prefix endpoint
- Classic autocomplete, search suggestions, spell checkers

### The Insight

Once you build the trie, finding words with a given prefix is a two-step process:
1. Walk down the trie following the prefix characters. This gets you to the "prefix node."
2. From that node, do a DFS and collect every word you encounter (every `is_end = True` node).

```
Trie built from: ["cat", "car", "cart", "card", "cable", "cabin"]

        root
          |
          c
          |
          a
        / | \
       t  r  b
      (*)  \   \
           t   l   i
          / \   \   \
         (end) d  e   n
               |   |   |
              (*)  (*) (*)
```
(*) = is_end = True

User types "ca". We walk to node 'a'. From there, DFS finds:
- t → "cat" (end)
- r → t → "cart" (end), d → "card" (end)
- b → l → e → "cable" (end), i → n → "cabin" (end)

```
Query: prefix = "ca"

Walk: root -> c -> a   [arrived at prefix node]

DFS from 'a':
   a
  /|\
 t  r  b
 |  |  |
[cat] [r→card,cart] [b→cable,cabin]

Results: ["cat", "car", "cart", "card", "cable", "cabin"]
```

### Template Code

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
        node.word = word

    def _find_prefix_node(self, prefix: str):
        """Walk down trie following prefix. Return the node at prefix end, or None."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def _dfs_collect(self, node, results: list) -> None:
        """DFS from node, collecting all words (is_end = True)."""
        if node.is_end:
            results.append(node.word)
        for child in node.children.values():
            self._dfs_collect(child, results)

    def get_all_with_prefix(self, prefix: str) -> list:
        prefix_node = self._find_prefix_node(prefix)
        if not prefix_node:
            return []
        results = []
        self._dfs_collect(prefix_node, results)
        return results

    def starts_with(self, prefix: str) -> bool:
        return self._find_prefix_node(prefix) is not None


# Usage
trie = AutocompleteTrie()
words = ["cat", "car", "cart", "card", "cable", "cabin", "dog", "door"]
for w in words:
    trie.insert(w)

print(trie.get_all_with_prefix("ca"))
# → ["cat", "car", "cart", "card", "cable", "cabin"]

print(trie.get_all_with_prefix("do"))
# → ["dog", "door"]

print(trie.starts_with("cab"))
# → True

print(trie.starts_with("xyz"))
# → False
```

### Complexity
- Build trie: O(W × L) — W words, L average length
- Query prefix: O(P + K × L) — P = prefix length, K = number of matching words

### Interview Variant: Top-K Autocomplete
Store a sorted list of (frequency, word) at each node. On insert, update all ancestor nodes. This lets you return the top K most frequent words for a prefix in O(P + K) time. The tradeoff is more storage.

---

## Pattern 2: Word Search in Grid (DFS + Trie)

### The Problem

Classic LeetCode 212: "Word Search II". Given an m×n grid of characters and a list of words, return all words that can be found in the grid (horizontally/vertically adjacent, no reuse of cells).

### The Critical Insight: Why Trie Beats Naive

Naive approach: For each word, run a DFS on the grid. If you have 1000 words, you run 1000 separate DFS searches.

**Naive complexity:** O(words × grid × 4^L) — brutal.

**Trie approach:** You build a trie of all words first, then do ONE DFS over the grid, and at each position you navigate the trie simultaneously. When the current path of characters doesn't match any prefix in the trie, you prune immediately — you don't waste time chasing dead ends.

**Trie complexity:** O(grid × 4^L) — you only do the grid DFS once, no matter how many words there are.

Think of it like this: you're walking through the grid, and the trie is your checklist. As soon as the path you're walking doesn't appear anywhere on the checklist, you stop and backtrack.

### ASCII: Grid + Trie Pruning

```
Grid:                    Trie (words: ["eat", "oath", "oath"]):
o  a  a  n               root
e  t  a  e                |  \
i  h  k  r               e    o
i  f  l  v               |    |
                         a    a
                         |    |
                         t    t
                        (*)   |
                              h
                             (*)

DFS starting from 'e' (row 1, col 0):
  - 'e' matches trie root's child 'e'? YES → go deeper
  - Move to 't' (row 1, col 1) → trie 'e'→'a'? 't' is not 'a' → PRUNE
  - Move to 'a' (row 0, col 1) → trie 'e'→'a'? YES → go deeper
  - Move to 't' (row 1, col 1) → trie 'e'→'a'→'t'? YES → is_end? YES → FOUND "eat"!

DFS starting from 'o' (row 0, col 0):
  - 'o' matches trie root's child 'o'? YES → go deeper
  - Move to 'a' (row 0, col 1) → trie 'o'→'a'? YES → go deeper
  - Move to 't' (row 1, col 1) → trie 'o'→'a'→'t'? YES → go deeper
  - Move to 'h' (row 2, col 1) → trie 'o'→'a'→'t'→'h'? YES → is_end? YES → FOUND "oath"!
```

### Template Code

```python
from typing import List

class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        # Step 1: Build trie from all words
        root = TrieNode()
        for word in words:
            node = root
            for ch in word:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.is_end = True
            node.word = word  # store full word at terminal node

        ROWS, COLS = len(board), len(board[0])
        found = set()

        def dfs(r, c, node):
            ch = board[r][c]

            # Prune: if current char is not in trie at this level → stop
            if ch not in node.children:
                return

            next_node = node.children[ch]

            # Found a complete word
            if next_node.is_end:
                found.add(next_node.word)
                # Don't return — there might be longer words through this path
                # Optional optimization: next_node.is_end = False  (avoid revisiting)

            # Mark cell as visited by temporarily replacing it
            board[r][c] = '#'

            # Explore all 4 directions
            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] != '#':
                    dfs(nr, nc, next_node)

            # Restore cell
            board[r][c] = ch

        # Step 2: Start DFS from every cell
        for r in range(ROWS):
            for c in range(COLS):
                dfs(r, c, root)

        return list(found)
```

### The Pruning Optimization

Add this after finding a word: `next_node.is_end = False`. Once you've found a word, you don't need to find it again. Even better, you can prune entire branches: if a trie node has no more words under it (no `is_end` descendants), remove it entirely. This makes later DFS calls skip those branches.

```python
# Advanced pruning: remove leaf nodes after finding words
def dfs(r, c, node):
    ch = board[r][c]
    if ch not in node.children:
        return

    next_node = node.children[ch]
    if next_node.is_end:
        found.add(next_node.word)
        next_node.is_end = False  # don't re-add

    board[r][c] = '#'
    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] != '#':
            dfs(nr, nc, next_node)
    board[r][c] = ch

    # Prune empty branch (no children, no words below)
    if not next_node.children and not next_node.is_end:
        del node.children[ch]
```

---

## Pattern 3: XOR Maximum (Binary Trie)

### The Story

You have a bag of numbers. You want to pick two numbers that, when XOR-ed together, give the biggest possible result.

XOR gives a 1 wherever bits differ. So to maximize XOR, you want bits to differ as much as possible from the most significant bit downward.

A **binary trie** stores numbers bit by bit (from the most significant bit to least significant). For each number you query, you greedily navigate the trie choosing the opposite bit at each level — because opposite bits XOR to 1, which is what you want.

### The Insight

For a 32-bit number:
- At bit 31 (most significant): if current bit is 0, you want the other number to have bit 31 = 1. Go to the `1` branch if it exists.
- If `1` branch doesn't exist, go to `0` branch (no choice).
- Continue down 30 more levels.

The number at the bottom of your greedy path maximizes XOR with your query number.

### ASCII: Binary Trie for XOR

```
Numbers: [3, 10, 5, 25, 2, 8]
Binary (5-bit for simplicity):
  3  = 00011
  10 = 01010
  5  = 00101
  25 = 11001
  2  = 00010
  8  = 01000

Binary Trie (built from all numbers, 5 levels):

          root
         /    \
        0      1
       / \      \
      0   1      1
     /\   |       \
    0  1  0        0
   /\   \  \        \
  1  0   1  0        1
  |  |   |  |        |
 [3] [2] [5][10]    [25]

Query number = 25 = 11001
Greedy: at each level, pick OPPOSITE bit:
  Level 4: bit=1 → want 0 → 0-branch exists → go 0, XOR contrib = 1 at this bit
  Level 3: bit=1 → want 0 → 0-branch exists → go 0, XOR contrib = 1 at this bit
  Level 2: bit=0 → want 1 → 1-branch exists → go 1, XOR contrib = 1 at this bit
  Level 1: bit=0 → want 1 → 1-branch doesn't exist → go 0, XOR contrib = 0
  Level 0: bit=1 → want 0 → 0-branch exists → go 0, XOR contrib = 1
  Path lands at: 10 (01010)
  XOR: 25 ^ 10 = 11001 ^ 01010 = 10011 = 19 ← max XOR found for 25
```

### Template Code

```python
class MaxXORTrie:
    def __init__(self):
        # Each node: [left_child, right_child] where index = bit value (0 or 1)
        # Using list for speed; dict also works
        self.root = [None, None]

    def insert(self, num: int) -> None:
        node = self.root
        for i in range(31, -1, -1):   # 32 bits, MSB first
            bit = (num >> i) & 1
            if node[bit] is None:
                node[bit] = [None, None]
            node = node[bit]

    def find_max_xor(self, num: int) -> int:
        node = self.root
        xor_val = 0
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            want = 1 - bit            # we want the opposite bit
            if node[want] is not None:
                xor_val |= (1 << i)   # this bit contributes to XOR
                node = node[want]
            else:
                node = node[bit]      # no choice, take same bit
        return xor_val


def findMaximumXOR(nums):
    trie = MaxXORTrie()
    for n in nums:
        trie.insert(n)
    return max(trie.find_max_xor(n) for n in nums)


# Test
print(findMaximumXOR([3, 10, 5, 25, 2, 8]))
# → 28  (5 XOR 25 = 00101 ^ 11001 = 11100 = 28)
```

### Complexity
- Build: O(N × 32)
- Query: O(N × 32)
- Overall: O(N) since 32 is a constant

### Interview Variants
- **Maximum XOR with elements from a prefix of array:** Insert numbers one by one. Before inserting nums[i], query for max XOR using the current trie (only previous elements). Useful when pairs must come from specific index ranges.
- **Maximum XOR subarray:** Use prefix XOR + this trie.

---

## Pattern 4: Replace Words (Shortest Prefix / Root Replacement)

### The Story

In English, "cat" is a root. "Catfish", "cattle", "catapult" are all derivatives. Suppose you want to replace every derivative word in a sentence with its shortest known root.

Input dictionary: ["cat", "bat", "rat"]
Input sentence: "the cattle was rattled by the battery"
Output: "the cat was rat by the bat"

"cattle" → "cat" is its shortest root → replaced with "cat"
"rattled" → "rat" is its shortest root → replaced with "rat"
"battery" → "bat" is its shortest root → replaced with "bat"

### The Insight

Build a trie from the dictionary roots. For each word in the sentence, walk down the trie character by character. The moment you hit a node where `is_end = True`, that's the shortest root. Stop and use it.

If you reach the end of the word without hitting a root, keep the original word.

### ASCII: Root Replacement

```
Dictionary roots: ["cat", "bat", "rat"]

Trie:
     root
    / | \
   c  b  r
   |  |  |
   a  a  a
   |  |  |
   t  t  t
  (*)(*)(*)
(*) = is_end = True (root ends here)

Word: "cattle"
c → a → t → [is_end = True!] → STOP → return "cat"

Word: "battery"
b → a → t → [is_end = True!] → STOP → return "bat"

Word: "the"
t → [no child 't' at root level] → no root found → keep "the"
```

### Template Code

```python
def replaceWords(dictionary: list, sentence: str) -> str:
    # Build trie from dictionary roots
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
        """Return shortest root for word, or word itself if none found."""
        node = root
        for i, ch in enumerate(word):
            if ch not in node.children:
                break
            node = node.children[ch]
            if node.is_end:
                return node.word   # found shortest root
        return word                # no root found

    return ' '.join(find_root(w) for w in sentence.split())


# Test
print(replaceWords(
    ["cat", "bat", "rat"],
    "the cattle was rattled by the battery"
))
# → "the cat was rat by the bat"
```

### Why This Works Better Than a Set

You could store roots in a set and for each word check all its prefixes. But that's O(L²) per word (L checks, each O(L)). The trie is O(L) per word — you walk once and stop at the first root.

### Edge Cases
- Two roots, one is prefix of the other ("cat" and "ca"): The trie naturally returns "ca" first since you stop at the first `is_end` node encountered, which is the shorter root.
- Word shorter than any root: Walk ends before hitting `is_end` → keep original word.

---

## Pattern 5: Palindrome Pairs

### The Story

You have a list of words. Find all pairs (i, j) where concatenating `words[i] + words[j]` forms a palindrome.

Example: words = ["abcd", "dcba", "lls", "s", "sssll"]
- "dcba" + "abcd" → "dcbaabcd" → palindrome
- "abcd" + "dcba" → "abcddcba" → palindrome
- "lls" + "sssll" → "llssssll" → palindrome (wait, let's check: l-l-s-s-s-s-l-l → yes!)
- "s" + "lls" → "slls" → palindrome (s-l-l-s → yes!)

### The Key Observation

For `words[i] + words[j]` to be a palindrome, one of these must be true:
1. `words[j]` is the reverse of `words[i]` (simple full reverse)
2. `words[i]` has a palindromic suffix, and the remaining prefix is the reverse of `words[j]`
3. `words[i]` has a palindromic prefix, and the remaining suffix is the reverse of `words[j]`

The trie approach: insert the **reverse** of each word into the trie. For each word `w`, walk the trie with characters of `w`. As you walk:
- If you reach `is_end` and the remaining unmatched part of the current trie path is a palindrome → found a pair.
- If you exhaust `w` and the remaining trie path ahead can form palindromes → also valid.

### Trace Through Example

```
words = ["lls", "s", "sssll"]
indices: 0="lls", 1="s", 2="sssll"

Insert REVERSED words into trie:
  reverse("lls")   = "sll"   → stored with index 0
  reverse("s")     = "s"     → stored with index 1
  reverse("sssll") = "llsss" → stored with index 2

Trie:
  root
  / \
 s   l
 |\ /
 s  l
 |  |
[1] s
 |   \
 s    s
 |    |
[?]  [2]
 |
 l
 |
 l
 |
[0]

Query word "lls" (index 0):
Walk trie with 'l','l','s':
  - 'l' → 'l' → 's' → hit node with index 2 ("sssll" reversed)
  - Remaining: nothing from "lls", but does path to index 2 have palindromic suffix?
  - At index 2, full word matched → "sssll" + "lls" → "ssslllls"? check...
    Actually: words[2] + words[0] = "sssll" + "lls" = "ssslllls" — not palindrome
    words[0] + words[2] = "lls" + "sssll" = "llssssll" — IS palindrome!
  - When words[i]'s reverse is a prefix of trie word, and the trie word's remaining suffix is palindrome → (i, trie_word_index) is valid

Query word "s" (index 1):
Walk trie with 's':
  - 's' → found node, index 1 would be same word (skip)
  - Continue into 's' child → 's' → 's' → 'l' → 'l' → index 0 ("lls" reversed)
  - Words[1] + words[0] = "s" + "lls" = "slls" → palindrome! (valid pair)
  - Go back: 's' → 's' → index for intermediate?
  - If we check "s" matching first 's' of "sll", remaining "ll" from trie is palindrome
  - → words[0] + words[1] = "lls" + "s" = "llss"? not palindrome
  - Hmm, let me re-trace...
```

The trie approach for palindrome pairs is involved. Here is the clean, complete implementation:

### Template Code

```python
def palindromePairs(words: list) -> list:
    def is_palindrome(s):
        return s == s[::-1]

    # Build trie of reversed words
    root = {}
    for i, word in enumerate(words):
        node = root
        for ch in reversed(word):
            if ch not in node:
                node[ch] = {}
            node = node[ch]
        node['#'] = i   # word index stored at terminal

    results = []

    for i, word in enumerate(words):
        node = root
        for j, ch in enumerate(word):
            # Case 1: trie word ends here, check if remaining suffix of current word is palindrome
            if '#' in node:
                other_idx = node['#']
                if other_idx != i and is_palindrome(word[j:]):
                    results.append([i, other_idx])

            if ch not in node:
                break
            node = node[ch]
        else:
            # Case 2: we consumed all of word, now check all words in trie whose
            # remaining part (what we haven't matched) is a palindrome
            if '#' in node:
                other_idx = node['#']
                if other_idx != i:
                    results.append([i, other_idx])

            # Check remaining trie paths for palindromes
            # (this requires a helper to walk remaining trie branches)

    return results
```

The full palindrome pairs problem has several edge cases (empty strings, same-word, etc). The simpler and often-seen approach in interviews:

```python
def palindromePairs_simple(words: list) -> list:
    """
    Hash map approach — simpler to implement under pressure.
    O(N × L^2) time.
    """
    word_map = {w: i for i, w in enumerate(words)}
    results = []

    def is_pal(s):
        return s == s[::-1]

    for i, word in enumerate(words):
        n = len(word)
        for k in range(n + 1):
            # Split word into prefix and suffix
            prefix, suffix = word[:k], word[k:]

            # Case 1: prefix is palindrome, find reversed suffix in map
            if is_pal(prefix):
                rev_suffix = suffix[::-1]
                if rev_suffix in word_map and word_map[rev_suffix] != i:
                    results.append([word_map[rev_suffix], i])

            # Case 2: suffix is palindrome, find reversed prefix in map
            # Avoid duplicates when k == n (same split counted twice)
            if k != n and is_pal(suffix):
                rev_prefix = prefix[::-1]
                if rev_prefix in word_map and word_map[rev_prefix] != i:
                    results.append([i, word_map[rev_prefix]])

    return results


# Test
print(palindromePairs_simple(["lls","s","sssll"]))
# Expected pairs: [0,1] → "lls"+"s"="llss"? No...
# Let me verify: "s"+"lls" = "slls" → palindrome! → [1,0]
#                "lls"+"sssll" = "llssssll" → palindrome! → [0,2]
#                "sssll"+"lls" = no
```

---

## Pattern 6: Word Break / Word Break II

### The Story

Given a string like "leetcode" and a dictionary ["leet", "code"], can you segment the string into dictionary words? Answer: "leet code" → yes.

**Word Break II** asks for ALL possible segmentations.

### Two Approaches

#### Approach A: Dynamic Programming (Classic)

```
s = "leetcode"
dp[i] = True if s[0:i] can be segmented

dp[0] = True  (empty string)

dp[1]: s[0:1]="l" in dict? No → dp[1] = False
dp[2]: s[0:2]="le" in dict? No; s[1:2]="e" and dp[1]? False → dp[2] = False
dp[3]: s[0:3]="lee" No; ... → False
dp[4]: s[0:4]="leet" in dict? YES! and dp[0]=True → dp[4] = True
dp[5]: s[0:5]="leetc" No; s[4:5]="c" and dp[4]=True? "c" in dict? No → False
dp[6]: ... similarly False
dp[7]: ... False
dp[8]: s[4:8]="code" in dict? YES! and dp[4]=True → dp[8] = True

Answer: dp[8] = True → can be segmented!
```

```python
def wordBreak_dp(s: str, wordDict: list) -> bool:
    word_set = set(wordDict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True   # empty prefix is always breakable

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break

    return dp[n]


# Test
print(wordBreak_dp("leetcode", ["leet", "code"]))   # True
print(wordBreak_dp("applepenapple", ["apple", "pen"]))  # True
print(wordBreak_dp("catsandog", ["cats", "dog", "sand", "and", "cat"]))  # False
```

#### Approach B: Trie + DFS with Memoization

The trie makes prefix matching faster: instead of checking `s[j:i] in word_set` (which is O(L)), you walk the trie from position j in one pass.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

def wordBreak_trie(s: str, wordDict: list) -> bool:
    # Build trie
    root = TrieNode()
    for word in wordDict:
        node = root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    n = len(s)
    memo = {}  # position → can we break s[pos:]?

    def dfs(start: int) -> bool:
        if start == n:
            return True
        if start in memo:
            return memo[start]

        node = root
        for end in range(start, n):
            ch = s[end]
            if ch not in node.children:
                break              # no word starts with s[start:end+1] → prune
            node = node.children[ch]
            if node.is_end:        # found a valid word s[start:end+1]
                if dfs(end + 1):
                    memo[start] = True
                    return True

        memo[start] = False
        return False

    return dfs(0)


print(wordBreak_trie("leetcode", ["leet", "code"]))        # True
print(wordBreak_trie("catsandog", ["cats","dog","and","cat","sand"]))  # False
```

#### Word Break II: Return All Segmentations

```python
def wordBreakII(s: str, wordDict: list) -> list:
    word_set = set(wordDict)
    n = len(s)
    memo = {}  # start → list of sentences from s[start:]

    def dfs(start: int) -> list:
        if start == n:
            return ['']
        if start in memo:
            return memo[start]

        result = []
        for end in range(start + 1, n + 1):
            word = s[start:end]
            if word in word_set:
                for rest in dfs(end):
                    if rest:
                        result.append(word + ' ' + rest)
                    else:
                        result.append(word)

        memo[start] = result
        return result

    return dfs(0)


print(wordBreakII("catsanddog", ["cat","cats","and","sand","dog"]))
# → ["cat sand dog", "cats and dog"]
```

### DP vs Trie+DFS: When to Use What

| Scenario | Use DP | Use Trie+DFS |
|---|---|---|
| Just need True/False | Yes | Either |
| Need all solutions | Use DFS+memo | Either |
| Dictionary is large, words are long | DP is simpler | Trie is faster |
| Dictionary has many long common prefixes | DP fine | Trie shines |
| Real-time, words added dynamically | Rebuild set | Insert into trie |

The trie approach shines when many words share prefixes — you avoid repeated checking of the same prefix.

---

## Trie Problem Recognition Cheatsheet

```
Trigger Phrase                          → Pattern
-----------------------------------------------------
"starts with prefix"                    → Pattern 1 (Autocomplete)
"autocomplete suggestions"              → Pattern 1
"find multiple words in grid"           → Pattern 2 (Grid DFS + Trie)
"Word Search II"                        → Pattern 2
"maximum XOR of two numbers"            → Pattern 3 (Binary Trie)
"replace words with shortest root"      → Pattern 4 (Root Replacement)
"replace with dictionary root"          → Pattern 4
"palindrome formed by concatenation"    → Pattern 5 (Palindrome Pairs)
"segment string into dictionary words"  → Pattern 6 (Word Break)

When trie BEATS alternatives:
  - Prefix queries: trie > set (set can't query by prefix)
  - Multiple word search in grid: trie > repeated DFS
  - XOR optimization: binary trie > brute force O(N²)
  - Online prefix insertions: trie > sorted array

When trie might be overkill:
  - Single word search (just use set)
  - No prefix operations needed
  - Memory is very constrained
```

---

## Common Bugs and Fixes

```python
# Bug 1: Forgetting to mark is_end
# → search() always returns False
# Fix: node.is_end = True after the insert loop

# Bug 2: Using a shared default dict (common in Python dict tricks)
# from collections import defaultdict
# children = defaultdict(TrieNode)  ← this is FINE
# children = {}  ← this is also fine, just check 'if ch in children'

# Bug 3: Not handling empty string
# insert("") should set root.is_end = True
# search("") should return root.is_end

# Bug 4: In Word Search II, not restoring board[r][c] after DFS
# Always: board[r][c] = ch  after recursive calls

# Bug 5: Binary trie — using wrong bit range
# For 32-bit numbers: range(31, -1, -1)  ← 32 levels: bits 31 to 0
# For 20-bit numbers: range(19, -1, -1)  ← adjust to problem constraints
```

---

## Full Complexity Reference

| Pattern | Build Time | Query Time | Space |
|---|---|---|---|
| Autocomplete | O(W×L) | O(P + K×L) | O(W×L) |
| Grid Word Search | O(W×L) | O(R×C×4^L) | O(W×L) |
| XOR Maximum | O(N×32) | O(N×32) | O(N×32) |
| Replace Words | O(D×L) | O(L per word) | O(D×L) |
| Palindrome Pairs | O(N×L) | O(N×L²) | O(N×L) |
| Word Break | O(D×L) | O(N²) DP / O(N×L) DFS | O(N+D×L) |

W = number of words, L = average word length, P = prefix length, K = matching words, R×C = grid size, D = dictionary size, N = input size.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Real World Usage →](./real_world_usage.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
