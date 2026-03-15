# Strings — A Visual Story

---

## Chapter 1: The Telegraph Tape

In the early days of communication, messages were encoded as sequences of dots
and dashes on a long paper tape. Each character had its position. The tape was
read left to right, character by character.

A string is that tape.

```
"hello"

┌───┬───┬───┬───┬───┐
│ h │ e │ l │ l │ o │
└───┴───┴───┴───┴───┘
  0   1   2   3   4

Each slot holds one character.
Each character maps to a number (its ASCII / Unicode value).
```

Under the hood, `"hello"` is `[104, 101, 108, 108, 111]` — just integers.
Python's `ord('h')` returns 104. `chr(104)` returns `'h'`.

Strings are character arrays. Everything you know about arrays applies —
with one critical twist.

---

## Chapter 2: Strings Are Carved in Stone

In Python, strings are **immutable**. Once created, they cannot be changed.
The tape is set. You cannot erase a character and write a new one.

```python
s = "hello"
s[0] = 'x'   # TypeError: 'str' object does not support item assignment
```

```
Attempt to change s[0]:

"hello"
┌───┬───┬───┬───┬───┐
│ h │ e │ l │ l │ o │   ← carved in stone
└───┴───┴───┴───┴───┘
  ↑
  You cannot chisel this out.
  Python refuses. The stone breaks.
```

### What Happens When You Use `+`

```python
s = "hello"
s = s + " world"
```

You did NOT modify `"hello"`. You created a **brand new string** `"hello world"`
and pointed `s` at it. The old `"hello"` still exists in memory (until garbage collected).

```
Before:
  s ──→ "hello"

After s = s + " world":
  s ──→ "hello world"   (new object in memory)
         "hello"        (old object, now unreferenced, will be garbage collected)
```

This is why concatenation in a loop is O(n²):

```python
# SLOW: O(n²) — creates n new strings
result = ""
for word in words:
    result = result + word   # new string every iteration

# FAST: O(n) — builds list, joins once
result = "".join(words)      # one final string creation
```

---

## Chapter 3: Lexicographic Order — The Dictionary Game

"Lexicographic" is just a fancy word for "dictionary order."

When you compare two strings, Python compares them character by character,
using each character's numerical value (ASCII / Unicode).

```
Compare "apple" vs "banana":

  a  p  p  l  e
  97 112 112 108 101

  b  a  n  a  n  a
  98  97 110  97 110  97

Step 1: Compare position 0
  'a' (97) vs 'b' (98)
   97 < 98 → "apple" < "banana"

Done! We do not need to check the rest.
```

```
Compare "app" vs "apple":

  a  p  p
  a  p  p  l  e

All three characters match.
"app" runs out of characters first.
Shorter string is "less than" — "app" < "apple"
```

### The ASCII Trap

```
'Z' = 90
'a' = 97

So 'Z' < 'a' in ASCII!
"Zebra" < "apple" in Python string comparison.

>>> "Zebra" < "apple"
True
```

Use `.lower()` when you want case-insensitive comparison.

---

## Chapter 4: Substrings — The Window on the Tape

A substring is just a portion of the tape.

```
s = "programming"
      0123456789...

     p r o g r a m m i n g
     0 1 2 3 4 5 6 7 8 9 10

s[3:7] → "gram"

     p r o g r a m m i n g
           ↑       ↑
           3       7  (exclusive)

     ┌─────────────┐
     │  g  r  a  m │  ← the window s[3:7]
     └─────────────┘
```

Python slicing: `s[start:end]` — includes start, excludes end.
`s[3:7]` means "characters at indices 3, 4, 5, 6."

Slicing creates a new string in O(k) time where k is the length of the slice.

---

## Chapter 5: Anagram Detection — Two Strategies

Two words are anagrams if they use the same characters with the same frequencies.
"listen" and "silent" are anagrams. "hello" and "world" are not.

### Strategy 1: Sort and Compare

If two strings are anagrams, sorting them gives identical results.

```
"listen" → sorted → ['e', 'i', 'l', 'n', 's', 't'] → "eilnst"
"silent" → sorted → ['e', 'i', 'l', 'n', 's', 't'] → "eilnst"

"eilnst" == "eilnst" → True, they're anagrams!

"hello"  → sorted → ['e', 'h', 'l', 'l', 'o'] → "ehllo"
"world"  → sorted → ['d', 'l', 'o', 'r', 'w'] → "dlorw"

"ehllo" != "dlorw" → False, not anagrams.
```

Time: O(n log n) for sorting. Simple, clean.

### Strategy 2: Frequency Map

Build a character counter for each string. Compare the counters.

```
"listen":
┌───┬───┬───┬───┬───┬───┐
│ l │ i │ s │ t │ e │ n │
│ 1 │ 1 │ 1 │ 1 │ 1 │ 1 │
└───┴───┴───┴───┴───┴───┘

"silent":
┌───┬───┬───┬───┬───┬───┐
│ s │ i │ l │ e │ n │ t │
│ 1 │ 1 │ 1 │ 1 │ 1 │ 1 │
└───┴───┴───┴───┴───┴───┘

Both maps: {l:1, i:1, s:1, t:1, e:1, n:1}
Maps are equal → anagrams!
```

