# Trie — Real World Usage

A trie (prefix tree) stores strings character by character, making prefix-based operations
O(m) where m is the string length — independent of how many strings are stored. This makes
tries the data structure of choice for any system where you ask "what strings start with this
prefix?" or "what is the longest matching prefix?"

---

## 1. Search Autocomplete — Google and YouTube Suggestions

Google processes 8.5 billion searches per day. The instant suggestions that appear as you
type are powered by trie-based prefix lookups over a precomputed set of popular queries,
combined with personalization signals. YouTube's search bar, Spotify's track search, and
Amazon's product search all use variants of this pattern. The trie lookup itself is O(m)
where m is what you've typed so far.

```python
from collections import defaultdict
import heapq

class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end = False
        self.frequency = 0      # search frequency for ranking


class SearchAutocomplete:
    """
    Prefix-based search autocomplete system.
    Used by: Google Search, YouTube, Spotify, Amazon product search

    Design principle: insert all popular queries at startup,
    then get_suggestions(prefix) returns the top-k by frequency.
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, frequency: int = 1):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.frequency = max(node.frequency, frequency)

    def _collect_all(self, node: TrieNode, prefix: str) -> list[tuple[int, str]]:
        """DFS to collect all words under a node with frequencies."""
        results = []
        if node.is_end:
            results.append((-node.frequency, prefix))   # negative for min-heap max behavior
        for char, child in node.children.items():
            results.extend(self._collect_all(child, prefix + char))
        return results

    def get_suggestions(self, prefix: str, top_k: int = 5) -> list[str]:
        """Return top-k suggestions for a given prefix."""
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []   # no words with this prefix
            node = node.children[char]

        candidates = self._collect_all(node, prefix.lower())
        # Sort by frequency descending (stored as negatives)
        candidates.sort()
        return [word for _, word in candidates[:top_k]]


# Load with realistic search frequencies
autocomplete = SearchAutocomplete()
queries = [
    ("python tutorial", 95000),
    ("python list comprehension", 72000),
    ("python dictionary", 68000),
    ("python string format", 61000),
    ("python install", 58000),
    ("python f-string", 54000),
    ("python sort list", 49000),
    ("pytorch tutorial", 88000),
    ("pytorch vs tensorflow", 45000),
    ("postgresql", 67000),
    ("postgresql tutorial", 55000),
    ("postgresql json", 38000),
]

for query, freq in queries:
    autocomplete.insert(query, freq)

for prefix in ["py", "pyt", "pyth", "post"]:
    suggestions = autocomplete.get_suggestions(prefix, top_k=3)
    print(f"  '{prefix}' -> {suggestions}")
# 'py'   -> ['python tutorial', 'pytorch tutorial', 'python list comprehension']
# 'pyth' -> ['python tutorial', 'python list comprehension', 'python dictionary']
```

---

## 2. Spell Checker — Fuzzy Matching with Edit Distance

Microsoft Word, Google Docs, browser spell-checkers, and IDE spell-check plugins need to find
all dictionary words within edit distance 1 or 2 of a misspelled word. A trie lets you do
this with DFS while tracking the current edit count and pruning branches that have exceeded
the allowed distance — far faster than comparing against every dictionary word individually.

