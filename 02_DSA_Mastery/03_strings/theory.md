<a id="top"></a>
# 📘 03 – Strings in Python

## 📖 Table of Contents

- [📌 Learning Priority](#learning-priority)
- [1. What Is a String?](#1-what-is-a-string)
  - [String as an Array of Characters](#string-as-array)
  - [Visual: The Telegraph Tape](#visual-telegraph-tape)
- [2. Immutability — The Defining Feature](#2-immutability)
  - [Visual: Carved in Stone](#visual-carved-in-stone)
  - [What Happens When You "Modify" a String](#what-happens-modify)
- [3. Time Complexity of String Operations](#3-time-complexity)
  - [The Concatenation Trap](#concatenation-trap)
- [4. Common String Operations](#4-common-operations)
  - [Slicing](#slicing)
  - [Visual: The Window on the Tape](#visual-window-tape)
  - [Reverse](#reverse)
  - [Split](#split)
  - [Replace](#replace)
- [5. String Internals](#5-string-internals)
  - [Interning](#interning)
  - [Memory Representation](#memory-representation)
- [6. String Comparison](#6-string-comparison)
  - [Visual: Lexicographic Order](#visual-lexicographic)
  - [The ASCII Trap](#ascii-trap)
  - [String vs List of Characters](#string-vs-list)
- [7. Interview Patterns](#7-interview-patterns)
  - [Anagram Detection](#anagram-detection)
  - [Sliding Window — Longest No-Repeat Substring](#sliding-window)
  - [Palindrome Checking](#palindrome-checking)
  - [Substring Search and KMP](#substring-search-kmp)
- [8. Space Complexity and When to Avoid Strings](#8-space-complexity)
- [9. Real-World Impact](#9-real-world-impact)
  - [Full-Text Search Engines](#full-text-search)
  - [Log Parsing](#log-parsing)
  - [URL Parsing and Routing](#url-routing)
- [🔥 Summary](#summary)

<a id="learning-priority"></a>
## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
string immutability · indexing and slicing · concatenation pitfall (O(n²)) · two-pointer patterns

**Should Learn** — Important for real projects, comes up regularly:
string interning · character encoding · split/reverse/replace operations

**Good to Know** — Useful in specific situations, not always tested:
palindrome checking patterns · basic substring search

**Reference** — Know it exists, look up syntax when needed:
KMP algorithm · rolling hash · Rabin-Karp · suffix arrays

Kai works at an intelligence agency, decoding intercepted messages. Every message is a sequence of characters — letters, digits, symbols — laid out in a precise order on a long tape. His job is to search for patterns, compare fragments, rearrange pieces, and detect hidden repetitions. But there is one rule that governs everything he does: once a message is printed on the tape, it cannot be changed. If Kai needs a different version, he must print an entirely new tape. That single constraint — **immutability** — shapes every technique he will learn today.

<a id="1-what-is-a-string"></a>
# 1. What Is a String?

Kai receives his first message: `"hello"`. It arrives on a strip of tape, each character in its own slot, numbered from left to right starting at zero. That strip — an ordered, indexed sequence of characters — is a string.

An **array** stores elements by position. A **string** is an array of characters. Everything Kai learned about arrays applies here, with one critical twist: the tape is read-only.

Important characteristics:
- Ordered
- Indexed (O(1) access)
- Immutable (cannot be changed after creation)
- Iterable

That one word — **immutable** — defines most of its behavior.

<a id="string-as-array"></a>
## String as an Array of Characters

```
Index:   0   1   2   3   4
Value:   h   e   l   l   o
```

```python
s = "hello"
s[0]   # 'h' — O(1), same as array indexing
s[2]   # 'l'
```

Under the hood, `"hello"` is `[104, 101, 108, 108, 111]` — just integers. Python's `ord('h')` returns 104. `chr(104)` returns `'h'`.

**Common mistake — ord/chr base confusion:** Subtract `ord('a')` for lowercase and `ord('A')` for uppercase. They are different: `ord('a') = 97`, `ord('A') = 65`. Using the wrong base gives an `IndexError` in a frequency array.

```python
# WRONG: forgetting which base
idx = ord('h') - ord('A')   # 104 - 65 = 39 → IndexError on [0]*26

# RIGHT: match the case
idx = ord('h') - ord('a')   # 104 - 97 = 7 → correct
```

<a id="visual-telegraph-tape"></a>
## Visual: The Telegraph Tape

In the early days of communication, messages were encoded as sequences of dots and dashes on a long paper tape. Each character had its position. The tape was read left to right, character by character.

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

> 📝 **Practice:** [Q1 · string-immutability-explain](./practice.md#q1--string-immutability-explain----why-cant-you-modify-s0-)

> [↑ Back to Top](#top)

<a id="2-immutability"></a>
# 2. Immutability — The Defining Feature

Kai tries to fix a typo in a decoded message — he wants to change the first letter. But the tape is carved in stone. He cannot erase a character and write a new one. He must carve an entirely new stone tablet with the corrected message.

In Python, once a string is created, it cannot be modified.

```python
s = "hello"
s[0] = "H"   # TypeError: 'str' object does not support item assignment
```

Why immutability?
1. Memory safety
2. Hashing stability (strings can be dictionary keys because they never change)
3. Thread safety
4. Performance optimization (string interning)

<a id="visual-carved-in-stone"></a>
## Visual: Carved in Stone

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

**Common mistake — forgetting strings are immutable:** Trying `s[0] = 'H'` raises a `TypeError`. The fix is to convert to a list, modify, then join back: `chars = list(s); chars[0] = 'H'; s = ''.join(chars)`.

<a id="what-happens-modify"></a>
## What Happens When You "Modify" a String

When Kai writes `s = s + " world"`, he does NOT modify the original tape. He prints a brand new tape with the combined content and throws away the old one.

```python
s = "hello"
s = s + " world"
```

Python:
1. Creates a new string object `"hello world"`
2. Copies old content `"hello"` into it
3. Appends `" world"`
4. Reassigns `s` to point to the new object

```
Before:
  s ──→ "hello"

After s = s + " world":
  s ──→ "hello world"   (new object in memory)
         "hello"         (old object, unreferenced, garbage collected)
```

> 📝 **Practice:** [Q1 · string-immutability-explain](./practice.md#q1--string-immutability-explain----why-cant-you-modify-s0-)

> [↑ Back to Top](#top)

<a id="3-time-complexity"></a>
# 3. Time Complexity of String Operations

Kai needs to know how expensive each operation is on his message tapes. Some operations are instant — checking tape length. Others are deceptively expensive — what looks like a small edit actually copies the entire tape.

| Operation | Complexity | Why |
|------------|------------|-----|
| Indexing `s[i]` | O(1) | Direct address jump |
| Length `len(s)` | O(1) | Python stores length |
| Slicing `s[i:j]` | O(k) | Creates new string of length k |
| Concatenation `s + t` | O(n + m) | Creates new string |
| `in` operator | O(n) | Scans sequentially |
| Iteration | O(n) | Visits each character |

Important insight: slicing creates a new string → O(k), not O(1).

<a id="concatenation-trap"></a>
## The Concatenation Trap

Kai decodes a message one character at a time. He tries taping each new character onto the end of his growing message. But because the tape is immutable, he actually copies the entire message so far and creates a new tape — every single time.

```python
# WRONG — O(n²)
result = ""
for char in data:
    result += char   # copies entire result each time

# RIGHT — O(n)
result = []
for char in data:
    result.append(char)
final = "".join(result)
```

```
Building "hello" character by character:

Iteration 1: result = "" + "h"     (copied 0 chars, wrote 1)
Iteration 2: result = "h" + "e"    (copied 1 char,  wrote 1)
Iteration 3: result = "he" + "l"   (copied 2 chars, wrote 1)
Iteration 4: result = "hel" + "l"  (copied 3 chars, wrote 1)
Iteration 5: result = "hell" + "o" (copied 4 chars, wrote 1)

Total characters written: 0+1+2+3+4 + 5 = 15 for a 5-char string.
For length n: n*(n+1)/2 = O(n²)
```

The `''.join(iterable)` pattern allocates one final string in O(n). Collect parts into a list, join once at the end.

**Common mistake — concatenating strings in a loop:** For n=50,000 characters, `''.join()` is roughly **700x faster** than `+=` in a loop.

> 📝 **Practice:** [Q2 · build-string-join-vs-concat](./practice.md#q2--build-string-join-vs-concat----build-a-string-from-a-list-of-chars-)

> [↑ Back to Top](#top)

<a id="4-common-operations"></a>
# 4. Common String Operations

Kai's daily toolkit — the operations he reaches for on every message. Each one creates a new tape (because immutability), so understanding the cost matters.

<a id="slicing"></a>
## Slicing

```python
s = "programming"
s[3:7]   # "gram" — creates a new string, O(k)
```

<a id="visual-window-tape"></a>
## Visual: The Window on the Tape

Kai places a magnifying window over a portion of his tape — he can read just that section.

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
Slicing creates a new string in O(k) time where k is the slice length.

<a id="reverse"></a>
## Reverse

```python
s[::-1]   # creates new reversed string, O(n)
```

> 📝 **Practice:** [Q3 · reverse-string](./practice.md#q3--reverse-string----reverse-a-string-in-place-no-extra-string-)

<a id="split"></a>
## Split

```python
s.split(" ")   # returns list of substrings, O(n)
```

**Common mistake — split() vs split(' '):** `split()` with no argument is the smart scissors — it collapses any whitespace and never produces empty strings. `split(' ')` is the dumb scissors — it cuts at every single space, producing empty strings for consecutive spaces.

```python
s = "  hello   world  "

# WRONG for word counting:
s.split(' ')   # ['', '', 'hello', '', '', 'world', '', '']

# RIGHT:
s.split()      # ['hello', 'world']
```

Use `split(delimiter)` only when you need a specific separator and want to preserve empty fields (e.g., CSV parsing).

> 📝 **Practice:** [Q6 · split-join-strip](./practice.md#q6--split-join-strip----know-your-string-methods-)

<a id="replace"></a>
## Replace

```python
s.replace("a", "b")   # creates new string, O(n)
```

All these operations return new strings — the original is never touched.

> [↑ Back to Top](#top)

<a id="5-string-internals"></a>
# 5. String Internals

Kai notices something strange — two copies of the same decoded message share the exact same memory address. His agency is saving resources by keeping only one copy of frequently used phrases. Python does the same thing.

<a id="interning"></a>
## Interning

Python optimizes small strings by reusing them. If two variables hold the same short string, they may point to the exact same object in memory.

```python
a = "hello"
b = "hello"
print(a is b)   # True — same object (interned)

a = "hello world!!"
b = "hello world!!"
print(a is b)   # False — not interned (contains special chars)
```

This is called **string interning**. It improves memory efficiency and comparison speed (identity check `is` is O(1) vs value check `==` which is O(n)).

But never rely on interning in your logic — it is a CPython implementation detail, not a language guarantee.

<a id="memory-representation"></a>
## Memory Representation

Kai's tapes are not simple byte arrays. Each character can be 1, 2, or 4 bytes depending on the character set — Python handles this transparently.

Strings in Python are Unicode (UTF-8 internally in CPython 3.12+). Unlike C, strings are not null-terminated arrays.

Python stores:
- **Length** — retrieval is O(1)
- **Hash** — cached after first computation, makes dict lookups O(1)
- **Character data** — contiguous, encoding depends on widest character

```
Python string object layout:

┌────────────────────────────────┐
│  ob_refcnt    (reference count)│
│  ob_type      (str type)       │
│  ob_size      (length)         │
│  hash         (cached hash)    │
│  state        (encoding flags) │
│  data[]       (character bytes)│
└────────────────────────────────┘
```

> [↑ Back to Top](#top)

<a id="6-string-comparison"></a>
# 6. String Comparison

Kai needs to determine which of two intercepted messages comes first in alphabetical order. He compares them character by character, left to right — the moment he finds a difference, he has his answer.

```python
"abc" == "abc"   # True — O(n) worst case, stops early on mismatch
```

<a id="visual-lexicographic"></a>
## Visual: Lexicographic Order

"Lexicographic" is just a fancy word for "dictionary order."

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

<a id="ascii-trap"></a>
## The ASCII Trap

Kai discovers that uppercase and lowercase letters live in completely different neighborhoods on the ASCII chart.

```
'Z' = 90
'a' = 97

So 'Z' < 'a' in ASCII!
"Zebra" < "apple" in Python string comparison.

>>> "Zebra" < "apple"
True
```

Use `.lower()` when you want case-insensitive comparison.

**Common mistake — case sensitivity in comparisons:** `'P'` (ASCII 80) is not equal to `'p'` (ASCII 112). Forgetting `.lower()` before comparison silently misses matches. Always normalize: `s1.lower() == s2.lower()`.

**Common mistake — string comparison is lexicographic not numeric:** `sorted(["10", "9", "2"])` gives `['10', '2', '9']` because `'1' < '2' < '9'` by ASCII value.

```python
# WRONG:
sorted(["10", "9", "2"])          # ['10', '2', '9']

# RIGHT:
sorted(["10", "9", "2"], key=int) # ['2', '9', '10']
```

<a id="string-vs-list"></a>
## String vs List of Characters

Kai sometimes needs to modify individual characters. Since strings are immutable, he converts to a list, modifies, then joins back.

| Feature | String | List of Characters |
|----------|---------|------------------|
| Mutable | No | Yes |
| Indexing | O(1) | O(1) |
| Concatenation | Expensive (new object) | Cheap (append) |
| Memory | Efficient | Slightly more |

```python
s = "hello"
chars = list(s)      # ['h', 'e', 'l', 'l', 'o']
chars[0] = 'H'       # modify freely
s = ''.join(chars)   # "Hello"
```

If frequent modifications are needed, convert to list first.

> [↑ Back to Top](#top)

<a id="7-interview-patterns"></a>
# 7. Interview Patterns

Kai has decoded enough messages to recognize recurring patterns. Most string problems in interviews fall into a handful of categories — recognizing the pattern is half the battle.

Key patterns:
1. Two pointers
2. Sliding window
3. Frequency counting (hashing)
4. Palindrome checking
5. Substring search
6. Anagram detection
7. Prefix/suffix comparison

> 📝 **Practice:** [Q9 · palindrome-two-pointer](./practice.md#q9--palindrome-two-pointer----check-if-a-string-is-a-palindrome-) · [Q11 · anagram-detection-counter](./practice.md#q11--anagram-detection-counter----are-two-strings-anagrams-) · [Q14 · longest-no-repeat-substring](./practice.md#q14--longest-no-repeat-substring----sliding-window-no-repeats-)

<a id="anagram-detection"></a>
## Anagram Detection

Kai intercepts two messages and needs to check if they use the exact same characters — just rearranged. "listen" and "silent" are anagrams. "hello" and "world" are not.

## Visual: Two Strategies

**Strategy 1 — Sort and Compare:**

If two strings are anagrams, sorting them gives identical results.

```
"listen" → sorted → "eilnst"
"silent" → sorted → "eilnst"
"eilnst" == "eilnst" → True!
```

Time: O(n log n) for sorting. Simple, clean.

**Strategy 2 — Frequency Map:**

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

Time: O(n). Faster than sorting.

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

<a id="sliding-window"></a>
## Sliding Window — Longest No-Repeat Substring

Kai scans a long intercepted message looking for the longest stretch of unique characters. He uses a sliding magnifying glass — expanding right as long as all characters inside are unique, shrinking from the left when a repeat is detected.

Problem: find the longest substring without repeating characters.
Input: `"abcabcbb"`. Answer: `"abc"` (length 3).

## Visual: Sliding Window

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
    Window = "bca". max_len still 3.
     a [b c a] b c b b
       ^    ^
    left=1, right=3

Step 6: Try to add 'b'. 'b' is in window at index 1!
    Shrink: remove 'b' → left=2. Window = "cab". max_len still 3.
     a b [c a b] c b b
         ^    ^
    left=2, right=4

Step 7: Try to add 'c'. 'c' is in window at index 2!
    Shrink: remove 'c' → left=3. Window = "abc". max_len still 3.
     a b c [a b c] b b
           ^    ^
    left=3, right=5

Step 8-9: Continue shrinking for repeated 'b'. max_len stays 3.

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

**Common mistake — sliding window missing update after shrink:** When the left pointer moves right and removes a character, you must update the validity counter. Forgetting this means the loop keeps thinking the window satisfies all requirements even after it no longer does.

```python
# When shrinking, always update validity:
left_char = s[left]
window[left_char] -= 1
left += 1
if left_char in need and window[left_char] < need[left_char]:
    have -= 1   # ← this line is the critical update
```

> 📝 **Practice:** [Q14 · longest-no-repeat-substring](./practice.md#q14--longest-no-repeat-substring----sliding-window-no-repeats-)

<a id="palindrome-checking"></a>
## Palindrome Checking

Kai receives a message that reads the same forwards and backwards — a palindrome. The most efficient check uses two pointers moving inward from both ends.

```python
left = 0
right = len(s) - 1
# Move inward, comparing characters — O(n) time, O(1) space
```

## Visual: The Mirror Check

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

## Expand Around Center — Longest Palindromic Substring

For each character, treat it as the center and expand outward.

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

Longest: "bab" or "aba", both length 3.
```

**Common mistake — palindrome check with non-alphanumeric:** Most palindrome problems require filtering out spaces and punctuation first.

```python
# WRONG:
s == s[::-1]   # fails on "A man, a plan, a canal: Panama"

# RIGHT:
cleaned = ''.join(c.lower() for c in s if c.isalnum())
return cleaned == cleaned[::-1]
```

> 📝 **Practice:** [Q9 · palindrome-two-pointer](./practice.md#q9--palindrome-two-pointer----check-if-a-string-is-a-palindrome-) · [Q10 · palindrome-with-nonalnum](./practice.md#q10--palindrome-with-nonalnum----valid-palindrome-ignoring-punctuation-)
> 📝 **Practice:** [Q8 · palindrome-check](../dsa_practice_questions_100.md#q8--thinking--palindrome-check)

<a id="substring-search-kmp"></a>
## Substring Search and KMP

Kai needs to find every occurrence of a code word inside a long intercepted message. The naive approach — checking every position — is O(nm). The KMP algorithm does it in O(n + m) by using the pattern itself to skip unnecessary comparisons.

Basic method: Linear scan → O(nm)

Optimized algorithms:
- KMP → O(n + m)
- Rabin-Karp (rolling hash)
- Boyer-Moore

## Visual: KMP Failure Function

When a mismatch occurs, the pattern itself tells you how far to jump back. This information is encoded in the **failure function** (prefix function).

## Building the Failure Array

For each position in the pattern, ask: "What is the longest proper prefix of this substring that is also a suffix?"

```
Pattern: A B A B C
Index:   0 1 2 3 4

f[0] = 0  (no proper prefix/suffix for single character)

f[1]: "AB"  → prefix "A", suffix "B" → no match → f[1] = 0

f[2]: "ABA" → prefix "A", suffix "A" → match! length 1 → f[2] = 1
  A B A
  ↑     ↑
  prefix  suffix both = "A"

f[3]: "ABAB" → prefix "AB", suffix "AB" → match! length 2 → f[3] = 2
  A B A B
  ↑ ↑   ↑ ↑
  prefix   suffix both = "AB"

f[4]: "ABABC" → no prefix-suffix overlap → f[4] = 0

Failure array: [0, 0, 1, 2, 0]
```

## Search Trace on "ABABDABABC"

```
Text:    A B A B D A B A B C
Pattern: A B A B C

Position 0: A=A, B=B, A=A, B=B, then D≠C → mismatch at index 4
With KMP: failure[3] = 2, so jump pattern back to index 2
          We already know text positions 2-3 match pattern 0-1!

Restart:         A B A B C   ← pattern shifted, not restarted
Text:    A B A B D A B A B C
                 ↑
                 D≠A, mismatch again. failure[0]=0, start fresh.

                   A B A B C
Text:    A B A B D A B A B C
                   ↑ ↑ ↑ ↑ ↑  all match!

Found at index 5!
```

```python
def build_failure(pattern):
    n = len(pattern)
    f = [0] * n
    k = 0
    for i in range(1, n):
        while k > 0 and pattern[k] != pattern[i]:
            k = f[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        f[i] = k
    return f

def kmp_search(text, pattern):
    f = build_failure(pattern)
    matches = []
    k = 0
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

**Common mistake — using `in` for substring vs character check:** `"ab" in s` checks substring, not individual characters. Also: `find()` returns `-1` when not found; `index()` raises `ValueError`.

```python
pos = s.find("xyz")    # -1 if not found — safe
pos = s.index("xyz")   # ValueError if not found — crashes
```

**Common mistake — KMP failure function off-by-one:** When a mismatch occurs during lps construction, fall back to `lps[length - 1]`, not `lps[length]`.

> 📝 **Practice:** [Q22 · kmp-lps-build](./practice.md#q22--kmp-lps-build----build-the-kmp-failure-lps-array-) · [Q23 · kmp-full-search](./practice.md#q23--kmp-full-search----full-kmp-pattern-search-)
> 📝 **Practice:** [Q9 · substring-search](../dsa_practice_questions_100.md#q9--code--substring-search) · [Q71 · kmp-string-matching](../dsa_practice_questions_100.md#q71--thinking--kmp-string-matching)

> [↑ Back to Top](#top)

<a id="8-space-complexity"></a>
# 8. Space Complexity and When to Avoid Strings

Kai realizes that every time he slices, concatenates, or reverses a tape, he is creating a brand new copy. For small messages this is fine. For a 10-million-character intercepted transmission, the copies add up fast.

A string of size n costs O(n) space. But operations silently create additional copies:

| Operation | Extra Space |
|---|---|
| Slicing `s[i:j]` | O(j-i) — new string |
| Concatenation `s + t` | O(n + m) — new string |
| Reverse `s[::-1]` | O(n) — new string |
| Recursive string problems | O(n) stack frames |

**When to avoid strings directly:**

- **Repeated concatenation in loops** — use `list.append()` + `''.join()`
- **Massive data processing** — consider byte arrays (`bytearray`) or streaming
- **Character-level mutations** — convert to `list(s)`, modify, `''.join()`
- **Binary data** — use `bytes` / `bytearray`, not `str`

> [↑ Back to Top](#top)

<a id="9-real-world-impact"></a>
# 9. Real-World Impact

Kai's string skills translate directly to production engineering. Every web request is a URL string. Every log line is a string. Every search query is a string. The patterns he learned — indexing, frequency counting, pattern matching — power the systems that run the internet.

<a id="full-text-search"></a>
## Full-Text Search Engines

Google, Elasticsearch, and Lucene do not scan every document for every query. They preprocess documents into an **inverted index**: a hash map from term to list of document IDs. At query time, a word lookup is O(1) in the index rather than O(n * m) brute force.

```python
from collections import defaultdict

def build_inverted_index(documents: list) -> dict:
    index = defaultdict(set)
    for doc_id, text in enumerate(documents):
        tokens = text.lower().split()
        for token in tokens:
            token = token.strip(".,!?")
            index[token].add(doc_id)
    return dict(index)

def search(index: dict, query: str) -> set:
    terms = query.lower().split()
    if not terms:
        return set()
    result = index.get(terms[0], set())
    for term in terms[1:]:
        result = result & index.get(term, set())
    return result

docs = [
    "Python is a high level programming language",
    "Python is used in data science and machine learning",
    "Java is a compiled programming language",
    "Data science requires statistics and programming",
]

index = build_inverted_index(docs)
print(search(index, "python programming"))   # {0}
print(search(index, "programming language")) # {0, 2}
```

Elasticsearch uses BM25 ranking on top of an inverted index. KMP is used in `grep`, `awk`, and every log analysis tool.

<a id="log-parsing"></a>
## Log Parsing

Application logs are unstructured strings. Logstash, Fluent Bit, and CloudWatch Logs Insights use regex and substring matching to extract structured fields from raw log lines.

```python
import re

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
```

<a id="url-routing"></a>
## URL Parsing and Routing

Every web framework (Flask, Django, FastAPI) routes incoming URLs to handler functions. URL routing is a string pattern matching problem.

```python
import re
from typing import Callable

class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, pattern: str, handler: Callable):
        param_pattern = re.sub(r':(\w+)', r'(?P<\1>[^/]+)', pattern)
        regex = re.compile(f'^{param_pattern}$')
        self.routes.append((regex, handler))

    def dispatch(self, path: str):
        for regex, handler in self.routes:
            match = regex.match(path)
            if match:
                return handler, match.groupdict()
        return None, {}

def get_user(params): return f"User {params['id']}"
def get_post(params): return f"Post {params['post_id']} of user {params['user_id']}"

router = Router()
router.add_route("/users/:id", get_user)
router.add_route("/users/:user_id/posts/:post_id", get_post)

handler, params = router.dispatch("/users/42")
print(handler(params))  # User 42

handler, params = router.dispatch("/users/7/posts/99")
print(handler(params))  # Post 99 of user 7
```

```python
from urllib.parse import urlparse, parse_qs

url = "https://api.example.com/v1/search?q=python+strings&page=2&limit=10"
parsed = urlparse(url)
print(f"Scheme: {parsed.scheme}")    # https
print(f"Host:   {parsed.netloc}")    # api.example.com
print(f"Path:   {parsed.path}")      # /v1/search
params = parse_qs(parsed.query)
print(f"Params: {params}")
```

At scale, Nginx uses a radix tree (compressed trie) for O(m) URL routing where m is the URL length.

> [↑ Back to Top](#top)

<a id="summary"></a>
## 🔥 Summary

```
Operation                    Time                Notes
────────────────────────────────────────────────────────────────
Length check len(s)          O(1)                Python stores length
Access s[i]                  O(1)                Direct index
Slice s[i:j]                 O(j-i)              Creates new string
Concatenation s + t          O(len(s)+len(t))    Creates new string
"".join(list of n strings)   O(total chars)      Build list, join once
Find substring (naive)       O(nm)               n=text, m=pattern
Find substring (KMP)         O(n+m)              Precompute failure array
Sort string                  O(n log n)          Convert to list, sort
Anagram check (sort)         O(n log n)
Anagram check (counter)      O(n)
Palindrome check             O(n)                Two pointers
Sliding window (no-repeat)   O(n)                Hash set / map
────────────────────────────────────────────────────────────────
```

| Concept | Key Takeaway |
|---------|-------------|
| Immutability | Every "modification" creates a new string — O(n) hidden cost |
| Concatenation trap | `+=` in loop is O(n²) — use `''.join()` |
| Two pointers | Palindromes in O(n) time, O(1) space |
| Sliding window | Substring problems that would be O(n²) become O(n) |
| Frequency maps | Anagram and character counting problems from O(n log n) to O(n) |
| KMP | Find all pattern occurrences in O(n + m) instead of O(nm) |

**Performance estimation:**
- If string length = 10⁵: O(n²) is too slow, O(n log n) acceptable, O(n) ideal
- Always check constraints before choosing approach

**Advanced topics for senior roles:**
- KMP algorithm (covered above)
- Rolling hash / Rabin-Karp
- Trie-based prefix search
- Suffix arrays
- Memory-efficient streaming parsing

> 📝 **Practice:** [Q72 · rabin-karp-hash](../dsa_practice_questions_100.md#q72--normal--rabin-karp-hash) · [Q7 · anagram-detection](../dsa_practice_questions_100.md#q7--code--anagram-detection)

# 🔁 Navigation

**[🏠 Back to README](../README.md)**

| Direction | Module |
|---|---|
| ⬅ Prev Module | [02_arrays → theory.md](../02_arrays/theory.md) |
| ➡ Next Module | [04_recursion → theory.md](../04_recursion/theory.md) |

**This folder:**
[theory.md](./theory.md) · [Practice](./practice.md) · [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md)

**Related modules:**
[02 Arrays →](../02_arrays/theory.md) · [04 Recursion →](../04_recursion/theory.md) · [10 Hashing →](../10_hashing/theory.md) · [17 Trie →](../17_trie/theory.md)

**Jump to specific topics in other files:**
- Two pointers pattern → [11_two_pointers § theory.md](../11_two_pointers/theory.md)
- Sliding window pattern → [12_sliding_window § theory.md](../12_sliding_window/theory.md)
- Hashing for frequency maps → [10_hashing § theory.md](../10_hashing/theory.md)
- Trie for prefix search → [17_trie § theory.md](../17_trie/theory.md)

> [↑ Back to Top](#top)