Time: O(n). Faster than sorting. Better for large strings.

```python
from collections import Counter

def is_anagram(s, t):
    return Counter(s) == Counter(t)

# Or manually:
def is_anagram_manual(s, t):
    if len(s) != len(t):
        return False
    count = {}
    for ch in s:
        count[ch] = count.get(ch, 0) + 1
    for ch in t:
        count[ch] = count.get(ch, 0) - 1
        if count[ch] < 0:
            return False
    return True
```

---

## Chapter 6: Sliding Window — Finding the Longest No-Repeat Substring

Problem: find the longest substring without repeating characters.
Input: `"abcabcbb"`. Answer: `"abc"` (length 3).

### The Window Analogy

Imagine a sliding magnifying glass over the tape.
The window expands right as long as all characters inside are unique.
When a repeat is detected, the left edge of the window slides right to remove it.

```
s = "a b c a b c b b"
     0 1 2 3 4 5 6 7

Step 1: Start with empty window. left=0, right=0.

Step 2: Add 'a'. Window = "a". No repeats. max_len=1.
    [a] b c a b c b b
     ^
    left=0, right=0

Step 3: Add 'b'. Window = "ab". No repeats. max_len=2.
    [a b] c a b c b b
     ^  ^
    left=0, right=1

Step 4: Add 'c'. Window = "abc". No repeats. max_len=3.
    [a b c] a b c b b
     ^    ^
    left=0, right=2

Step 5: Try to add 'a'. But 'a' is already in window!
    Shrink left until 'a' is removed.
    Remove 'a' at left=0 → left becomes 1.
    Window = "bc". Now add 'a': window = "bca". max_len still 3.
     a [b c a] b c b b
       ^    ^
    left=1, right=3

Step 6: Try to add 'b'. 'b' is in window at index 1!
    Shrink: remove 'b' at left=1 → left=2. Window = "ca".
    Add 'b': window = "cab". max_len still 3.
     a b [c a b] c b b
         ^    ^
    left=2, right=4

Step 7: Try to add 'c'. 'c' is in window at index 2!
    Shrink: remove 'c' → left=3. Window = "ab".
    Add 'c': window = "abc". max_len still 3.
     a b c [a b c] b b
           ^    ^
    left=3, right=5

Step 8: Try to add 'b'. 'b' in window.
    Shrink: remove 'a' → left=4. Window = "bc".
    Add 'b': but 'b' still in window!
    Shrink: remove 'b' → left=5. Window = "c".
    Add 'b': window = "cb". max_len still 3.

Step 9: Add second 'b'. 'b' in window.
    Shrink past 'b' → left=7. Window = "b". max_len still 3.

Final answer: 3 ("abc")
```

```python
def length_of_longest_substring(s):
    seen = {}         # character → last seen index
    left = 0
    max_len = 0

    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1      # jump left past the repeat
        seen[ch] = right
        max_len = max(max_len, right - left + 1)

    return max_len
```

O(n) time, O(min(n, alphabet_size)) space.

---

## Chapter 7: KMP Failure Function — When the Pattern Knows Itself

The KMP algorithm (Knuth-Morris-Pratt) is about searching for a pattern inside text efficiently.
The key idea: when a mismatch occurs, the pattern itself tells you how far to jump back.

This "how far to jump back" information is encoded in the **failure function** (also called the prefix function).

### The Partial Match Story

Before searching text, we study the pattern itself.
For each position in the pattern, we ask: "What is the longest proper prefix of this substring that is also a suffix?"

Example pattern: `"ABABC"`

```
Pattern: A B A B C
Index:   0 1 2 3 4
```

Build the failure array `f[]`:

```
f[0] = 0  (no proper prefix/suffix for single character)

Pattern so far: "A"
Prefixes: "" (empty only)
Suffixes: "" (empty only)
Longest match: 0

─────────────────────────────────────────────

f[1]: Pattern so far: "AB"
Proper prefixes: "A"
Proper suffixes: "B"
Longest match: 0  (none in common)
f[1] = 0

─────────────────────────────────────────────

f[2]: Pattern so far: "ABA"
Proper prefixes: "A", "AB"
Proper suffixes: "A", "BA"
Longest match: "A"  (length 1)
f[2] = 1

  A B A
  ↑     ↑
  prefix  suffix both = "A"

─────────────────────────────────────────────

f[3]: Pattern so far: "ABAB"
Proper prefixes: "A", "AB", "ABA"
Proper suffixes: "B", "AB", "BAB"
Longest match: "AB"  (length 2)
f[3] = 2

  A B A B
  ↑ ↑   ↑ ↑
  prefix   suffix both = "AB"

─────────────────────────────────────────────

f[4]: Pattern so far: "ABABC"
Proper prefixes: "A", "AB", "ABA", "ABAB"
Proper suffixes: "C", "BC", "ABC", "BABC"
Longest match: none (no overlap)
f[4] = 0

─────────────────────────────────────────────

Failure array: [0, 0, 1, 2, 0]

Pattern: A  B  A  B  C
         0  0  1  2  0
```