```python
class SpellChecker:
    """
    Trie-based spell checker with fuzzy matching.
    Used by: Microsoft Word, Google Docs, browser spellcheck (Hunspell),
             IDEs (VS Code, JetBrains), mobile keyboard autocorrect
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search_within_distance(self, word: str, max_distance: int = 1) -> list[str]:
        """
        Find all dictionary words within edit distance `max_distance` of `word`.
        Uses DFS on trie with a running edit distance — prune when distance exceeded.
        """
        results = []

        def dfs(node, trie_path, word_idx, deletions, insertions, substitutions):
            current_dist = deletions + insertions + substitutions
            if current_dist > max_distance:
                return

            if node.is_end:
                # We've matched a complete dictionary word
                # word_idx must be at end (or we used deletions to finish early)
                remaining = len(word) - word_idx
                total = current_dist + remaining
                if total <= max_distance:
                    results.append("".join(trie_path))

            if word_idx >= len(word):
                # Word exhausted — only trie insertions remain
                for char, child in node.children.items():
                    dfs(child, trie_path + [char], word_idx,
                        deletions, insertions + 1, substitutions)
                return

            current_char = word[word_idx]
            for char, child in node.children.items():
                if char == current_char:
                    # Exact match — no edit needed
                    dfs(child, trie_path + [char], word_idx + 1,
                        deletions, insertions, substitutions)
                else:
                    # Substitution: advance both
                    dfs(child, trie_path + [char], word_idx + 1,
                        deletions, insertions, substitutions + 1)
                    # Insertion into trie position (skip trie char, don't advance word)
                    dfs(child, trie_path + [char], word_idx,
                        deletions, insertions + 1, substitutions)

            # Deletion: skip this word character (don't advance in trie)
            dfs(node, trie_path, word_idx + 1,
                deletions + 1, insertions, substitutions)

        dfs(self.root, [], 0, 0, 0, 0)
        return list(set(results))


checker = SpellChecker()
dictionary = ["hello", "helo", "hell", "help", "held", "hero", "here",
              "world", "word", "wore", "more", "core", "code", "coke"]
for w in dictionary:
    checker.insert(w)

misspelled = ["helllo", "wrold", "helo", "cod"]
for typo in misspelled:
    suggestions = checker.search_within_distance(typo, max_distance=1)
    print(f"  '{typo}' -> suggestions: {sorted(suggestions)}")
```

---

## 3. IP Routing (CIDR) — Longest Prefix Match

Every internet router — Cisco, Juniper, Arista — uses a trie of IP prefixes to forward packets.
When a packet arrives for 192.168.1.50, the router searches its routing table for the longest
matching prefix (e.g., 192.168.1.0/24 beats 192.168.0.0/16). This is called Longest Prefix
Match (LPM) and is implemented as a binary trie of IP address bits in hardware FIB (Forwarding
Information Base) tables. Software-defined networks (AWS VPC routing, Kubernetes CNI) implement
the same logic in software.

```python
class IPRouter:
    """
    Longest Prefix Match IP router using a binary trie.
    Each level represents one bit of the IP address.

    Used by: Cisco IOS, Linux kernel netfilter, AWS VPC route tables,
             Kubernetes kube-proxy, iptables, OpenVSwitch
    """
    class Node:
        def __init__(self):
            self.children = [None, None]   # [0-bit, 1-bit]
            self.route = None              # next-hop if this is a prefix end

    def __init__(self):
        self.root = self.Node()

    @staticmethod
    def _ip_to_bits(ip: str) -> list[int]:
        parts = [int(p) for p in ip.split(".")]
        bits = []
        for part in parts:
            for i in range(7, -1, -1):
                bits.append((part >> i) & 1)
        return bits

    def add_route(self, cidr: str, next_hop: str):
        """Add a CIDR prefix to the routing table."""
        ip, prefix_len = cidr.split("/")
        bits = self._ip_to_bits(ip)[:int(prefix_len)]

        node = self.root
        for bit in bits:
            if node.children[bit] is None:
                node.children[bit] = self.Node()
            node = node.children[bit]
        node.route = next_hop

    def lookup(self, ip: str) -> str:
        """Find the best (longest matching) route for an IP address."""
        bits = self._ip_to_bits(ip)
        node = self.root
        best_route = "default-drop"

        for bit in bits:
            if node.route:
                best_route = node.route    # update best match as we go deeper
            if node.children[bit] is None:
                break
            node = node.children[bit]

        if node.route:
            best_route = node.route
        return best_route


router = IPRouter()
# Simulating an AWS VPC route table
router.add_route("0.0.0.0/0",      "internet-gateway")        # default route
router.add_route("10.0.0.0/8",     "vpc-peering-prod")        # RFC 1918
router.add_route("10.100.0.0/16",  "transit-gateway")         # specific VPC
router.add_route("10.100.1.0/24",  "subnet-us-east-1a")       # specific subnet
router.add_route("172.16.0.0/12",  "vpn-gateway")
router.add_route("192.168.0.0/16", "on-premise-vpn")

test_ips = [
    "10.100.1.55",    # matches /24 (most specific)
    "10.100.5.10",    # matches /16
    "10.50.0.1",      # matches /8
    "8.8.8.8",        # matches default
    "192.168.1.1",    # matches on-premise VPN
]

for ip in test_ips:
    print(f"  {ip:18s} -> {router.lookup(ip)}")
```

