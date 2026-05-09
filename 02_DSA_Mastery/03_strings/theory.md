<a id="top"></a>
# 📘 Strings in Python — Complete Theory (Zero to Advanced)

> This file builds a deep understanding of strings from fundamentals
> to advanced problem-solving perspective.
>  
> Focus: memory behavior, performance implications, manipulation patterns,
> and real-world engineering usage.

## 📖 Table of Contents

1. [What Is a String?](#what-is-a-string)
2. [String as an Array of Characters](#string-as-an-array-of-characters)
3. [Why Strings Are Immutable](#why-strings-are-immutable)
4. [What Happens When You Modify a String?](#what-happens-when-you-modify-a-string)
5. [Time Complexity of String Operations](#time-complexity-of-string-operations)
6. [Why Repeated Concatenation Is Dangerous](#why-repeated-concatenation-is-dangerous)
7. [String Interning](#string-interning)
8. [Memory Representation](#memory-representation)
9. [Common String Operations](#common-string-operations)
10. [String Comparison](#string-comparison)
11. [String vs List of Characters](#string-vs-list-of-characters)
12. [Important Interview Patterns with Strings](#important-interview-patterns-with-strings)
13. [Anagram Detection](#anagram-detection)
14. [Sliding Window — Longest No-Repeat Substring](#sliding-window--longest-no-repeat-substring)
15. [Palindrome Checking](#palindrome-checking)
16. [Substring Search](#substring-search)
17. [Space Complexity Considerations](#space-complexity-considerations)
18. [When NOT To Use Strings Directly](#when-not-to-use-strings-directly)
19. [Real-World Usage of Strings](#real-world-usage-of-strings)
20. [Performance Estimation](#performance-estimation)
21. [Advanced Topics](#advanced-topics)
22. [Complexity Cheat Sheet](#complexity-cheat-sheet)
23. [Final Summary](#final-summary)

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
string immutability · indexing and slicing · concatenation pitfall (O(n²)) · two-pointer patterns

**Should Learn** — Important for real projects, comes up regularly:
string interning · character encoding · split/reverse/replace operations

**Good to Know** — Useful in specific situations, not always tested:
palindrome checking patterns · basic substring search

**Reference** — Know it exists, look up syntax when needed:
KMP algorithm · rolling hash · Rabin-Karp · suffix arrays

<a id="what-is-a-string"></a>
# 1. What Is a String?

A string is a sequence of characters.

In Python:

```python
s = "hello"
```

Internally, a string is an **ordered sequence of characters stored in memory**.

Important characteristics:

- Ordered
- Indexed
- Immutable
- Iterable

That one word — **immutable** — defines most of its behavior.

## Visual: The Telegraph Tape

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

**Common mistake — ord/chr confusion:** Subtract `ord('a')` for lowercase letters and `ord('A')` for uppercase. They are different locker rooms: `ord('a') = 97`, `ord('A') = 65`. Using the wrong base gives indices in the range 32–57 instead of 0–25, causing an `IndexError` in a frequency array.

```python
# WRONG: forgetting which base
idx = ord('h') - ord('A')   # 104 - 65 = 39 -> IndexError on [0]*26

# RIGHT: match the case
idx = ord('h') - ord('a')   # 104 - 97 = 7 -> correct
```

> 📝 **Practice:** [Q1 · string-immutability-explain](./practice.md#q1--string-immutability-explain----why-cant-you-modify-s0-)

> [↑ Back to Top](#top)

<a id="string-as-an-array-of-characters"></a>
# 2. String as an Array of Characters

Conceptually:

```
Index:   0   1   2   3   4
Value:   h   e   l   l   o
```

You can access:

```python
s[0]  # 'h'
```

Time complexity: O(1)

Because string indexing works like array indexing.

> [↑ Back to Top](#top)

<a id="why-strings-are-immutable"></a>
# 3. Why Strings Are Immutable

In Python, once a string is created, it cannot be modified.

Example:

```python
s = "hello"
s[0] = "H"   # Error
```

Why immutability?

1. Memory safety
2. Hashing stability (important for dictionaries)
3. Thread safety
4. Performance optimization (string interning)

If strings were mutable, hashing and dictionary keys would break.

## Visual: Strings Are Carved in Stone

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

When you use `+`, you did NOT modify `"hello"`. You created a **brand new string** and pointed `s` at it. The old `"hello"` still exists in memory (until garbage collected).

```
Before:
  s ──→ "hello"

After s = s + " world":
  s ──→ "hello world"   (new object in memory)
         "hello"        (old object, now unreferenced, will be garbage collected)
```

**Common mistake — forgetting strings are immutable:** Trying `s[0] = 'H'` raises a `TypeError`. The fix is to convert to a list, modify the list, then join back: `chars = list(s); chars[0] = 'H'; s = ''.join(chars)`.

> 📝 **Practice:** [Q1 · string-immutability-explain](./practice.md#q1--string-immutability-explain----why-cant-you-modify-s0-)

> [↑ Back to Top](#top)

<a id="what-happens-when-you-modify-a-string"></a>
# 4. What Happens When You Modify a String?

When you write:

```python
s = "hello"
s = s + " world"
```

Python does not modify the original string.

It:

1. Creates new string
2. Copies old content
3. Appends new content
4. Reassigns reference

So concatenation creates a new object.

This is important for performance.

> [↑ Back to Top](#top)

<a id="time-complexity-of-string-operations"></a>
# 5. Time Complexity of String Operations

| Operation | Complexity |
|------------|------------|
| Indexing | O(1) |
| Slicing | O(k) |
| Concatenation | O(n + m) |
| Length | O(1) |
| Iteration | O(n) |
| Searching (in operator) | O(n) |

Important insight:
Slicing creates new string → O(k), not O(1).

> [↑ Back to Top](#top)

<a id="why-repeated-concatenation-is-dangerous"></a>
# 6. Why Repeated Concatenation Is Dangerous

Example:

```python
result = ""
for char in data:
    result += char
```

Each concatenation:
- Creates new string
- Copies entire previous content

If n characters:

Total complexity becomes O(n²)

Better approach:

```python
result = []
for char in data:
    result.append(char)

final = "".join(result)
```

join() builds string efficiently in O(n).

This is a very common interview discussion.

**Common mistake — concatenating strings in a loop:** Every `+=` copies the entire string so far. Building "hello" character by character writes 0+1+2+3+4 = 10 extra characters beyond the 5 you need — and that grows to O(n²) for length n. For n=50,000 characters, `''.join()` is roughly **700x faster** than `+=` in a loop.

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

> 📝 **Practice:** [Q2 · build-string-join-vs-concat](./practice.md#q2--build-string-join-vs-concat----build-a-string-from-a-list-of-chars-)

> [↑ Back to Top](#top)

<a id="string-interning"></a>
# 7. String Interning

Python optimizes small strings.

Example:

```python
a = "hello"
b = "hello"
```

Sometimes both refer to same memory location.

This is called **string interning**.

It improves memory efficiency and speed.

But never rely on it in logic.

> [↑ Back to Top](#top)

<a id="memory-representation"></a>
# 8. Memory Representation

Strings in Python are Unicode.

Each character:
- Can take different number of bytes
- Optimized internally depending on character set

Unlike C:
Strings are not null-terminated arrays.

Python stores:
- Length
- Hash
- Character data

Length retrieval is O(1).

> [↑ Back to Top](#top)

<a id="common-string-operations"></a>
# 9. Common String Operations

## 1. Slicing

```python
s[1:4]
```

Creates new string.

Time: O(k)

## Visual: Substrings — The Window on the Tape

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

## 2. Reverse String

```python
s[::-1]
```

Creates new reversed string.

Time: O(n)

> 📝 **Practice:** [Q3 · reverse-string](./practice.md#q3--reverse-string----reverse-a-string-in-place-no-extra-string-)

## 3. Split

```python
s.split(" ")
```

Returns list of substrings.

Time: O(n)

**Common mistake — split() vs split(' '):** `split()` with no argument is the smart scissors — it collapses any whitespace and never produces empty strings. `split(' ')` is the dumb scissors — it cuts at every single space, producing empty strings for leading, trailing, and consecutive spaces. For messy input like `"  hello   world  "`, `split()` gives `['hello', 'world']` while `split(' ')` gives `['', '', 'hello', '', '', 'world', '', '']`.

```python
s = "  hello   world  "

# WRONG for word counting:
s.split(' ')   # ['', '', 'hello', '', '', 'world', '', '']

# RIGHT:
s.split()      # ['hello', 'world']
```

Use `split(delimiter)` only when you need a specific separator and want to preserve empty fields (e.g., CSV parsing).

> 📝 **Practice:** [Q6 · split-join-strip](./practice.md#q6--split-join-strip----know-your-string-methods-)

## 4. Replace

```python
s.replace("a", "b")
```

Creates new string.

Time: O(n)

> [↑ Back to Top](#top)

<a id="string-comparison"></a>
# 10. String Comparison

```python
"abc" == "abc"
```

Python compares lexicographically.

Worst case complexity: O(n)

Stops early if mismatch found.

## Visual: Lexicographic Order — The Dictionary Game

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

**Common mistake — case sensitivity in comparisons:** `'P'` (ASCII 80) is not equal to `'p'` (ASCII 112). Forgetting `.lower()` before comparison silently misses matches. Always normalize: `s1.lower() == s2.lower()` or use `sorted(s.lower())` for anagram checks.

**Common mistake — string comparison is lexicographic not numeric:** `sorted(["10", "9", "2"])` gives `['10', '2', '9']` because `'1' < '2' < '9'` by ASCII value. For numeric ordering, use `key=int`:

```python
# WRONG:
sorted(["10", "9", "2"])         # ['10', '2', '9']

# RIGHT:
sorted(["10", "9", "2"], key=int) # ['2', '9', '10']
```

> [↑ Back to Top](#top)

<a id="string-vs-list-of-characters"></a>
# 11. String vs List of Characters

| Feature | String | List of Characters |
|----------|---------|------------------|
| Mutable | ❌ | ✅ |
| Indexing | O(1) | O(1) |
| Concatenation | Expensive | Cheap |
| Memory | Efficient | Slightly more |

If frequent modifications needed:
Convert to list.

> [↑ Back to Top](#top)

<a id="important-interview-patterns-with-strings"></a>
# 12. Important Interview Patterns with Strings

Most string problems fall into patterns:

1. Two pointers
2. Sliding window
3. Frequency counting (hashing)
4. Palindrome checking
5. Substring search
6. Anagram detection
7. Prefix/suffix comparison

Recognizing pattern is critical.

> 📝 **Practice:** [Q9 · palindrome-two-pointer](./practice.md#q9--palindrome-two-pointer----check-if-a-string-is-a-palindrome-) · [Q11 · anagram-detection-counter](./practice.md#q11--anagram-detection-counter----are-two-strings-anagrams-) · [Q14 · longest-no-repeat-substring](./practice.md#q14--longest-no-repeat-substring----sliding-window-no-repeats-)

> [↑ Back to Top](#top)

<a id="anagram-detection"></a>
# Anagram Detection

Two words are anagrams if they use the same characters with the same frequencies.
"listen" and "silent" are anagrams. "hello" and "world" are not.

## Visual: Anagram Detection — Two Strategies

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

> [↑ Back to Top](#top)

<a id="sliding-window--longest-no-repeat-substring"></a>
# Sliding Window — Longest No-Repeat Substring

Problem: find the longest substring without repeating characters.
Input: `"abcabcbb"`. Answer: `"abc"` (length 3).

## Visual: Sliding Window

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

Step 8-9: Continue shrinking for repeated 'b' and 'b'. max_len stays 3.

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

**Common mistake — sliding window missing update after shrink:** When the left pointer moves right and removes a character from the window, you must update the validity counter (`have`). Forgetting this means the loop keeps thinking the window satisfies all requirements even after it no longer does, producing incorrect minimum-window results.

```python
# When shrinking, always update validity:
left_char = s[left]
window[left_char] -= 1
left += 1
if left_char in need and window[left_char] < need[left_char]:
    have -= 1   # ← this line is the critical update
```

> 📝 **Practice:** [Q14 · longest-no-repeat-substring](./practice.md#q14--longest-no-repeat-substring----sliding-window-no-repeats-)

> [↑ Back to Top](#top)

<a id="palindrome-checking"></a>
# 13. Palindrome Checking

Efficient method:

Two pointers:

```python
left = 0
right = len(s) - 1
```

Move inward.

Time: O(n)
Space: O(1)

Better than reversing string (extra memory).

## Visual: Palindrome — The Mirror Check

A palindrome reads the same forwards and backwards.

### Two-Pointer Approach

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

### Longest Palindromic Substring — Expand Around Center

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

**Common mistake — palindrome check with non-alphanumeric:** Most palindrome problems (e.g., "A man, a plan, a canal: Panama") require filtering out spaces and punctuation before checking. Without `isalnum()` and `.lower()`, the raw reversal comparison fails silently.

```python
# WRONG:
s == s[::-1]   # fails on "A man, a plan, a canal: Panama"

# RIGHT:
cleaned = ''.join(c.lower() for c in s if c.isalnum())
return cleaned == cleaned[::-1]
```

> 📝 **Practice:** [Q9 · palindrome-two-pointer](./practice.md#q9--palindrome-two-pointer----check-if-a-string-is-a-palindrome-) · [Q10 · palindrome-with-nonalnum](./practice.md#q10--palindrome-with-nonalnum----valid-palindrome-ignoring-punctuation-)
> 📝 **Practice:** [Q8 · palindrome-check](../dsa_practice_questions_100.md#q8--thinking--palindrome-check)

> [↑ Back to Top](#top)

<a id="substring-search"></a>
# 14. Substring Search

Basic method:
Linear scan → O(nm)

Optimized algorithms:
- KMP → O(n + m)
- Rabin-Karp
- Boyer-Moore

For senior roles, knowing at least KMP is expected.

## Visual: KMP Failure Function

The KMP algorithm (Knuth-Morris-Pratt) searches for a pattern inside text efficiently.
When a mismatch occurs, the pattern itself tells you how far to jump back.
This information is encoded in the **failure function** (prefix function).

### Building the Failure Array

For each position in the pattern, we ask: "What is the longest proper prefix of this substring that is also a suffix?"

Example pattern: `"ABABC"`

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

Pattern: A  B  A  B  C
         0  0  1  2  0
```

### Search Trace on "ABABDABABC"

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

**Common mistake — using `in` for substring vs character check:** `"ab" in s` checks whether `"ab"` appears as a substring, not whether `'a'` or `'b'` is a character. Also: `find()` returns `-1` when the pattern is not found; `index()` raises `ValueError`. Use `find()` when the substring might be absent.

```python
pos = s.find("xyz")    # -1 if not found — safe
pos = s.index("xyz")   # ValueError if not found — crashes without try/except
```

**Common mistake — KMP failure function off-by-one:** When a mismatch occurs during lps construction, fall back to `lps[length - 1]`, not `lps[length]`. Using `lps[length]` over-falls and produces incorrect values for patterns with overlapping prefixes, making the search miss valid matches.

> 📝 **Practice:** [Q22 · kmp-lps-build](./practice.md#q22--kmp-lps-build----build-the-kmp-failure-lps-array-) · [Q23 · kmp-full-search](./practice.md#q23--kmp-full-search----full-kmp-pattern-search-)
> 📝 **Practice:** [Q9 · substring-search](../dsa_practice_questions_100.md#q9--code--substring-search)

> 📝 **Practice:** [Q71 · kmp-string-matching](../dsa_practice_questions_100.md#q71--thinking--kmp-string-matching)

> [↑ Back to Top](#top)

<a id="space-complexity-considerations"></a>
# 15. Space Complexity Considerations

String of size n:
Space = O(n)

But operations like slicing:
Create additional O(k) memory.

Recursive string problems:
Add stack space.

> [↑ Back to Top](#top)

<a id="when-not-to-use-strings-directly"></a>
# 16. When NOT To Use Strings Directly

Avoid direct string concatenation in loops.

Avoid string-heavy processing for massive data:
Consider:
- Streaming
- Byte arrays
- Memory-efficient structures

> [↑ Back to Top](#top)

<a id="real-world-usage-of-strings"></a>
# 17. Real-World Usage of Strings

Strings are everywhere in production systems. Three deep examples follow.

## Real-World: Full-Text Search Engines

Google, Elasticsearch, and Lucene do not scan every document for every query.
They preprocess documents into an **inverted index**: a hash map from term to list of document IDs.
At query time, a word lookup is O(1) in the index rather than O(n * m) brute force.

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
    """AND search across all query terms."""
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

# KMP for single-pattern scan — used in grep, log scanners
def kmp_search(text: str, pattern: str) -> list:
    if not pattern:
        return []
    m = len(pattern)
    fail = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = fail[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        fail[i] = j
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

Elasticsearch uses BM25 ranking on top of an inverted index.
KMP is used in `grep`, `awk`, and every log analysis tool.

## Real-World: Log Parsing

Application logs are unstructured strings. Logstash, Fluent Bit, and CloudWatch Logs Insights
use regex and substring matching to extract structured fields from raw log lines.

```python
import re

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
```

In production, Logstash's Grok filter expands named regex patterns like `%{COMBINEDAPACHELOG}`
into the full nginx pattern shown above. Use KMP for fast fixed-string literal search;
use regex for flexible structural patterns.

## Real-World: URL Parsing and Routing

Every web framework (Flask, Django, FastAPI) routes incoming URLs to handler functions.
URL routing is a string pattern matching problem. Flask's Werkzeug compiles URL rules
into a regex automaton; FastAPI's Starlette matches path parameters with regex groups.

```python
import re
from typing import Callable

class Router:
    """Simplified URL router — similar to Flask/Express internals."""

    def __init__(self):
        self.routes = []  # list of (compiled_regex, handler)

    def add_route(self, pattern: str, handler: Callable):
        """Register a URL pattern. :param syntax converted to named groups."""
        param_pattern = re.sub(r':(\w+)', r'(?P<\1>[^/]+)', pattern)
        regex = re.compile(f'^{param_pattern}$')
        self.routes.append((regex, handler))

    def dispatch(self, path: str):
        """Find handler for incoming request path."""
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

# URL parsing — splits a URL into components
from urllib.parse import urlparse, parse_qs

url = "https://api.example.com/v1/search?q=python+strings&page=2&limit=10"
parsed = urlparse(url)
print(f"Scheme: {parsed.scheme}")    # https
print(f"Host:   {parsed.netloc}")    # api.example.com
print(f"Path:   {parsed.path}")      # /v1/search
params = parse_qs(parsed.query)
print(f"Params: {params}")
```

At scale, Nginx uses a radix tree (compressed trie) for O(m) URL routing
where m is the URL length — more efficient than iterating all regex patterns.

> [↑ Back to Top](#top)

<a id="performance-estimation"></a>
# 18. Performance Estimation

If string length = 10⁵:

- O(n²) operations → too slow
- O(n log n) → acceptable
- O(n) → ideal

Always check constraints before choosing approach.

> [↑ Back to Top](#top)

<a id="advanced-topics"></a>
# 19. Advanced Topics (For Senior Roles)

- KMP algorithm
- Rolling hash
- Trie-based prefix search
- Suffix arrays (conceptual)
- Memory-efficient streaming parsing

These are expected for high-level product roles.

> [↑ Back to Top](#top)

<a id="complexity-cheat-sheet"></a>
# Complexity Cheat Sheet

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

### The Key Intuitions

1. **Immutability** means operations that look O(1) might be O(n). Building strings with `+` in a loop is a classic trap.
2. **Two pointers** solve many palindrome problems in O(n) with O(1) space.
3. **Sliding window** solves substring problems that would otherwise be O(n²).
4. **Frequency maps** (Counter/dict) turn many string comparison problems from O(n log n) to O(n).
5. **KMP** is the go-to when you need to find all occurrences of a pattern quickly.

> [↑ Back to Top](#top)

<a id="final-summary"></a>
# 📌 Final Summary

Strings are:

- Immutable sequences of characters
- Indexed and iterable
- Backed by contiguous memory
- Optimized for read-heavy operations

They are powerful,
but expensive for repeated modifications.

Understanding immutability,
memory behavior,
and algorithmic patterns
is essential for mastering string problems.

> 📝 **Practice:** [Q72 · rabin-karp-hash](../dsa_practice_questions_100.md#q72--normal--rabin-karp-hash)

> 📝 **Practice:** [Q7 · anagram-detection](../dsa_practice_questions_100.md#q7--code--anagram-detection)

> [↑ Back to Top](#top)

**[🏠 Back to README](../README.md)**

**Prev:** [← Arrays](../02_arrays/theory.md) | **Next:** [Recursion →](../04_recursion/theory.md)

**Related Topics:** [Cheat Sheet](./cheetsheet.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)