### How the Failure Array Saves Work During Search

When searching text `"ABABDABABC"` for pattern `"ABABC"`:

```
Text:    A B A B D A B A B C
Pattern: A B A B C

Position 0: A=A, B=B, A=A, B=B, then D≠C → mismatch at index 4
Without KMP: restart from position 1 in text
With KMP: failure[3] = 2, so jump pattern back to index 2
          We already know text positions 2-3 match pattern 0-1!

Restart:         A B A B C   ← pattern shifted, not restarted
Text:    A B A B D A B A B C
                 ↑
                 D≠A, mismatch again. Failure[0]=0, start fresh.

                   A B A B C
Text:    A B A B D A B A B C
                   ↑ ↑ ↑ ↑ ↑  all match!

Found at index 5!
```

```python
def build_failure(pattern):
    n = len(pattern)
    f = [0] * n
    k = 0  # length of previous longest prefix-suffix
    for i in range(1, n):
        while k > 0 and pattern[k] != pattern[i]:
            k = f[k - 1]  # fall back
        if pattern[k] == pattern[i]:
            k += 1
        f[i] = k
    return f

def kmp_search(text, pattern):
    f = build_failure(pattern)
    matches = []
    k = 0  # characters matched so far
    for i, ch in enumerate(text):
        while k > 0 and pattern[k] != ch:
            k = f[k - 1]
        if pattern[k] == ch:
            k += 1
        if k == len(pattern):
            matches.append(i - len(pattern) + 1)
            k = f[k - 1]
    return matches
```

KMP runs in O(n + m) where n = text length, m = pattern length.
The naive approach is O(nm). For large inputs, this is a massive difference.

---

## Chapter 8: Palindrome — The Mirror Check

A palindrome reads the same forwards and backwards.
"racecar", "madam", "level", "aba".

### Two-Pointer Approach

Place one pointer at the start, one at the end.
Move them toward each other. If they always agree, it is a palindrome.

```
"racecar"
 r a c e c a r
 ↑           ↑  left=0, right=6
 r == r ✓ → move inward

 r a c e c a r
   ↑       ↑    left=1, right=5
   a == a ✓ → move inward

 r a c e c a r
     ↑   ↑      left=2, right=4
     c == c ✓ → move inward

 r a c e c a r
       ↑        left=3, right=3
       left >= right → done! It's a palindrome.
```

```
"hello"
 h e l l o
 ↑       ↑  left=0, right=4
 h == o? No! → Not a palindrome.
```

```python
def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
```

O(n) time, O(1) space. Clean and direct.

### Longest Palindromic Substring — Expand Around Center

For each character, treat it as the center of a palindrome and expand outward.

```
"babad"

Center at index 1 ('a'):
  b [a] b a d
    ↑
  expand: b == b ✓ → "bab"
  expand: left out of bounds → stop
  Palindrome: "bab" (length 3)

Center at index 2 ('b'):
  b a [b] a d
      ↑
  expand: a == a ✓ → "aba"
  expand: b == d? No → stop
  Palindrome: "aba" (length 3)

Also try even-length centers (between characters):
  Between index 1 and 2: 'a' == 'b'? No.
  Between index 2 and 3: 'b' == 'a'? No.

Longest: "bab" or "aba", both length 3.
```

---

## Chapter 9: String Complexity Cheat Sheet

```
Operation                    Time          Notes
────────────────────────────────────────────────────────────────
Length check len(s)          O(1)          Python stores length
Access s[i]                  O(1)          Direct index
Slice s[i:j]                 O(j-i)        Creates new string
Concatenation s + t          O(len(s)+len(t))  Creates new string
"".join(list of n strings)   O(total chars)    Build list, join once
Find substring (naive)       O(nm)         n=text, m=pattern
Find substring (KMP)         O(n+m)        Precompute failure array
Sort string                  O(n log n)    Convert to list, sort
Anagram check (sort)         O(n log n)
Anagram check (counter)      O(n)
Palindrome check             O(n)          Two pointers
Sliding window (no-repeat)   O(n)          Hash set / map
────────────────────────────────────────────────────────────────
```

### The Key Intuitions

1. **Immutability** means operations that look O(1) might be O(n). Building strings with `+` in a loop is a classic trap.
2. **Two pointers** solve many palindrome problems in O(n) with O(1) space.
3. **Sliding window** solves substring problems that would otherwise be O(n²).
4. **Frequency maps** (Counter/dict) turn many string comparison problems from O(n log n) to O(n).
5. **KMP** is the go-to when you need to find all occurrences of a pattern quickly.

---

*Next up: Sorting — from bubble sort to TimSort, and why comparison sorting cannot be faster than O(n log n).*

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./theory.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Theory](./theory.md) · [Cheat Sheet](./cheatsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
