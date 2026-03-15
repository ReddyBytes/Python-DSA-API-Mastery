# Strings — Real World Usage

Strings are sequences of characters, but at the systems level they are byte arrays with encoding.
String algorithms power search engines, compilers, network security tools, and genomics.

---

## 1. Full-Text Search Engines — Inverted Index and Multi-Pattern Matching

Google, Elasticsearch, and Lucene do not scan every document for every query.
They preprocess documents into an inverted index: a hash map from term to list of document IDs.
At query time, a word lookup is O(1) in the index rather than O(n * m) brute force.

For multi-pattern matching (find many keywords simultaneously in one pass),
Aho-Corasick automaton is used. It builds a trie of all patterns and adds failure links,
enabling O(n + m + z) where n is text length, m is total pattern length, z is match count.

```python
# Inverted index — the heart of every search engine
from collections import defaultdict

def build_inverted_index(documents: list) -> dict:
    index = defaultdict(set)
    for doc_id, text in enumerate(documents):
        tokens = text.lower().split()
        for token in tokens:
            # Remove punctuation (real engines use tokenizers + stemmers)
            token = token.strip(".,!?")
            index[token].add(doc_id)
    return dict(index)

def search(index: dict, query: str) -> set:
    """AND search across all query terms."""
    terms = query.lower().split()
    if not terms:
        return set()
    result = index.get(terms[0], set())
    for term in terms[1:]:
        result = result & index.get(term, set())  # intersection
    return result

docs = [
    "Python is a high level programming language",
    "Python is used in data science and machine learning",
    "Java is a compiled programming language",
    "Data science requires statistics and programming",
]

index = build_inverted_index(docs)
print(search(index, "python programming"))  # {0} — only doc 0 has both
print(search(index, "programming language")) # {0, 2}

# KMP — find a single pattern in O(n+m), used in grep, log scanners
def kmp_search(text: str, pattern: str) -> list:
    if not pattern:
        return []
    # Build failure function
    m = len(pattern)
    fail = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = fail[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        fail[i] = j
    # Search
    matches = []
    j = 0
    for i, ch in enumerate(text):
        while j > 0 and ch != pattern[j]:
            j = fail[j - 1]
        if ch == pattern[j]:
            j += 1
        if j == m:
            matches.append(i - m + 1)
            j = fail[j - 1]
    return matches

log_line = "2024-01-15 ERROR database connection failed ERROR retry"
print(kmp_search(log_line, "ERROR"))  # [11, 47]
```

Elasticsearch uses the BM25 ranking algorithm on top of an inverted index.
KMP is used in `grep`, `awk`, and every log analysis tool.

---

## 2. DNA Sequence Analysis — String Algorithms in Bioinformatics

DNA is a string over the alphabet {A, T, G, C}.
The human genome is ~3 billion characters. Bioinformatics is entirely string algorithm problems.

Key operations:
- Sequence alignment: find where a short read matches the genome (inexact matching).
- Smith-Waterman: dynamic programming for local sequence alignment (O(nm)).
- Suffix arrays: preprocess the genome for O(m log n) query of any pattern.

```python
# Smith-Waterman local alignment — finds best matching substring
# Used in BLAST (Basic Local Alignment Search Tool) at NCBI

def smith_waterman(seq1: str, seq2: str, match=2, mismatch=-1, gap=-1):
    """Find the best local alignment between seq1 and seq2."""
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_score = 0
    max_pos = (0, 0)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            score = match if seq1[i-1] == seq2[j-1] else mismatch
            dp[i][j] = max(
                0,                          # local alignment: reset at 0
                dp[i-1][j-1] + score,       # diagonal: match/mismatch
                dp[i-1][j] + gap,           # up: gap in seq2
                dp[i][j-1] + gap,           # left: gap in seq1
            )
            if dp[i][j] > max_score:
                max_score = dp[i][j]
                max_pos = (i, j)

    return max_score, max_pos

# Genome fragment and a read
genome   = "ACGTTAGCTTACGATCGAT"
read     = "TTACGA"
score, pos = smith_waterman(genome, read)
print(f"Alignment score: {score}, ending at genome pos {pos}")

# Simple exact pattern count — used in k-mer frequency analysis
def kmer_frequency(sequence: str, k: int) -> dict:
    """Count all k-mers (k-length substrings) in a sequence."""
    freq = {}
    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i+k]
        freq[kmer] = freq.get(kmer, 0) + 1
    return freq

dna = "ACGTACGTTTACGT"
kmers = kmer_frequency(dna, k=3)
print(sorted(kmers.items(), key=lambda x: -x[1])[:3])  # top 3-mers
```