---

## 4. T9 Keyboard — Phone Number to Word Mapping

T9 (Text on 9 keys) was the predictive text system used on Nokia and Motorola phones before
touchscreens. It's still used in feature phones (2+ billion users globally), industrial
terminals, and number-pad input devices. Modern implementations of T9 use a trie where each
node stores the phone key that maps to its character.

```python
class T9Keyboard:
    """
    T9 predictive text using a trie mapping digit sequences to words.
    Used by: Nokia feature phones, industrial HMI terminals,
             TV remote text input, car infotainment systems
    """
    KEYMAP = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"
    }
    CHAR_TO_KEY = {ch: key for key, chars in KEYMAP.items() for ch in chars}

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def _word_to_digits(self, word: str) -> str:
        return "".join(self.CHAR_TO_KEY.get(c, "") for c in word.lower())

    def get_words(self, digits: str) -> list[str]:
        """
        Return all dictionary words that map to the given digit sequence.
        E.g., "4663" -> ["gone", "good", "home", "hood", "hone"]
        """
        results = []

        def dfs(node, path, digit_idx):
            if digit_idx == len(digits):
                if node.is_end:
                    results.append("".join(path))
                return

            digit = digits[digit_idx]
            valid_chars = self.KEYMAP.get(digit, "")

            for char in valid_chars:
                if char in node.children:
                    dfs(node.children[char], path + [char], digit_idx + 1)

        dfs(self.root, [], 0)
        return results


t9 = T9Keyboard()
words = ["act", "cat", "bat", "bad", "ace", "age", "aged",
         "home", "good", "gone", "hood", "hone", "golf",
         "python", "data", "code", "node", "mode", "mode"]
for w in words:
    t9.insert(w)

test_sequences = [
    ("228", "cat/bat/act/ace"),
    ("4663", "home/good/gone"),
    ("2633", "code/mode"),
]

for digits, hint in test_sequences:
    words_found = t9.get_words(digits)
    print(f"  {digits} ({hint}): {words_found}")
```

---

## 5. Boggle Solver — Find All Valid Words in a Grid

Boggle is a word game where you find words by connecting adjacent letters on a 4x4 grid. The
commercial Boggle game app (Hasbro Digital), Words with Friends, and similar games need to
enumerate all valid words in a given grid in milliseconds. Loading the entire dictionary into
a trie and using it during DFS grid traversal makes it practical — you prune entire branches
when no dictionary word can start with the current prefix.

```python
class BoggleSolver:
    """
    Find all valid dictionary words on a Boggle grid.
    Uses trie for O(1) prefix checking during DFS traversal.

    Used by: Hasbro Boggle app, Words With Friends, Wordament (Microsoft),
             Scramble with Friends, Letterpress
    """
    def __init__(self):
        self.root = TrieNode()

    def load_dictionary(self, words: list[str]):
        for word in words:
            node = self.root
            for char in word.lower():
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.is_end = True

    def find_all_words(self, grid: list[list[str]]) -> list[str]:
        rows, cols = len(grid), len(grid[0])
        found = set()

        def dfs(r, c, node, path, visited):
            char = grid[r][c].lower()
            if char not in node.children:
                return   # prune: no word in dictionary starts with current path + char

            next_node = node.children[char]
            path.append(char)
            visited.add((r, c))

            if next_node.is_end and len(path) >= 3:   # Boggle: min 3 letters
                found.add("".join(path))

            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                        dfs(nr, nc, next_node, path, visited)

            path.pop()
            visited.remove((r, c))

        for r in range(rows):
            for c in range(cols):
                dfs(r, c, self.root, [], set())

        return sorted(found, key=len, reverse=True)


solver = BoggleSolver()
solver.load_dictionary([
    "eat", "ate", "tea", "eta", "sat", "rat", "tar", "art", "rate",
    "tear", "read", "dear", "idea", "data", "date", "trade", "rated",
    "tread", "dater", "irate", "tirade"
])

boggle_grid = [
    ["T", "E", "A", "D"],
    ["R", "I", "T", "A"],
    ["S", "A", "T", "E"],
    ["D", "E", "R", "S"],
]

words_found = solver.find_all_words(boggle_grid)
print(f"Grid:")
for row in boggle_grid:
    print("  " + " ".join(row))
print(f"\nWords found ({len(words_found)}):")
for word in words_found:
    print(f"  {word} ({len(word)} letters)")
```

