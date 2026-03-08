# Strings — Cheatsheet

## String Operations Complexity

```
+-------------------------------+----------+----------+----------------------------+
| Operation                     | Time     | Space    | Note                       |
+-------------------------------+----------+----------+----------------------------+
| Access s[i]                   | O(1)     | O(1)     |                            |
| Length len(s)                 | O(1)     | O(1)     | stored attribute           |
| Concatenation s + t           | O(n+m)   | O(n+m)   | creates NEW string         |
| Slice s[i:j]                  | O(k)     | O(k)     | k = j-i, NEW string        |
| s in t (substring search)     | O(n*m)   | O(1)     | CPython uses fast heuristic |
| s.find(t)                     | O(n*m)   | O(1)     | -1 if not found            |
| s.replace(old, new)           | O(n)     | O(n)     | new string                 |
| s.split(sep)                  | O(n)     | O(n)     | list of substrings         |
| ''.join(lst)                  | O(n)     | O(n)     | preferred way to build str |
| s.count(sub)                  | O(n*m)   | O(1)     | non-overlapping            |
| s.strip()                     | O(n)     | O(n)     |                            |
| s.lower() / s.upper()         | O(n)     | O(n)     |                            |
| s == t (compare)              | O(n)     | O(1)     |                            |
| s.startswith(prefix)          | O(m)     | O(1)     | m = len(prefix)            |
+-------------------------------+----------+----------+----------------------------+
```

---

## String Immutability — The Core Rule

```
Python strings are IMMUTABLE. You cannot modify a character in place.

WRONG (TypeError):
    s[0] = 'X'

CORRECT pattern — convert to list, modify, rejoin:
    chars = list(s)         # O(n) time + space
    chars[0] = 'X'
    result = ''.join(chars) # O(n)

String concatenation in a loop is O(n^2) TOTAL:
    WRONG:
        result = ""
        for c in s:
            result += c     # new string created each iteration => O(n^2)

    CORRECT:
        parts = []
        for c in s:
            parts.append(c)
        result = ''.join(parts)  # O(n)
```

---

## Python String Methods Quick Reference

```python
s = "  Hello, World!  "

# Case
s.lower()           # "  hello, world!  "
s.upper()           # "  HELLO, WORLD!  "
s.title()           # "  Hello, World!  "
s.swapcase()        # "  hELLO, wORLD!  "

# Strip / pad
s.strip()           # "Hello, World!"
s.lstrip()          # "Hello, World!  "
s.rstrip()          # "  Hello, World!"
"hi".ljust(10, '-') # "hi--------"
"hi".rjust(10, '-') # "--------hi"
"hi".center(10)     # "    hi    "
"5".zfill(3)        # "005"

# Search
s.find("World")     # index of first occurrence, -1 if missing
s.rfind("l")        # rightmost occurrence
s.index("World")    # like find but raises ValueError if missing
s.count("l")        # count non-overlapping occurrences
s.startswith("  H") # True
s.endswith("!  ")   # True

# Modify
s.replace("World", "Python")  # new string
",".join(["a","b","c"])        # "a,b,c"
"a,b,c".split(",")             # ["a","b","c"]
"  hi  ".split()               # ["hi"] — splits on any whitespace

# Check type
"abc".isalpha()     # True — only letters
"123".isdigit()     # True — only digits
"abc123".isalnum()  # True — letters or digits
"   ".isspace()     # True
"Hello".istitle()   # True

# Format
f"Hello {name}"          # f-string (preferred)
"Hello {}".format(name)  # .format()
"%s %d" % (name, age)    # % formatting (legacy)
```

---

## Character Arithmetic — ord() / chr()

```python
ord('a')    # 97
ord('A')    # 65
ord('z')    # 122
chr(97)     # 'a'

# Map lowercase letter to 0-25 index:
idx = ord(c) - ord('a')     # 'a'->0, 'b'->1, ... 'z'->25

# Check if char is lowercase letter:
'a' <= c <= 'z'             # or c.islower()

# Frequency array for lowercase letters:
freq = [0] * 26
for c in s:
    freq[ord(c) - ord('a')] += 1
```

---

## Pattern 1 — Palindrome Check

```python
# Simple: two pointers — O(n) time, O(1) space
def is_palindrome(s):
    lo, hi = 0, len(s) - 1
    while lo < hi:
        if s[lo] != s[hi]:
            return False
        lo += 1
        hi -= 1
    return True

# One-liner (creates copy):
def is_palindrome(s):
    return s == s[::-1]

# Alphanumeric only (interview variant):
def is_palindrome_alnum(s):
    filtered = [c.lower() for c in s if c.isalnum()]
    return filtered == filtered[::-1]
```

---

## Pattern 2 — Anagram Check