Real-world scale: BWA (Burrows-Wheeler Aligner) uses BWT (Burrows-Wheeler Transform)
to align short reads to a reference genome in O(m log n) per read.
23andMe and Illumina sequencers run these algorithms on millions of reads per second.

---

## 3. Network Packet Inspection — Deep Packet Inspection

Firewalls, intrusion detection systems (Snort, Suricata), and content filters
scan network packets for malicious patterns.

A packet payload is a byte string. DPI tools match it against thousands of signatures
simultaneously using Aho-Corasick (multi-pattern matching).

```python
# Simulating DPI signature matching with Aho-Corasick concept
from collections import deque

class SimpleAhoCorasick:
    """Simplified Aho-Corasick for multi-pattern matching."""

    def __init__(self, patterns: list):
        self.goto = [{}]
        self.fail = [0]
        self.output = [[]]
        self._build(patterns)

    def _build(self, patterns):
        for pattern in patterns:
            state = 0
            for ch in pattern:
                if ch not in self.goto[state]:
                    self.goto[state][ch] = len(self.goto)
                    self.goto.append({})
                    self.fail.append(0)
                    self.output.append([])
                state = self.goto[state][ch]
            self.output[state].append(pattern)

        # Build failure links via BFS
        queue = deque()
        for ch, s in self.goto[0].items():
            self.fail[s] = 0
            queue.append(s)
        while queue:
            r = queue.popleft()
            for ch, s in self.goto[r].items():
                queue.append(s)
                state = self.fail[r]
                while state != 0 and ch not in self.goto[state]:
                    state = self.fail[state]
                self.fail[s] = self.goto[state].get(ch, 0)
                if self.fail[s] == s:
                    self.fail[s] = 0
                self.output[s] += self.output[self.fail[s]]

    def search(self, text: str) -> list:
        state = 0
        matches = []
        for i, ch in enumerate(text):
            while state != 0 and ch not in self.goto[state]:
                state = self.fail[state]
            state = self.goto[state].get(ch, 0)
            for pattern in self.output[state]:
                matches.append((i - len(pattern) + 1, pattern))
        return matches

# DPI signature database (simplified — real ones have thousands)
malware_signatures = ["exec(", "eval(", "/etc/passwd", "DROP TABLE", "<script>"]
dpi = SimpleAhoCorasick(malware_signatures)

# Inspect incoming HTTP payload
payload = 'GET /api?q=<script>alert(1)</script> HTTP/1.1'
threats = dpi.search(payload)
print(f"Threats detected: {threats}")
# Output: [(10, '<script>')]

sql_payload = "'; DROP TABLE users; --"
threats = dpi.search(sql_payload)
print(f"SQL injection detected: {threats}")
```

Snort processes millions of packets per second using this approach.
Every corporate firewall and cloud WAF (AWS WAF, Cloudflare) uses multi-pattern string matching.

---

## 4. Log Parsing — Regex and String Matching in Production

Application logs are unstructured strings. Parsing them requires pattern matching.
Logstash, Fluent Bit, and CloudWatch Logs Insights use regex and substring matching
to extract structured fields (timestamp, log level, request ID) from raw log lines.

```python
import re
from datetime import datetime

# Nginx access log format:
# 192.168.1.1 - - [15/Jan/2024:10:22:35 +0000] "GET /api/users HTTP/1.1" 200 1234

LOG_PATTERN = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+) '
    r'- - \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\w+) (?P<path>[^ ]+) HTTP/[\d.]+" '
    r'(?P<status>\d+) '
    r'(?P<bytes>\d+)'
)

def parse_log_line(line: str) -> dict | None:
    match = LOG_PATTERN.match(line)
    if not match:
        return None
    d = match.groupdict()
    d["status"] = int(d["status"])
    d["bytes"] = int(d["bytes"])
    return d

logs = [
    '192.168.1.1 - - [15/Jan/2024:10:22:35 +0000] "GET /api/users HTTP/1.1" 200 1234',
    '10.0.0.5 - - [15/Jan/2024:10:22:36 +0000] "POST /api/login HTTP/1.1" 401 89',
    '192.168.1.1 - - [15/Jan/2024:10:22:37 +0000] "GET /api/data HTTP/1.1" 500 512',
]

parsed = [parse_log_line(line) for line in logs]
errors = [e for e in parsed if e and e["status"] >= 500]
print(f"5xx errors: {len(errors)}")
for err in errors:
    print(f"  {err['method']} {err['path']} -> {err['status']}")

# KMP for fast fixed-string search in logs (faster than regex for literals)
error_positions = kmp_search(" ".join(logs), "HTTP/1.1\" 5")
print(f"KMP found HTTP 5xx at positions: {error_positions}")

def kmp_search(text: str, pattern: str) -> list:
    m = len(pattern)
    if m == 0:
        return []
    fail = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = fail[j-1]
        if pattern[i] == pattern[j]:
            j += 1
        fail[i] = j
    matches = []
    j = 0
    for i, ch in enumerate(text):
        while j > 0 and ch != pattern[j]:
            j = fail[j-1]
        if ch == pattern[j]:
            j += 1
        if j == m:
            matches.append(i - m + 1)
            j = fail[j-1]
    return matches
```