---

## 6. IDE Code Completion — Symbol Indexing

VS Code, JetBrains IntelliJ, Sublime Text, and Neovim's language servers (LSP) all maintain
a trie of every symbol (function name, class name, variable) in your project. As you type,
the completion engine does a prefix lookup and ranks results by recency, frequency, and
type relevance. Large codebases at Google and Meta have millions of symbols indexed this way.

```python
from dataclasses import dataclass, field

@dataclass
class Symbol:
    name: str
    kind: str           # "function", "class", "variable", "module"
    file_path: str
    line: int
    usage_count: int = 0


class CodeCompleter:
    """
    IDE symbol completion using a trie.
    Used by: VS Code (TypeScript language server), IntelliJ IDEA,
             PyCharm, GitHub Copilot (symbol context), clangd

    Real implementation also includes: fuzzy matching, type-aware filtering,
    recently-used boosting, and semantic embeddings for ML-based ranking.
    """
    class Node:
        def __init__(self):
            self.children: dict[str, "CodeCompleter.Node"] = {}
            self.symbols: list[Symbol] = []   # symbols completing at this node

    def __init__(self):
        self.root = self.Node()

    def index_symbol(self, symbol: Symbol):
        node = self.root
        for char in symbol.name.lower():
            if char not in node.children:
                node.children[char] = self.Node()
            node = node.children[char]
        node.symbols.append(symbol)

    def complete(self, prefix: str, kind_filter: str | None = None, top_k: int = 8) -> list[Symbol]:
        """Return top-k symbol completions for a given prefix."""
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        # Collect all symbols under this prefix node
        all_symbols = []
        def collect(n):
            all_symbols.extend(n.symbols)
            for child in n.children.values():
                collect(child)
        collect(node)

        # Filter by kind if specified
        if kind_filter:
            all_symbols = [s for s in all_symbols if s.kind == kind_filter]

        # Rank by usage count (most-used first), then alphabetically
        all_symbols.sort(key=lambda s: (-s.usage_count, s.name))
        return all_symbols[:top_k]


completer = CodeCompleter()
symbols = [
    Symbol("get_user",            "function", "api/users.py",    45, 234),
    Symbol("get_user_by_email",   "function", "api/users.py",    67, 89),
    Symbol("get_user_profile",    "function", "api/profile.py",  12, 156),
    Symbol("getUserById",         "function", "frontend/api.ts",  8, 312),
    Symbol("GenerateToken",       "function", "auth/jwt.py",     23, 78),
    Symbol("get_all_orders",      "function", "api/orders.py",   91, 45),
    Symbol("GraphQLResolver",     "class",    "graphql/base.py",  5, 23),
    Symbol("get_cached_result",   "function", "cache/redis.py",  34, 190),
]

for sym in symbols:
    completer.index_symbol(sym)

print("Completions for 'get':")
for s in completer.complete("get", top_k=5):
    print(f"  {s.name:30s} ({s.kind}) — used {s.usage_count}x in {s.file_path}")

print("\nCompletions for 'ge' (functions only):")
for s in completer.complete("ge", kind_filter="function", top_k=4):
    print(f"  {s.name:30s} — line {s.line}")
```

---

## Key Takeaways

| Use Case | Trie Operation | Complexity | System |
|---|---|---|---|
| Search autocomplete | Prefix walk + DFS collect | O(m + k) | Google, YouTube, Spotify |
| Spell checking | DFS with edit distance budget | O(26^m) pruned | Word, Docs, Hunspell |
| IP routing (LPM) | Binary trie walk on bits | O(32) or O(128) | Cisco IOS, Linux netfilter |
| T9 keyboard | Digit-to-char mapping + DFS | O(4^m) | Nokia, TV remotes |
| Boggle solver | Grid DFS + trie prefix pruning | O(rows*cols*4^m) | Word games |
| IDE completion | Prefix walk + ranked collect | O(m + k log k) | VS Code, IntelliJ |

The fundamental advantage of a trie over a hash map for string problems: **prefix operations are
natural**. A hash map gives you O(1) exact lookup but O(n) prefix search; a trie gives O(m)
for both, where m is the string length. When your application is prefix-heavy — autocomplete,
routing, spell checking — the trie is the right tool.