```python
from collections import Counter

# Two strings are anagrams iff sorted chars are equal
def is_anagram(s, t):
    return Counter(s) == Counter(t)  # O(n)

# Without Counter:
def is_anagram_manual(s, t):
    if len(s) != len(t): return False
    freq = [0] * 26
    for a, b in zip(s, t):
        freq[ord(a) - ord('a')] += 1
        freq[ord(b) - ord('a')] -= 1
    return all(f == 0 for f in freq)

# Group anagrams (sort key trick):
from collections import defaultdict
def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        groups[tuple(sorted(w))].append(w)  # sorted string as key
    return list(groups.values())
```

---

## Pattern 3 — Sliding Window on Strings

```python
# Template: minimum window substring containing all chars of t
from collections import Counter

def min_window(s, t):
    need = Counter(t)
    missing = len(t)        # total chars still needed
    lo = 0
    best = ""

    for hi, c in enumerate(s):
        if need[c] > 0:
            missing -= 1
        need[c] -= 1

        while missing == 0:         # valid window, try to shrink
            window = s[lo:hi+1]
            if not best or len(window) < len(best):
                best = window
            if need[s[lo]] == 0:    # removing this char makes window invalid
                missing += 1
            need[s[lo]] += 1
            lo += 1
    return best

# Longest substring without repeating chars:
def length_of_longest_substring(s):
    seen = {}
    lo = 0
    best = 0
    for hi, c in enumerate(s):
        if c in seen and seen[c] >= lo:
            lo = seen[c] + 1        # jump left pointer past duplicate
        seen[c] = hi
        best = max(best, hi - lo + 1)
    return best
```

---

## Pattern 4 — String Matching Overview

```
+----------------+-----------+---------+--------------------------------------+
| Algorithm      | Time      | Space   | When to use                          |
+----------------+-----------+---------+--------------------------------------+
| Naive / Brute  | O(n*m)    | O(1)    | short strings, simple cases          |
| KMP            | O(n+m)    | O(m)    | single pattern search, no hash       |
| Rabin-Karp     | O(n+m)*   | O(1)    | multiple patterns, rolling hash      |
| Python 'in'    | O(n)* avg | O(1)    | good enough for interviews           |
+----------------+-----------+---------+--------------------------------------+

KMP key idea:
  - Build failure function (prefix = suffix table) for pattern — O(m)
  - Use it to avoid re-scanning already matched characters — O(n)

Rabin-Karp key idea:
  - Hash pattern; use rolling hash on text windows — O(n) average
  - Handle hash collisions with explicit string comparison
```

---

## KMP Failure Function Template

```python
def kmp_search(text, pattern):
    def build_lps(pat):                 # longest proper prefix = suffix
        lps = [0] * len(pat)
        length = 0
        i = 1
        while i < len(pat):
            if pat[i] == pat[length]:
                length += 1
                lps[i] = length
                i += 1
            elif length:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
        return lps

    lps = build_lps(pattern)
    matches = []
    j = 0                               # index in pattern
    for i, c in enumerate(text):        # index in text
        while j and c != pattern[j]:
            j = lps[j - 1]
        if c == pattern[j]:
            j += 1
        if j == len(pattern):
            matches.append(i - j + 1)
            j = lps[j - 1]
    return matches
```

---

## Common String Interview Patterns

```
+-----------------------------------+------------------------------------------+
| Problem type                      | Pattern                                  |
+-----------------------------------+------------------------------------------+
| Is palindrome                     | Two pointers                             |
| Is anagram                        | Counter / freq array                     |
| Longest substring no repeat       | Sliding window + set/dict                |
| Minimum window substring          | Sliding window + Counter                 |
| Group anagrams                    | Sort-key hash map                        |
| String to integer (atoi)          | Strip, sign, digit loop                  |
| Valid parentheses                 | Stack                                    |
| Longest common prefix             | Vertical scan or sort + compare ends     |
| Encode / decode strings           | Length-prefix encoding                   |
| Word break                        | DP with set of words                     |
| Pattern match (regex-like)        | DFS / DP                                 |
+-----------------------------------+------------------------------------------+
```

---

## Gotchas / Traps

```
1. Strings are immutable — s[i] = 'x' raises TypeError
2. s += c in a loop is O(n^2) total — use list + join
3. s.split() with no arg splits on ANY whitespace and removes empty strings
   s.split(' ') keeps empty strings between consecutive spaces
4. s.find() returns -1 on miss; s.index() raises ValueError — know which you want
5. Comparing strings: 'a' < 'b' is True (lexicographic by Unicode code point)
   'Z' < 'a' is True because ord('Z')=90, ord('a')=97
6. ord('0')=48, ord('9')=57 — digit to int: int(c) or ord(c)-ord('0')
7. f-string expressions evaluated at runtime — safe for quick formatting
8. String slicing s[i:j] never raises IndexError even with out-of-bounds indices
```

---

## When To Use Strings vs Other Structures

```
Keep as string  — read-only operations, comparisons, hashing (dict key)
Convert to list — any in-place character modification needed
Use Counter     — frequency counting, anagram checks
Use set(s)      — unique characters in O(n) time and space
Use deque       — if building string char-by-char with both-end operations
```