In production, Logstash's Grok filter is a library of named regex patterns.
`%{COMBINEDAPACHELOG}` expands to the full nginx pattern shown above.

---

## 5. Code Editors — Syntax Highlighting with Tries

A code editor needs to identify keywords (`def`, `class`, `return`, `if`, `for`, ...)
and highlight them. Checking every token against a list of 50+ keywords naively is O(k)
per token. A trie gives O(m) per token where m is the token length, regardless of keyword count.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_keyword = False
        self.keyword = None

class KeywordTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, keyword: str):
        node = self.root
        for ch in keyword:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_keyword = True
        node.keyword = keyword

    def is_keyword(self, token: str) -> bool:
        node = self.root
        for ch in token:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_keyword

    def highlight(self, code: str) -> list:
        """Tokenize and identify keywords. Returns list of (token, is_keyword)."""
        tokens = []
        current = ""
        for ch in code + " ":
            if ch.isalnum() or ch == "_":
                current += ch
            else:
                if current:
                    tokens.append((current, self.is_keyword(current)))
                    current = ""
                if ch.strip():
                    tokens.append((ch, False))
        return tokens

python_keywords = ["def", "class", "return", "if", "else", "for", "while",
                   "import", "from", "in", "not", "and", "or", "True", "False"]
trie = KeywordTrie()
for kw in python_keywords:
    trie.insert(kw)

code = "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"
tokens = trie.highlight(code)
for token, is_kw in tokens:
    if is_kw:
        print(f"[KEYWORD] {token}")
    else:
        print(f"          {token}")
```

VS Code's TextMate grammar engine, tree-sitter (used by Neovim), and CodeMirror
all use automata-based approaches to scan source files for syntax highlighting.
Tree-sitter builds an actual parse tree, but the lexer phase is trie/DFA-based.

---

## 6. Spam Filters — N-gram String Features

Spam classifiers (like Gmail's) extract features from email text.
N-grams (contiguous sequences of n words or characters) are among the most powerful features.
Bigram "buy now" appearing in an email is a strong spam signal.

```python
from collections import Counter

def extract_ngrams(text: str, n: int) -> list:
    """Extract character n-grams from text."""
    text = text.lower()
    return [text[i:i+n] for i in range(len(text) - n + 1)]

def extract_word_ngrams(text: str, n: int) -> list:
    """Extract word n-grams from text."""
    words = text.lower().split()
    return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]

spam_email = "CONGRATULATIONS! You have WON a FREE iPhone. Click here to CLAIM now!"
ham_email  = "Hi Sarah, the meeting is rescheduled to 3pm tomorrow. Let me know if that works."

# Character 3-grams — language-model features
spam_trigrams = Counter(extract_ngrams(spam_email, 3))
ham_trigrams  = Counter(extract_ngrams(ham_email, 3))

# Word bigrams — phrase-level features
spam_bigrams = Counter(extract_word_ngrams(spam_email, 2))
ham_bigrams  = Counter(extract_word_ngrams(ham_email, 2))

print("Top spam bigrams:", spam_bigrams.most_common(3))
print("Top ham bigrams:",  ham_bigrams.most_common(3))

