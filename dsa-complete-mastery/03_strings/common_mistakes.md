# Common Mistakes with Python Strings

> "Strings look simple. They are a sequence of characters. How hard can it be? — Famous last words before a 3-hour debugging session."

Strings are deceptively tricky. They look like lists but are immutable. They look simple but hide quadratic time bombs. This guide covers every major string mistake with stories, traces, and the right fix.

---

## Table of Contents

1. [Concatenating Strings in a Loop](#1-concatenating-strings-in-a-loop)
2. [Forgetting Strings Are Immutable](#2-forgetting-strings-are-immutable)
3. [str.split() vs str.split(' ')](#3-strsplit-vs-strsplit-)
4. [Case Sensitivity in Comparisons](#4-case-sensitivity-in-comparisons)
5. [Confusing in for Substring vs Character Check](#5-confusing-in-for-substring-vs-character-check)
6. [Ord/Chr Confusion](#6-ordchr-confusion)
7. [Sliding Window: Missing the Update After Shrink](#7-sliding-window-missing-the-update-after-shrink)
8. [KMP Failure Function Off-by-One](#8-kmp-failure-function-off-by-one)
9. [Palindrome Check with Non-Alphanumeric](#9-palindrome-check-with-non-alphanumeric)
10. [String Comparison is Lexicographic Not Numeric](#10-string-comparison-is-lexicographic-not-numeric)
11. [f-string vs format vs %](#11-f-string-vs-format-vs-)

---

## 1. Concatenating Strings in a Loop

### The Story: The Broken Tape Recorder

Imagine a tape recorder where every time you add a new word, you have to copy the entire tape from the beginning, add the word to the end of a new tape, and throw away the old tape. For 1 word: copy 0 characters + add 1. For 2 words: copy 1 + add 1. For 3 words: copy 2 + add 1. By the time you have typed 10,000 characters this way, you have physically written 1+2+3+...+10000 ≈ 50 million characters. That is what `result += char` does inside a loop.

Strings in Python are immutable. Every `+=` operation creates an entirely new string object. The old one gets garbage-collected, but the copy already happened. For n concatenations the total work is O(1 + 2 + 3 + ... + n) = O(n²).

### The WRONG Code

```python
# WRONG: Building a string character by character with +=
def reverse_string_wrong(s):
    result = ""
    for char in s:
        result += char   # BUG: O(n) copy every iteration -> O(n²) total!
    return result

# Also wrong in a more subtle way: building output in a loop
def join_words_wrong(words):
    sentence = ""
    for word in words:
        sentence += word + " "   # BUG: creates new string object each time
    return sentence.strip()
```

### Why It Is O(n²): A Concrete Trace

```
Building "hello" character by character:

Iteration 1: result = "" + "h"    = "h"      (copied 0 chars, wrote 1)
Iteration 2: result = "h" + "e"   = "he"     (copied 1 char, wrote 1)
Iteration 3: result = "he" + "l"  = "hel"    (copied 2 chars, wrote 1)
Iteration 4: result = "hel" + "l" = "hell"   (copied 3 chars, wrote 1)
Iteration 5: result = "hell" + "o"= "hello"  (copied 4 chars, wrote 1)

Total characters written: 0+1+2+3+4 + 5 = 15 for a 5-char string.

For a string of length n:
  Total work = 0 + 1 + 2 + ... + (n-1) + n = n*(n+1)/2 = O(n²)

For n = 10,000 characters: ~50 million character copies.
For n = 100,000 characters: ~5 billion character copies.
```

### Performance Measurement

```python
import time

n = 50_000

# Method 1: += in loop (O(n²))
chars = ['x'] * n
start = time.time()
result = ""
for c in chars:
    result += c
slow_time = time.time() - start

# Method 2: ''.join() (O(n))
start = time.time()
result = ''.join(chars)
fast_time = time.time() - start

print(f"Loop +=:      {slow_time:.4f}s")
print(f"''.join():    {fast_time:.6f}s")
print(f"Speedup:      {slow_time / fast_time:.0f}x faster")

# Typical output:
# Loop +=:      0.8500s
# ''.join():    0.001200s
# Speedup:      700x faster
```

### The RIGHT Code: ''.join()

```python
# RIGHT: Collect pieces, join once at the end
def reverse_string_right(s):
    chars = []
    for char in s:
        chars.append(char)  # O(1) amortized
    return ''.join(chars)   # O(n) once at the end

# Or even cleaner:
def reverse_string_pythonic(s):
    return ''.join(reversed(s))  # or s[::-1]


# RIGHT: Building sentences
def join_words_right(words):
    return ' '.join(words)  # join handles the separator cleanly!


# RIGHT: When building in a complex loop
def process_and_build(data):
    parts = []
    for item in data:
        if item > 0:
            parts.append(str(item))
        else:
            parts.append("X")
    return '-'.join(parts)

print(process_and_build([1, -2, 3, 0, 4]))  # "1-X-3-X-4"
```

### The join() Pattern Explained

```python
# ''.join(iterable) works like:
# Take every item in iterable (must be strings)
# Place the separator ('') between each one
# Return the full concatenated string, all in ONE allocation

separator = '-'
parts = ['a', 'b', 'c', 'd']
result = separator.join(parts)
# Result: "a-b-c-d"

# The separator goes BETWEEN items, not before or after.
# ''.join(['a','b','c']) = "abc"  (no separator)
# ' '.join(['hello','world']) = "hello world"
# '\n'.join(['line1','line2']) = "line1\nline2"
```

### Mini Test Case

```python
import time

# Verify correctness AND performance
words = ["the", "quick", "brown", "fox"]

wrong_result = ""
for w in words:
    wrong_result += w + " "
wrong_result = wrong_result.strip()

right_result = " ".join(words)

assert wrong_result == right_result == "the quick brown fox"
print("Both give the same result, but join() is vastly faster for large inputs.")
```

---

## 2. Forgetting Strings Are Immutable

### The Story: The Engraved Marble Slab

Once a string is created in Python, it is like an engraved marble slab. You can read every character, you can make a new slab with modifications, but you cannot chip into the existing slab and change a letter. Trying to do so raises a TypeError.

This surprises many programmers coming from C or Java (where char arrays are mutable), or from JavaScript (where... strings are also immutable, but the error is less obvious).

### The WRONG Code

```python
# WRONG: Trying to modify a string in place
s = "hello"

s[0] = 'H'          # TypeError: 'str' object does not support item assignment
s[0] = s[0].upper() # Same error

# Also wrong: trying to "fix" part of a string directly
def capitalize_first_wrong(s):
    s[0] = s[0].upper()  # TypeError!
    return s
```

### The Error Message

```
Traceback (most recent call last):
  File "example.py", line 3, in <module>
    s[0] = 'H'
TypeError: 'str' object does not support item assignment
```

### Why Strings Are Immutable: Python Interning

```
CPython interns (caches) frequently used strings.
For example, all variable names and short strings are interned.

>>> a = "hello"
>>> b = "hello"
>>> a is b   # True! Same object in memory.
True

If strings were mutable, changing a would change b too!
Immutability makes this safe caching possible.

It also means strings are hashable (can be used as dict keys).
Mutable objects cannot be reliably hashed.
```

### The RIGHT Approaches

**Approach A: Convert to list, modify, join back**

```python
# RIGHT: Convert to list for character-level modification
def capitalize_first(s):
    if not s:
        return s
    chars = list(s)      # mutable list of characters
    chars[0] = chars[0].upper()
    return ''.join(chars)

print(capitalize_first("hello"))  # "Hello"
print(capitalize_first("world"))  # "World"


# RIGHT: Replace a character at a specific index
def replace_char(s, index, new_char):
    chars = list(s)
    chars[index] = new_char
    return ''.join(chars)

print(replace_char("hello", 1, 'a'))  # "hallo"
```

**Approach B: String slicing to build new string**

```python
# RIGHT: Use slicing to create a new string with modifications
def replace_char_slice(s, index, new_char):
    return s[:index] + new_char + s[index+1:]

print(replace_char_slice("hello", 1, 'a'))  # "hallo"
print(replace_char_slice("python", 0, 'P')) # "Python"
```

**Approach C: Using built-in string methods (most common)**

```python
# Most string operations are built in
s = "Hello, World!"

print(s.lower())           # "hello, world!"
print(s.upper())           # "HELLO, WORLD!"
print(s.replace('l', 'L')) # "HeLLo, WorLd!"
print(s.strip())           # "Hello, World!" (strips whitespace from ends)

# These all return NEW strings -- the original s is unchanged
print(s)  # "Hello, World!"  -- still the same
```

### Common Pattern: Reversing a String

```python
# WRONG attempt
s = "hello"
for i in range(len(s) // 2):
    s[i], s[len(s)-1-i] = s[len(s)-1-i], s[i]  # TypeError!

# RIGHT: slice
s = "hello"
reversed_s = s[::-1]
print(reversed_s)  # "olleh"

# RIGHT: join(reversed())
reversed_s = ''.join(reversed(s))
print(reversed_s)  # "olleh"

# RIGHT: convert to list, swap in place, join back
s_list = list(s)
left, right = 0, len(s_list) - 1
while left < right:
    s_list[left], s_list[right] = s_list[right], s_list[left]
    left += 1
    right -= 1
reversed_s = ''.join(s_list)
print(reversed_s)  # "olleh"
```

### Mini Test Case

```python
# Verify the list approach works
s = "interview"
chars = list(s)

# Capitalize vowels
for i, c in enumerate(chars):
    if c in 'aeiou':
        chars[i] = c.upper()

result = ''.join(chars)
print(result)   # "IntErvIEw"
print(s)        # "interview"  -- original unchanged!
```

---

## 3. str.split() vs str.split(' ')

### The Story: The Smart Scissors vs the Dumb Scissors

`str.split()` (no argument) is the smart scissors. It knows that "whitespace is whitespace." Multiple spaces? Cut at all of them. Leading spaces? Ignore them. Trailing spaces? Ignore them. Empty strings in the result? Never produce them.

`str.split(' ')` (explicit space argument) is the dumb scissors. It cuts at every single space character, exactly once each. Multiple spaces? Multiple cuts, producing empty strings between them. Leading space? Empty string at the start. Trailing space? Empty string at the end.

### The WRONG Code

```python
# Input with messy whitespace (common in interview problems and real data)
s = "  hello   world  "

# WRONG: Using split(' ') on messy input
words_wrong = s.split(' ')
print(words_wrong)
# ['', '', 'hello', '', '', 'world', '', '']
# That's 8 elements with empty strings!

# Counting words -- completely wrong result
print(len(words_wrong))  # 8  -- but there are only 2 words!

# Joining them back
print(' '.join(words_wrong))  # "  hello   world  "  -- actually preserves spaces
```

### Detailed Comparison

```python
s = "  hello   world  "

# split() with no argument:
print(s.split())
# ['hello', 'world']
# - Splits on ANY whitespace (space, tab, newline)
# - Multiple consecutive whitespace treated as one separator
# - Leading and trailing whitespace ignored
# - Never produces empty strings

# split(' ') with explicit space:
print(s.split(' '))
# ['', '', 'hello', '', '', 'world', '', '']
# - Splits on EXACTLY one space character each
# - Each space is a separate separator
# - Produces empty strings between consecutive spaces
# - Includes empty strings for leading/trailing spaces

# split('\n') for line-by-line:
multiline = "line1\nline2\n\nline4"
print(multiline.split('\n'))  # ['line1', 'line2', '', 'line4']
print(multiline.splitlines()) # ['line1', 'line2', '', 'line4'] -- same here, but
                               # splitlines() handles \r\n and \r too
```

### Surprising Cases with Tabs and Newlines

```python
# split() handles ALL whitespace
s = "hello\tworld\nnext line"
print(s.split())    # ['hello', 'world', 'next', 'line']

# split(' ') only handles spaces
print(s.split(' '))  # ['hello\tworld\nnext', 'line'] -- tab and newline NOT split!


# Real-world gotcha: CSV-like data
data = "Alice, 25, Engineer"
print(data.split(', '))  # ['Alice', '25', 'Engineer']  -- correct
print(data.split(','))   # ['Alice', ' 25', ' Engineer'] -- leading spaces!
```

### When to Use Each

```python
# Use split() when:
# - You want tokens/words and don't care about exact whitespace
# - Handling user input (may have irregular spacing)
# - Counting words

sentence = "  The  quick brown   fox  "
words = sentence.split()
print(f"Words: {words}")     # ['The', 'quick', 'brown', 'fox']
print(f"Count: {len(words)}") # 4


# Use split(delimiter) when:
# - You have a specific delimiter (comma, pipe, tab)
# - You WANT to preserve the structure including empty fields
# - Parsing CSV-like data where empty fields matter

csv = "Alice,,Engineer"   # empty field in the middle!
fields = csv.split(',')
print(fields)   # ['Alice', '', 'Engineer']  -- empty string preserved, which is correct!


# Use split(None, maxsplit) when:
# - You only want to split a limited number of times
s = "first second third fourth"
print(s.split(None, 2))  # ['first', 'second', 'third fourth'] -- split at most 2 times
```

### Mini Test Case

```python
# Word frequency counter -- classic interview problem
def word_count_wrong(text):
    words = text.split(' ')   # WRONG for messy input
    return len([w for w in words if w])   # filter empty... but messy

def word_count_right(text):
    words = text.split()      # RIGHT: handles all whitespace cleanly
    return len(words)

text = "  the quick  brown fox  "
print(word_count_wrong(text))  # 4 (after filtering) -- this happens to work with filter
print(word_count_right(text))  # 4  -- clean and correct

# But without the filter:
print(len(text.split(' ')))    # 7 (includes empty strings!)
print(len(text.split()))       # 4 (correct!)
```

---

## 4. Case Sensitivity in Comparisons

### The Story: The Distracted Librarian

A librarian is checking if two book titles match. "Python Programming" vs "python programming" — they have the same words! But the librarian is checking letter by letter, and capital 'P' (ASCII 80) is NOT the same as lowercase 'p' (ASCII 112). The books get filed separately. The duplicate check misses the match.

Forgetting `.lower()` or `.upper()` is one of the most common silent bugs in string comparison problems.

### The WRONG Code

```python
# WRONG: Case-sensitive comparison when problem wants case-insensitive
def is_anagram_wrong(s1, s2):
    """Check if s1 and s2 are anagrams."""
    if len(s1) != len(s2):
        return False
    return sorted(s1) == sorted(s2)

print(is_anagram_wrong("Listen", "Silent"))  # False -- WRONG!
# 'L' != 'l' and 'S' != 's' in the sorted comparison
```

### Visual Trace: Why Case Breaks It

```
s1 = "Listen"  -> sorted: ['L', 'e', 'i', 'n', 's', 't']
                           ASCII: 76 101 105 110 115 116

s2 = "Silent"  -> sorted: ['S', 'e', 'i', 'l', 'n', 't']
                           ASCII: 83 101 105 108 110 116

Comparison: ['L','e','i','n','s','t'] vs ['S','e','i','l','n','t']
Position 0: 'L' (76) vs 'S' (83) -- DIFFERENT!
Result: False

But if we lowercase both:
sorted("listen") = ['e', 'i', 'l', 'n', 's', 't']
sorted("silent") = ['e', 'i', 'l', 'n', 's', 't']
-- EQUAL! They are anagrams!
```

### The RIGHT Code

```python
# RIGHT: Normalize case before comparison
def is_anagram_right(s1, s2):
    s1 = s1.lower()   # normalize
    s2 = s2.lower()   # normalize
    if len(s1) != len(s2):
        return False
    return sorted(s1) == sorted(s2)

print(is_anagram_right("Listen", "Silent"))  # True -- correct!
print(is_anagram_right("Triangle", "Integral"))  # True


# RIGHT: Using Counter for O(n) solution (still normalize first)
from collections import Counter

def is_anagram_counter(s1, s2):
    return Counter(s1.lower()) == Counter(s2.lower())

print(is_anagram_counter("Astronomer", "Moon starer"))  # False (space issue, see below)
# If we also strip spaces:
def is_anagram_full(s1, s2):
    clean = lambda s: s.lower().replace(' ', '')
    return Counter(clean(s1)) == Counter(clean(s2))

print(is_anagram_full("Astronomer", "Moon starer"))  # True!
```

### Other Case-Sensitive Traps

```python
# Trap 1: Case in dict keys
freq = {}
text = "Hello World hello"
for word in text.split():
    freq[word] = freq.get(word, 0) + 1

print(freq)  # {'Hello': 1, 'World': 1, 'hello': 1}
# 'Hello' and 'hello' are DIFFERENT keys!

# Right: normalize before counting
freq_right = {}
for word in text.lower().split():
    freq_right[word] = freq_right.get(word, 0) + 1

print(freq_right)  # {'hello': 2, 'world': 1}


# Trap 2: Case in string search
s = "Python is Great"
print("great" in s)       # False -- case mismatch!
print("great" in s.lower()) # True  -- correct


# Trap 3: String equality in if conditions
user_input = "YES"
if user_input == "yes":   # WRONG: won't match "YES" or "Yes"
    print("Confirmed")

if user_input.lower() == "yes":  # RIGHT: matches any case
    print("Confirmed")
```

### Mini Test Case

```python
# Group anagrams -- classic interview problem
def group_anagrams(strs):
    from collections import defaultdict
    groups = defaultdict(list)
    for s in strs:
        key = ''.join(sorted(s.lower()))  # normalize case!
        groups[key].append(s)
    return list(groups.values())

words = ["eat", "Tea", "tan", "ate", "nat", "bat"]
result = group_anagrams(words)
print(result)
# [['eat', 'Tea', 'ate'], ['tan', 'nat'], ['bat']]
# 'eat' and 'Tea' correctly grouped as anagrams!
```

---

## 5. Confusing `in` for Substring vs Character Check

### The Story: Two Different Security Guards

One security guard (the substring guard) checks if a sequence of people are standing in line exactly in the right order. "ab" in "xabcx" — is there a sequence 'a' then 'b' somewhere in the crowd? Yes.

Another guard (the character guard) checks if a single person is anywhere in the building. 'a' in "xabcx" — is there an 'a' anywhere? Yes.

Both use `in` in Python, but with different semantics. The confusion comes when you mix up `find()` and `index()` — one returns -1 on failure, the other raises an exception.

### The Basics of `in`

```python
s = "hello world"

# Substring check (any length)
print("hello" in s)    # True  -- "hello" appears as a substring
print("world" in s)    # True
print("xyz" in s)      # False
print("lo wo" in s)    # True  -- "lo wo" spans both words

# Single character check (also uses 'in')
print('h' in s)        # True  -- 'h' is in the string
print('z' in s)        # False

# Empty string is ALWAYS in every string
print("" in s)         # True  -- vacuously true
print("" in "")        # True
```

### The Confusion: Intent vs Behavior

```python
# Problem: Count vowels in a string
s = "hello"

# This works correctly but can be confusing:
vowels = "aeiou"
count = sum(1 for c in s if c in vowels)
# Here 'c' is one character, and we check if that character is IN the vowel string.
# Works correctly: 'h','e','l','l','o' -> only 'e' and 'o' pass -> count = 2
print(count)  # 2 -- correct

# Common mistake: checking substring when you mean character
s = "hello world"
# WRONG intent: "is 'ab' one of the individual characters?"
if "ab" in s:  # This checks if "ab" is a SUBSTRING, not a character
    print("found")
# "ab" is not a substring of "hello world", so nothing prints.
# But the person might have meant to check each character individually.
```

### find() vs index(): The Silent vs Loud Failure

```python
s = "hello world"

# find() returns -1 if not found (safe, no exception)
pos = s.find("xyz")
print(pos)  # -1 -- not found, but no exception

pos = s.find("world")
print(pos)  # 6 -- found at index 6


# index() raises ValueError if not found (loud, can crash)
pos = s.index("world")
print(pos)   # 6 -- same as find()

try:
    pos = s.index("xyz")  # ValueError!
except ValueError as e:
    print(f"Error: {e}")  # Error: substring not found
```

### WRONG Code: Using index() without error handling

```python
# WRONG: Assuming the substring always exists
def find_delimiter_wrong(text, delimiter):
    pos = text.index(delimiter)  # ValueError if delimiter not in text!
    return text[:pos], text[pos+1:]

find_delimiter_wrong("hello world", ",")  # ValueError: substring not found!
```

### RIGHT Code: Using find() or try/except

```python
# RIGHT Option A: Use find() and check for -1
def find_delimiter_right(text, delimiter):
    pos = text.find(delimiter)
    if pos == -1:
        return text, ""   # delimiter not found
    return text[:pos], text[pos+1:]

print(find_delimiter_right("hello,world", ","))  # ('hello', 'world')
print(find_delimiter_right("hello world", ","))   # ('hello world', '') -- graceful


# RIGHT Option B: Use index() with try/except (when you want to handle the error)
def parse_key_value(text):
    try:
        key, _, value = text.partition('=')
        return key.strip(), value.strip()
    except ValueError:
        return text.strip(), None


# partition() is often better than split/find for this pattern:
s = "key=value=with=equals"
key, sep, rest = s.partition('=')
print(key, rest)   # "key" "value=with=equals"  -- only splits at FIRST '='
```

### Mini Test Case

```python
# Demonstrate find vs index behavior
tests = ["hello world", "no comma here", "a,b,c"]
delimiter = ","

for t in tests:
    # find() approach -- safe
    pos = t.find(delimiter)
    if pos != -1:
        before, after = t[:pos], t[pos+1:]
        print(f"Found '{delimiter}' at {pos}: '{before}' | '{after}'")
    else:
        print(f"'{delimiter}' not in '{t}'")

# Output:
# ',' not in 'hello world'
# ',' not in 'no comma here'
# Found ',' at 1: 'a' | 'b,c'
```

---

## 6. Ord/Chr Confusion

### The Story: The Alphabet Locker Room

Imagine a locker room with lockers numbered 0 to 25 for lowercase letters. 'a' gets locker 0, 'b' gets locker 1, ..., 'z' gets locker 25. The formula is: `locker_number = ord(char) - ord('a')`.

There is a SEPARATE locker room for uppercase letters. 'A' gets locker 0 there, 'B' gets locker 1, etc. The formula is: `locker_number = ord(char) - ord('A')`.

The confusion: `ord('a') = 97` and `ord('A') = 65`. They are NOT the same locker room. Forgetting which locker room you are in causes index errors or wrong answers.

### The Core Values

```python
print(ord('a'))   # 97  (lowercase a)
print(ord('z'))   # 122 (lowercase z)
print(ord('A'))   # 65  (uppercase A)
print(ord('Z'))   # 90  (uppercase Z)
print(ord('0'))   # 48  (digit 0)
print(ord('9'))   # 57  (digit 9)

# chr() is the inverse
print(chr(97))    # 'a'
print(chr(65))    # 'A'
print(chr(122))   # 'z'
```

### The WRONG Code: Index Mapping

```python
# WRONG: Forgetting which base to subtract
def char_frequency_wrong(s):
    freq = [0] * 26
    for c in s:
        if c.isalpha():
            idx = ord(c) - ord('A')   # WRONG: this only works for uppercase!
            freq[idx] += 1            # For lowercase 'a': ord('a')-ord('A') = 32 -> index out of range!
    return freq

try:
    char_frequency_wrong("hello")
except IndexError as e:
    print(f"IndexError: {e}")
# IndexError: list assignment index out of range
# Because 'h' -> ord('h') - ord('A') = 104 - 65 = 39, which is >= 26!
```

### Visual Trace: The Wrong Index

```
For character 'h':
  ord('h') = 104
  ord('A') = 65
  index = 104 - 65 = 39   <-- out of range for a [0]*26 array!

For character 'h' (correct):
  ord('h') = 104
  ord('a') = 97
  index = 104 - 97 = 7    <-- correct! 'h' is the 7th letter (0-indexed)

Alphabet positions (0-indexed):
a=0, b=1, c=2, d=3, e=4, f=5, g=6, h=7, i=8, j=9, k=10, l=11, m=12
n=13, o=14, p=15, q=16, r=17, s=18, t=19, u=20, v=21, w=22, x=23, y=24, z=25
```

### The RIGHT Code

```python
# RIGHT: Normalize to lowercase first, then subtract ord('a')
def char_frequency_right(s):
    freq = [0] * 26
    for c in s.lower():   # normalize to lowercase
        if c.isalpha():
            idx = ord(c) - ord('a')  # 0 for 'a', 25 for 'z'
            freq[idx] += 1
    return freq

result = char_frequency_right("Hello World")
for i, count in enumerate(result):
    if count > 0:
        print(f"'{chr(ord('a') + i)}': {count}")
# 'd': 1
# 'e': 1
# 'h': 1
# 'l': 3
# 'o': 2
# 'r': 1
# 'w': 1
```

### Common Off-by-One with Chr Reconstruction

```python
# Building back the character from index
def index_to_char(i):
    return chr(ord('a') + i)   # i=0 -> 'a', i=25 -> 'z'

# WRONG: Adding 1 to 'a' accidentally
def index_to_char_wrong(i):
    return chr(ord('a') + i + 1)  # i=0 -> 'b'! Off by one!

print(index_to_char(0))         # 'a' -- correct
print(index_to_char_wrong(0))   # 'b' -- wrong!
print(index_to_char(25))        # 'z' -- correct


# Encoding trick: shift cipher
def caesar_shift(text, shift):
    result = []
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            shifted = (ord(c) - base + shift) % 26
            result.append(chr(base + shifted))
        else:
            result.append(c)
    return ''.join(result)

print(caesar_shift("Hello, World!", 3))  # "Khoor, Zruog!"
print(caesar_shift("Khoor, Zruog!", -3)) # "Hello, World!"
```

### Mini Test Case

```python
# Test char-to-index and back
for i in range(26):
    char = chr(ord('a') + i)
    idx = ord(char) - ord('a')
    assert idx == i, f"Failed for {char}: got {idx}, expected {i}"
    assert chr(ord('a') + idx) == char

print("All ord/chr mappings correct!")

# Test common interview pattern: is_anagram using frequency array
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    freq = [0] * 26
    for c in s:
        freq[ord(c) - ord('a')] += 1
    for c in t:
        freq[ord(c) - ord('a')] -= 1
    return all(f == 0 for f in freq)

print(is_anagram("anagram", "nagaram"))  # True
print(is_anagram("rat", "car"))          # False
```

---

## 7. Sliding Window: Missing the Update After Shrink

### The Story: The Security Guard Who Forgets to Update the Clipboard

Imagine a security guard checking if at least one of each required visitor type is in the building. They track a clipboard with counts. When a visitor leaves (left pointer moves right), the guard crosses off that person's type. But if they forget to check whether they still have enough of that type, the building might no longer satisfy the requirement — yet the guard keeps thinking it does, leading to invalid windows.

This is the sliding window bug: moving the left pointer forward and removing an element from the window, but forgetting to update whether the window is still "valid."

### The Problem: Minimum Window Substring

Find the minimum window in string `s` that contains all characters of string `t`.

```python
# WRONG: Forgetting to update validity after shrinking
def min_window_wrong(s, t):
    from collections import Counter

    need = Counter(t)          # what we need
    window = {}                # what we have in current window
    have = 0                   # how many distinct chars satisfied
    total_needed = len(need)   # total distinct chars to satisfy

    result = ""
    min_len = float('inf')
    left = 0

    for right in range(len(s)):
        char = s[right]
        window[char] = window.get(char, 0) + 1

        if char in need and window[char] == need[char]:
            have += 1

        # Try to shrink from left
        while have == total_needed:
            # Update result
            if right - left + 1 < min_len:
                min_len = right - left + 1
                result = s[left:right+1]

            # Remove left character
            left_char = s[left]
            window[left_char] -= 1
            left += 1

            # BUG: Forgot to update 'have'!
            # If window[left_char] drops below need[left_char],
            # we no longer satisfy that character's requirement,
            # but 'have' is not decremented!

    return result
```

### Visual Trace: The Missing Update

```
s = "ADOBECODEBANC", t = "ABC"
need = {'A':1, 'B':1, 'C':1}

... (finding first valid window ADOBEC) ...

Left pointer moves to shrink. Say we remove 'A' from the window.
Before: window = {'A':1, 'D':1, 'O':1, 'B':1, 'E':1, 'C':1}, have = 3
After removing 'A': window['A'] = 0

Correct behavior: have should drop from 3 to 2 (we no longer have enough 'A').
Bug behavior: have stays at 3, so the while loop keeps running!

The while loop continues shrinking even though we no longer have a valid window.
This skips potential valid windows and might give wrong minimum length.
```

### The RIGHT Code: Update have After Removing

```python
# RIGHT: Update 'have' when the window becomes invalid
def min_window_right(s, t):
    from collections import Counter

    if not s or not t:
        return ""

    need = Counter(t)
    window = {}
    have = 0
    total_needed = len(need)

    result = ""
    min_len = float('inf')
    left = 0

    for right in range(len(s)):
        char = s[right]
        window[char] = window.get(char, 0) + 1

        # Check if this character's requirement is now satisfied
        if char in need and window[char] == need[char]:
            have += 1

        # Shrink from left while window is valid
        while have == total_needed:
            # Update result if this window is smaller
            if right - left + 1 < min_len:
                min_len = right - left + 1
                result = s[left:right+1]

            # Remove left character from window
            left_char = s[left]
            window[left_char] -= 1
            left += 1

            # RIGHT: Update 'have' if requirement is no longer met
            if left_char in need and window[left_char] < need[left_char]:
                have -= 1   # <-- THIS IS THE CRITICAL LINE

    return result


# Test
print(min_window_right("ADOBECODEBANC", "ABC"))  # "BANC"
print(min_window_right("a", "a"))                # "a"
print(min_window_right("a", "aa"))               # ""
```

### General Sliding Window Template

```python
# Template for "minimum window" sliding window problems
def sliding_window_template(s, condition):
    """
    General template for shrinkable sliding window.
    The key pattern: update state when adding (right), update when removing (left).
    """
    left = 0
    state = {}  # whatever you track

    for right in range(len(s)):
        # 1. Expand: add s[right] to window
        # state[s[right]] += 1  (example)

        # 2. Shrink: while window violates condition, remove s[left]
        while False:  # replace False with your shrink condition
            # 3. ALWAYS update state when removing s[left]!
            # state[s[left]] -= 1  (example)
            # if state[s[left]] drops below threshold: update validity counter
            left += 1

        # 4. Update answer using current window [left, right]

    return None  # return answer
```

### Mini Test Case

```python
# Verify both handle edge cases
test_cases = [
    ("ADOBECODEBANC", "ABC", "BANC"),
    ("a", "a", "a"),
    ("a", "aa", ""),
    ("aa", "aa", "aa"),
    ("bba", "ab", "ba"),
]

for s, t, expected in test_cases:
    result = min_window_right(s, t)
    status = "PASS" if result == expected else "FAIL"
    print(f"{status}: s='{s}', t='{t}' -> got '{result}', expected '{expected}'")
```

---

## 8. KMP Failure Function Off-by-One

### The Story: The Repeating Song

Imagine you are trying to find a song (pattern) within a long playlist (text). The KMP algorithm's trick is this: if a partial match fails, you do not restart from scratch. You look at what you have already matched and say "the last k characters I matched happen to also be a valid PREFIX of the pattern — so I can restart from position k without re-reading those characters."

The `lps` (Longest Proper Prefix which is also a Suffix) array encodes this: `lps[i]` = the length of the longest proper prefix of `pattern[0..i]` that is also a suffix.

The off-by-one bug: confusing "length" (what lps stores) with "index" (the position to jump to).

### What lps Stores

```python
# lps[i] = length of longest proper prefix of pattern[0..i] that equals a suffix
#
# For pattern = "ABCABD":
#   i=0: "A"      -> no proper prefix is also a suffix -> lps[0] = 0
#   i=1: "AB"     -> prefix "A", suffix "B" -> no match -> lps[1] = 0
#   i=2: "ABC"    -> prefix "A", suffix "C" -> no match -> lps[2] = 0
#   i=3: "ABCA"   -> prefix "A", suffix "A" -> match! length=1 -> lps[3] = 1
#   i=4: "ABCAB"  -> prefix "AB", suffix "AB" -> match! length=2 -> lps[4] = 2
#   i=5: "ABCABD" -> prefix "AB", suffix "BD"? No. "A"=="D"? No -> lps[5] = 0
#
# lps = [0, 0, 0, 1, 2, 0]

pattern = "ABCABD"
print("lps should be [0, 0, 0, 1, 2, 0]")
```

### The WRONG Code: Off-by-One in lps Construction

```python
# WRONG: Common off-by-one bug in KMP lps construction
def build_lps_wrong(pattern):
    m = len(pattern)
    lps = [0] * m
    length = 0   # length of previous longest prefix-suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length]   # BUG: should be lps[length - 1]!
                # We want to fall back to the lps of the PREVIOUS position,
                # not the lps of 'length' itself.
            else:
                lps[i] = 0
                i += 1

    return lps
```

### Trace: The Wrong lps[length] vs lps[length-1]

```
Pattern: "AACAAAB"
Expected lps: [0, 1, 0, 1, 2, 2, 0]

When building at i=5 (pattern[5]='A'):
  length = 2 (from lps[4]=2, meaning pattern[0:2]=="AA" matches pattern[3:5]=="AA")
  pattern[5]='A', pattern[length]=pattern[2]='C'  -> mismatch!

We need to fall back. What do we fall back to?
  We need lps[length - 1] = lps[1] = 1
  (The longest prefix-suffix of "AA" is "A", length 1)

WRONG code uses: length = lps[length] = lps[2] = 0  <- over-falls, too aggressive!
RIGHT code uses: length = lps[length - 1] = lps[1] = 1  <- correct fallback

With wrong code at i=5:
  length becomes 0 (from lps[2])
  pattern[5]='A' == pattern[0]='A' -> length=1, lps[5]=1, i=6

Wrong lps: [0, 1, 0, 1, 2, 1, 0]  <- lps[5] should be 2, not 1!
```

### The RIGHT Code: KMP with Correct lps

```python
# RIGHT: Correct KMP failure function construction
def build_lps_right(pattern):
    """
    lps[i] = length of longest proper prefix of pattern[0..i]
             that is also a suffix of pattern[0..i]
    """
    m = len(pattern)
    lps = [0] * m
    length = 0   # length of current longest matching prefix-suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                # Don't increment i!
                # Fall back to the previous longest prefix-suffix.
                length = lps[length - 1]   # RIGHT: length - 1, not length!
            else:
                lps[i] = 0
                i += 1

    return lps


# Full KMP search using the correct lps
def kmp_search(text, pattern):
    if not pattern:
        return []

    lps = build_lps_right(pattern)
    matches = []

    n, m = len(text), len(pattern)
    i = 0  # index for text
    j = 0  # index for pattern

    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1

        if j == m:
            matches.append(i - j)   # found match at index i-j
            j = lps[j - 1]          # look for more matches
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]      # use lps for smart fallback
            else:
                i += 1

    return matches


# Test
text = "AACAAACAAB"
pattern = "AACAAB"
print(kmp_search(text, pattern))  # [4]

text2 = "AABAACAADAABAABA"
pattern2 = "AABA"
print(kmp_search(text2, pattern2))  # [0, 9, 12]
```

### lps Array Walkthrough (Correct)

```python
def build_lps_with_trace(pattern):
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            print(f"  Match: pattern[{i}]='{pattern[i]}' == pattern[{length-1}]='{pattern[length-1]}' -> lps[{i}]={length}")
            i += 1
        else:
            if length != 0:
                old_length = length
                length = lps[length - 1]
                print(f"  Mismatch: fallback from length={old_length} to lps[{old_length-1}]={length}")
            else:
                lps[i] = 0
                print(f"  Mismatch: no prefix to fall back to, lps[{i}]=0")
                i += 1

    return lps

print("Building lps for 'ABCABD':")
result = build_lps_with_trace("ABCABD")
print("lps =", result)  # [0, 0, 0, 1, 2, 0]
```

### Mini Test Case

```python
# Verify lps is built correctly
test_patterns = [
    ("ABCABD", [0, 0, 0, 1, 2, 0]),
    ("AACAAAB", [0, 1, 0, 1, 2, 2, 0]),
    ("AAAA", [0, 1, 2, 3]),
    ("ABCDE", [0, 0, 0, 0, 0]),
]

for pattern, expected_lps in test_patterns:
    result = build_lps_right(pattern)
    status = "PASS" if result == expected_lps else "FAIL"
    print(f"{status}: '{pattern}' -> lps={result} (expected {expected_lps})")
```

---

## 9. Palindrome Check with Non-Alphanumeric

### The Story: The Strict Librarian and the Lenient Librarian

A strict librarian checks if "A man, a plan, a canal: Panama" is a palindrome. She checks character by character, including commas, spaces, and colons. It clearly is not. A lenient librarian strips out everything that is not a letter or digit, converts to lowercase, and then checks. "amanaplanacanalpanama" — yes, that is a palindrome!

Most palindrome problems on LeetCode want the lenient librarian approach. Forgetting to clean the input is an extremely common bug.

### The WRONG Code

```python
# WRONG: Checking palindrome without cleaning non-alphanumeric characters
def is_palindrome_wrong(s):
    return s == s[::-1]

# Test cases that fail:
print(is_palindrome_wrong("A man, a plan, a canal: Panama"))
# False -- should be True!
# 'A' != 'a', and spaces and punctuation are included

print(is_palindrome_wrong("race a car"))
# False -- correct! But only by luck of the wrong approach.
```

### Visual Trace: Why Cleaning Matters

```
s = "A man, a plan, a canal: Panama"

Without cleaning:
s           = "A man, a plan, a canal: Panama"
reversed(s) = "amanaP :lanac a ,nalp a ,nam A"

s[0]     = 'A'  vs  reversed[0]  = 'a'  -> different (case)!
Result: False

With cleaning (alphanumeric only, lowercase):
cleaned = "amanaplanacanalpanama"
reversed = "amanaplanacanalpanama"
-> EQUAL! It is a palindrome.
```

### The RIGHT Code

```python
# RIGHT: Clean the string before palindrome check
def is_palindrome_right(s):
    # Keep only alphanumeric characters, convert to lowercase
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]

# Test cases
print(is_palindrome_right("A man, a plan, a canal: Panama"))  # True
print(is_palindrome_right("race a car"))                       # False
print(is_palindrome_right("Was it a car or a cat I saw?"))    # True
print(is_palindrome_right(" "))                                # True (empty after clean)


# Two-pointer approach (more space efficient -- O(1) extra space)
def is_palindrome_two_pointer(s):
    left, right = 0, len(s) - 1

    while left < right:
        # Skip non-alphanumeric from left
        while left < right and not s[left].isalnum():
            left += 1
        # Skip non-alphanumeric from right
        while left < right and not s[right].isalnum():
            right -= 1

        # Compare (case insensitive)
        if s[left].lower() != s[right].lower():
            return False

        left += 1
        right -= 1

    return True

print(is_palindrome_two_pointer("A man, a plan, a canal: Panama"))  # True
```

### isalnum() vs isalpha() vs isdigit()

```python
# isalnum(): letters AND digits
print('a'.isalnum())   # True
print('1'.isalnum())   # True
print(' '.isalnum())   # False
print(','.isalnum())   # False
print('é'.isalnum())   # True  -- unicode letters count!

# isalpha(): only letters (no digits)
print('a'.isalpha())   # True
print('1'.isalpha())   # False

# isdigit(): only digits
print('1'.isdigit())   # True
print('a'.isdigit())   # False
print('²'.isdigit())   # True  -- unicode superscript digits!

# For pure ASCII digits, use c in '0123456789' if you want to be strict
```

### Mini Test Case

```python
test_cases = [
    ("A man, a plan, a canal: Panama", True),
    ("race a car", False),
    ("Was it a car or a cat I saw?", True),
    ("0P", False),
    ("", True),
    ("a", True),
    ("Madam I'm Adam", True),
]

for s, expected in test_cases:
    result = is_palindrome_right(s)
    status = "PASS" if result == expected else "FAIL"
    print(f"{status}: '{s[:30]}...' -> {result}")
```

---

## 10. String Comparison is Lexicographic Not Numeric

### The Story: The Phone Book vs the Calculator

A phone book sorts names alphabetically: "10" comes before "9" because "1" comes before "9" in the alphabet. A calculator says 10 > 9 because ten is bigger than nine. These are two fundamentally different ways of ordering, and Python uses the phone book method for strings.

This causes completely wrong sort orders when you have number-strings and forget to convert to integers.

### The WRONG Code

```python
# WRONG: Sorting number-strings lexicographically
numbers = ["10", "9", "2", "100", "21", "3"]

wrong_sorted = sorted(numbers)    # lexicographic sort (default for strings)
print(wrong_sorted)
# ['10', '100', '2', '21', '3', '9']
# 10 and 100 come before 2 because '1' < '2'!


# WRONG: Comparing number-strings
print("10" < "9")    # True  -- lexicographic: '1' < '9'
print("100" < "2")   # True  -- lexicographic: '1' < '2'
print("21" < "3")    # True  -- lexicographic: '2' < '3'
```

### Visual Trace: Lexicographic vs Numeric

```
Lexicographic comparison of "10" vs "9":
  Compare first character: '1' vs '9'
  '1' has ASCII value 49
  '9' has ASCII value 57
  49 < 57, so "10" < "9"  <-- this is "correct" for lexicographic order!

Numeric comparison:
  int("10") = 10
  int("9")  = 9
  10 > 9  <-- this is what we usually want for number sorting


Sorted lexicographically: ["10", "100", "2", "21", "3", "9"]
Sorted numerically:       ["2", "3", "9", "10", "21", "100"]
```

### The RIGHT Code

```python
# RIGHT: Sort number-strings numerically using key=int
numbers = ["10", "9", "2", "100", "21", "3"]

right_sorted = sorted(numbers, key=int)
print(right_sorted)
# ['2', '3', '9', '10', '21', '100']  -- correct numerical order!


# RIGHT: Sort strings by length, not alphabetically
words = ["banana", "kiwi", "fig", "apple", "date"]

by_length = sorted(words, key=len)
print(by_length)
# ['fig', 'kiwi', 'date', 'apple', 'banana'] -- shortest to longest

# Compare by length first, then alphabetically as tiebreaker
by_length_then_alpha = sorted(words, key=lambda w: (len(w), w))
print(by_length_then_alpha)
# ['fig', 'date', 'kiwi', 'apple', 'banana']
```

### Real-World Interview Trap: Largest Number

```python
# Problem: Given a list of numbers, arrange them to form the largest number
# e.g., [3, 30, 34, 5, 9] -> "9534330"

# WRONG: sort numerically
nums = [3, 30, 34, 5, 9]
wrong = ''.join(str(n) for n in sorted(nums, reverse=True))
print(wrong)  # "9534330" -- happens to be right here, but...

nums2 = [3, 30, 34, 5, 9, 300]
wrong2 = ''.join(str(n) for n in sorted(nums2, reverse=True))
print(wrong2)  # "953430300" -- WRONG! Should be "9534330300"
# Because 30 > 300 numerically, but "30" concatenated before "300" gives "30300"
# while "300" before "30" gives "30030". We want "30300" (larger), so 30 should come first!

# RIGHT: Custom comparator
from functools import cmp_to_key

def compare(a, b):
    # Compare ab vs ba (as strings)
    if a + b > b + a:
        return -1  # a should come first
    elif a + b < b + a:
        return 1   # b should come first
    return 0

def largest_number(nums):
    num_strings = [str(n) for n in nums]
    num_strings.sort(key=cmp_to_key(compare))
    result = ''.join(num_strings)
    return '0' if result[0] == '0' else result  # handle all-zeros case

print(largest_number([3, 30, 34, 5, 9]))       # "9534330"
print(largest_number([3, 30, 34, 5, 9, 300]))  # "9534330300" -- but let me verify
```

### Mini Test Case

```python
# Classic error demo
versions = ["1.10.0", "1.9.0", "1.2.0", "1.11.0"]

# WRONG: lexicographic sort
print(sorted(versions))
# ['1.10.0', '1.11.0', '1.2.0', '1.9.0']
# 1.10 before 1.2 because '1' < '2'!

# RIGHT: parse and sort numerically
def version_key(v):
    return tuple(int(x) for x in v.split('.'))

print(sorted(versions, key=version_key))
# ['1.2.0', '1.9.0', '1.10.0', '1.11.0']  -- correct!
```

---

## 11. f-string vs format vs %

### The Story: Three Generations of the Same Family

The `%` operator is grandpa's way: been around since Python 2, works fine, but verbose and limited. `str.format()` is the parent's way: more readable and powerful. `f-strings` are the kid's way: fast, clean, and readable. All three work, but they are not equivalent in readability, speed, or flexibility. Knowing the differences prevents both bugs and slow code.

### The Three Methods

```python
name = "Alice"
score = 95.7
rank = 3

# Method 1: % formatting (old style, Python 2 era)
result1 = "Name: %s, Score: %.1f, Rank: %d" % (name, score, rank)
print(result1)  # "Name: Alice, Score: 95.7, Rank: 3"

# Method 2: str.format() (Python 2.6+)
result2 = "Name: {}, Score: {:.1f}, Rank: {}".format(name, score, rank)
print(result2)  # "Name: Alice, Score: 95.7, Rank: 3"

# Named fields with format()
result3 = "Name: {name}, Score: {score:.1f}, Rank: {rank}".format(
    name=name, score=score, rank=rank
)

# Method 3: f-strings (Python 3.6+, fastest and most readable)
result4 = f"Name: {name}, Score: {score:.1f}, Rank: {rank}"
print(result4)  # "Name: Alice, Score: 95.7, Rank: 3"
```

### Performance Comparison

```python
import timeit

name, score, rank = "Alice", 95.7, 3

# Benchmark each method
percent_time = timeit.timeit(
    lambda: "Name: %s, Score: %.1f, Rank: %d" % (name, score, rank),
    number=1_000_000
)

format_time = timeit.timeit(
    lambda: "Name: {}, Score: {:.1f}, Rank: {}".format(name, score, rank),
    number=1_000_000
)

fstring_time = timeit.timeit(
    lambda: f"Name: {name}, Score: {score:.1f}, Rank: {rank}",
    number=1_000_000
)

print(f"% format:    {percent_time:.3f}s")
print(f".format():   {format_time:.3f}s")
print(f"f-string:    {fstring_time:.3f}s")

# Typical results:
# % format:    0.180s
# .format():   0.200s
# f-string:    0.085s
# f-strings are roughly 2x faster than % and .format()
```

### Common Bugs with % Formatting

```python
# BUG 1: Forgetting the tuple for multiple values
name, age = "Alice", 25
bad = "Name: %s, Age: %d" % name, age    # WRONG: passes only 'name' to %
# TypeError: not all arguments converted during string formatting

good = "Name: %s, Age: %d" % (name, age)  # RIGHT: tuple!


# BUG 2: Single value in tuple -- must use comma
bad2 = "Hello %s" % (name)   # This actually WORKS for strings (single value)
bad3 = "Value: %d" % (42)    # Also works for single int
# But this fails:
bad4 = "Values: %s %s" % ("a")  # TypeError: not enough arguments for format string
good4 = "Values: %s %s" % ("a", "b")  # Right


# BUG 3: Using %s for a dict (common gotcha)
d = {'key': 'value'}
bad5 = "Dict: %s" % d   # TypeError: not enough arguments!
# Python thinks d is the mapping for %(key)s style formatting!

good5 = "Dict: %s" % (d,)    # Need comma to make it a tuple
good5_alt = f"Dict: {d}"     # f-string handles this cleanly
```

### f-String Advanced Features

```python
# f-strings support expressions directly
x = 10
print(f"{x * 2 + 1}")           # "21"
print(f"{x if x > 5 else 0}")   # "10"
print(f"{'hello':>10}")          # "     hello"  (right-aligned in 10 chars)
print(f"{3.14159:.2f}")          # "3.14"
print(f"{1000000:,}")            # "1,000,000"  (comma separator)
print(f"{255:#010b}")            # "0b11111111" (binary with prefix, 10 chars)

# f-string debugging (Python 3.8+)
value = 42
print(f"{value=}")   # "value=42"  -- shows variable name AND value!
```

### When to Use Each

```python
# Use f-strings for:
# - New code (Python 3.6+)
# - Performance-critical formatting
# - Readability when expressions are involved
message = f"Processing {len(items)} items at {rate:.2f}/s"

# Use .format() for:
# - Template strings you define separately from usage
template = "Dear {name}, your score is {score}."
# Later:
letter = template.format(name="Bob", score=88)

# Use % only for:
# - Logging (Python's logging module uses % style for lazy evaluation)
import logging
logging.info("Processing user %s with score %d", user_id, score)
# The % substitution only happens if the log level is active -- saves work!

# NEVER mix styles in the same codebase for consistency.
```

### Mini Test Case

```python
# Show they all produce the same output
pi = 3.14159
digits = 2

p = "Pi to %d digits: %.2f" % (digits, pi)
f_fmt = "Pi to {} digits: {:.2f}".format(digits, pi)
fstr = f"Pi to {digits} digits: {pi:.2f}"

assert p == f_fmt == fstr == "Pi to 2 digits: 3.14"
print(f"All three produce: '{fstr}'")
print("f-strings are fastest and most readable -- prefer them in new code.")
```

---

## Quick Reference: All 11 Mistakes at a Glance

```
#   Mistake                          | Quick Fix
----|----------------------------------|-------------------------------------------------
1   String concat in loop            | Use ''.join(list_of_chars) instead of +=
2   Strings are immutable            | Convert to list, modify, join back
3   split() vs split(' ')            | Use split() for words; split(delim) for CSV
4   Case sensitivity                  | Always .lower() or .upper() before comparison
5   in for substring vs char          | Use find() for safe substring search; not index()
6   ord/chr confusion                 | subtract ord('a') for lowercase, ord('A') for upper
7   Sliding window shrink update      | Update 'have' counter when left pointer removes a char
8   KMP lps off-by-one               | Fallback to lps[length - 1], not lps[length]
9   Palindrome with non-alphanum      | Filter with isalnum() and lower() before checking
10  Lexicographic vs numeric sort     | Use key=int for number-strings, key=version_key for versions
11  f-string vs format vs %           | Use f-strings for new code; % only in logging
```

---

## Final Checklist Before Submitting String Code

```
[ ] Did I use ''.join() instead of += in a loop?
[ ] Did I convert to list before trying to modify a string?
[ ] Did I check whether split() or split(delimiter) is appropriate?
[ ] Did I normalize case before any string comparison?
[ ] Did I use find() instead of index() where the substring might not exist?
[ ] Did I subtract the correct base (ord('a') vs ord('A')) in char mapping?
[ ] Did I update the validity counter when shrinking the sliding window?
[ ] Did I use lps[length - 1] (not lps[length]) in the KMP fallback?
[ ] Did I filter non-alphanumeric before palindrome check?
[ ] Did I use key=int when sorting number-strings?
[ ] Am I using f-strings for clarity and performance?
```