# Naive Bayes classifier using n-gram features
class NgramSpamFilter:
    def __init__(self, n=2):
        self.n = n
        self.spam_freq = Counter()
        self.ham_freq  = Counter()
        self.spam_total = 0
        self.ham_total  = 0

    def train(self, text: str, label: str):
        grams = extract_word_ngrams(text, self.n)
        if label == "spam":
            self.spam_freq.update(grams)
            self.spam_total += len(grams)
        else:
            self.ham_freq.update(grams)
            self.ham_total += len(grams)

    def predict(self, text: str) -> str:
        grams = extract_word_ngrams(text, self.n)
        spam_score = sum(self.spam_freq.get(g, 1) / (self.spam_total + 1) for g in grams)
        ham_score  = sum(self.ham_freq.get(g, 1)  / (self.ham_total + 1)  for g in grams)
        return "spam" if spam_score > ham_score else "ham"

clf = NgramSpamFilter(n=2)
clf.train(spam_email, "spam")
clf.train(ham_email, "ham")
clf.train("Win a free vacation now click here", "spam")
clf.train("Can you review the pull request I sent?", "ham")

print(clf.predict("You WON a free iPhone click to claim"))  # spam
print(clf.predict("The code review is scheduled for 2pm"))  # ham
```

Gmail's spam filter uses neural networks today, but n-gram features remain part of the
feature engineering pipeline. SpamAssassin (open-source) still uses n-gram rules.

---

## 7. URL Parsing and Routing — Pattern Matching in Web Frameworks

Every web framework (Flask, Django, FastAPI, Express) routes incoming URLs to handler functions.
URL routing is a string pattern matching problem.

Flask uses Werkzeug's routing system which compiles URL rules into a regex automaton.
FastAPI uses the Starlette router which matches path parameters with regex groups.

```python
import re
from typing import Callable

class Router:
    """Simplified URL router — similar to Flask/Express internals."""

    def __init__(self):
        self.routes = []  # list of (compiled_regex, param_names, handler)

    def add_route(self, pattern: str, handler: Callable):
        """Register a URL pattern. :param syntax converted to named groups."""
        # Convert /users/:id/posts/:post_id to regex
        param_pattern = re.sub(r':(\w+)', r'(?P<\1>[^/]+)', pattern)
        regex = re.compile(f'^{param_pattern}$')
        self.routes.append((regex, handler))

    def dispatch(self, path: str):
        """Find handler for incoming request path. O(k) where k = route count."""
        for regex, handler in self.routes:
            match = regex.match(path)
            if match:
                return handler, match.groupdict()  # params extracted
        return None, {}

def get_user(params): return f"User {params['id']}"
def get_post(params): return f"Post {params['post_id']} of user {params['user_id']}"
def list_products(params): return "Product list"

router = Router()
router.add_route("/users/:id", get_user)
router.add_route("/users/:user_id/posts/:post_id", get_post)
router.add_route("/products", list_products)

handler, params = router.dispatch("/users/42")
print(handler(params))  # User 42

handler, params = router.dispatch("/users/7/posts/99")
print(handler(params))  # Post 99 of user 7

handler, params = router.dispatch("/products")
print(handler(params))  # Product list

# URL parsing — splits a URL string into components
from urllib.parse import urlparse, parse_qs

url = "https://api.example.com/v1/search?q=python+strings&page=2&limit=10"
parsed = urlparse(url)
print(f"Scheme: {parsed.scheme}")    # https
print(f"Host:   {parsed.netloc}")    # api.example.com
print(f"Path:   {parsed.path}")      # /v1/search
params = parse_qs(parsed.query)
print(f"Params: {params}")           # {'q': ['python strings'], 'page': ['2'], ...}
```

At scale, Nginx uses a radix tree (compressed trie) for O(m) URL routing
where m is the URL length — more efficient than iterating all regex patterns.
Envoy proxy uses the same approach for its route matching.

---

## Summary

| Use Case | String Algorithm | Complexity |
|---|---|---|
| Search engine indexing | Inverted index + tokenization | O(1) query after O(n) build |
| Multi-pattern search | Aho-Corasick automaton | O(n + m + z) one pass |
| Log scanning | KMP, regex | O(n + m) per pattern |
| DNA alignment | Smith-Waterman DP | O(nm) local alignment |
| DPI / firewalls | Aho-Corasick signatures | O(n) per packet |
| Syntax highlighting | Trie-based keyword matching | O(m) per token |
| Spam filtering | N-gram feature extraction | O(n) per document |
| URL routing | Regex / radix trie | O(m) per request |

String algorithms are not just competitive programming tricks.
They are the core of search, security, bioinformatics, and web infrastructure.

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Common Mistakes →](./common_mistakes.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheatsheet.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
