# Practice — 03 Strings

> 🟢 Basic · 🟡 Intermediate · 🟠 Advanced

---

## Quick Index

| # | Concept | Difficulty |
|---|---------|------------|
| [Q1](#q1) | string-immutability-explain | 🟢 Basic |
| [Q2](#q2) | build-string-join-vs-concat | 🟢 Basic |
| [Q3](#q3) | reverse-string | 🟢 Basic |
| [Q4](#q4) | count-vowels | 🟢 Basic |
| [Q5](#q5) | first-non-repeating-char | 🟢 Basic |
| [Q6](#q6) | split-join-strip | 🟢 Basic |
| [Q7](#q7) | char-frequency-array | 🟢 Basic |
| [Q8](#q8) | caesar-cipher | 🟢 Basic |
| [Q9](#q9) | palindrome-two-pointer | 🟡 Intermediate |
| [Q10](#q10) | palindrome-with-nonalnum | 🟡 Intermediate |
| [Q11](#q11) | anagram-detection-counter | 🟡 Intermediate |
| [Q12](#q12) | anagram-detection-freq-array | 🟡 Intermediate |
| [Q13](#q13) | group-anagrams | 🟡 Intermediate |
| [Q14](#q14) | longest-no-repeat-substring | 🟡 Intermediate |
| [Q15](#q15) | minimum-window-substring | 🟡 Intermediate |
| [Q16](#q16) | string-compression | 🟡 Intermediate |
| [Q17](#q17) | valid-palindrome-ii | 🟡 Intermediate |
| [Q18](#q18) | word-frequency-counter | 🟡 Intermediate |
| [Q19](#q19) | find-all-anagrams-in-string | 🟡 Intermediate |
| [Q20](#q20) | string-comparison-sort | 🟡 Intermediate |
| [Q21](#q21) | longest-common-prefix | 🟡 Intermediate |
| [Q22](#q22) | kmp-lps-build | 🟠 Advanced |
| [Q23](#q23) | kmp-full-search | 🟠 Advanced |
| [Q24](#q24) | longest-palindromic-substring | 🟠 Advanced |
| [Q25](#q25) | minimum-window-hard-variant | 🟠 Advanced |

---

<a id="q1"></a>
### Q1 · string-immutability-explain — Why can't you modify `s[0]`? 🟢

```python
s = "hello"
s[0] = "H"   # what happens and why?
```

What does Python do? Why was this design decision made? What is the correct way
to capitalize the first character?

<details>
<summary>Hint</summary>
Strings are immutable — convert to a list, modify, then join back.
</details>

<details>
<summary>Answer</summary>

```python
s = "hello"
# s[0] = "H"  # ← TypeError: 'str' does not support item assignment

# Correct approach A — list + join
chars = list(s)       # ← mutable copy
chars[0] = "H"
result = "".join(chars)

# Correct approach B — slicing
result = "H" + s[1:]  # ← new string, O(n)

# Correct approach C — built-in
result = s.capitalize()
print(result)  # "Hello"
```

**Why:** Strings are **immutable** by design. Immutability enables hashing
(strings can be dict keys), safe interning (Python may reuse the same object
for identical strings), and thread safety. Any "modification" creates a brand
new string.

Time: O(n) · Space: O(n)
</details>

---

<a id="q2"></a>
### Q2 · build-string-join-vs-concat — Build a string from a list of chars 🟢

Given a list of characters, build a single string. Show the O(n²) approach,
explain why it is slow, and write the O(n) approach.

```python
chars = ["h", "e", "l", "l", "o"]
# expected output: "hello"
```

<details>
<summary>Hint</summary>
Every `+=` on a string creates a new string — collect items in a list and call `"".join()` once.
</details>

<details>
<summary>Answer</summary>

```python
chars = ["h", "e", "l", "l", "o"]

# SLOW — O(n²) because each += copies the whole string so far
result = ""
for c in chars:
    result += c   # ← new string object every iteration

# FAST — O(n): collect into list, join once
result = "".join(chars)   # ← single allocation
print(result)  # "hello"
```

**Why:** Strings are immutable. `result += c` is `result = result + c`, which
allocates a brand-new string and copies every character seen so far. For n
characters the total work is 1 + 2 + ... + n = O(n²). `"".join()` scans the
list once to compute the total length, allocates exactly the right memory, and
fills it in — O(n).

Time: O(n²) for `+=` loop · O(n) for `join` · Space: O(n)
</details>

---

<a id="q3"></a>
### Q3 · reverse-string — Reverse a string in-place (no extra string) 🟢

Write a function that reverses a string. The interviewer asks for two
approaches: one using Python slicing, one using two pointers on a list
(simulating "in-place").

```python
reverse_string("abcde")  # "edcba"
reverse_string("hello")  # "olleh"
```

<details>
<summary>Hint</summary>
Slice `s[::-1]` creates a reversed copy; for the two-pointer version convert to list, swap, then join.
</details>

<details>
<summary>Answer</summary>

```python
def reverse_string_slice(s: str) -> str:
    return s[::-1]   # ← pythonic, O(n) time and space

def reverse_string_two_pointer(s: str) -> str:
    chars = list(s)              # ← mutable copy
    left, right = 0, len(chars) - 1
    while left < right:
        chars[left], chars[right] = chars[right], chars[left]  # ← swap
        left += 1
        right -= 1
    return "".join(chars)

print(reverse_string_slice("hello"))           # "olleh"
print(reverse_string_two_pointer("abcde"))     # "edcba"
```

**Why:** The slice approach is idiomatic Python. The two-pointer approach
demonstrates O(1) "extra" space thinking (we only create the list to simulate
mutability — in a language with mutable strings like C, no extra space is needed).

Time: O(n) · Space: O(n) both (because strings are immutable in Python)
</details>

---

<a id="q4"></a>
### Q4 · count-vowels — Count vowels in a string 🟢

```python
count_vowels("hello world")  # 3
count_vowels("aeiou")        # 5
count_vowels("rhythm")       # 0
```

<details>
<summary>Hint</summary>
Check each character against the string `"aeiou"` using the `in` operator.
</details>

<details>
<summary>Answer</summary>

```python
def count_vowels(s: str) -> int:
    vowels = "aeiou"
    return sum(1 for c in s.lower() if c in vowels)  # ← normalize case first

print(count_vowels("hello world"))  # 3
print(count_vowels("AEIOU"))        # 5  (case handled by .lower())
```

**Why:** `c in vowels` is O(1) because `vowels` has only 5 characters — it
is effectively constant-time lookup. Calling `.lower()` once normalises
case so uppercase vowels count too.

Time: O(n) · Space: O(1)
</details>

---

<a id="q5"></a>
### Q5 · first-non-repeating-char — Find the first non-repeating character 🟢

```python
first_non_repeating("leetcode")     # "l"
first_non_repeating("loveleetcode") # "v"
first_non_repeating("aabb")         # "" (none found)
```

<details>
<summary>Hint</summary>
Two-pass: first build a frequency map, then scan left-to-right for count == 1.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter

def first_non_repeating(s: str) -> str:
    freq = Counter(s)                   # ← O(n) pass 1: count frequencies
    for c in s:                         # ← O(n) pass 2: find first with count 1
        if freq[c] == 1:
            return c
    return ""

print(first_non_repeating("leetcode"))      # "l"
print(first_non_repeating("loveleetcode"))  # "v"
print(first_non_repeating("aabb"))          # ""
```

**Why:** The **two-pass** approach is the classic pattern for this problem.
First pass builds the frequency map in O(n). Second pass scans in original
order — this guarantees we return the *first* non-repeating character, not
just any one.

Time: O(n) · Space: O(1) (at most 26 lowercase letters in the counter)
</details>

---

<a id="q6"></a>
### Q6 · split-join-strip — Know your string methods 🟢

What does each of the following print? Explain why.

```python
s = "  hello   world  "
print(s.split())
print(s.split(" "))
print("  trim me  ".strip())
print("-".join(["a", "b", "c"]))
print("hello".replace("l", "L"))
```

<details>
<summary>Hint</summary>
`split()` with no argument collapses all whitespace; `split(" ")` splits on every single space character.
</details>

<details>
<summary>Answer</summary>

```python
s = "  hello   world  "
print(s.split())        # ['hello', 'world']         ← strips and collapses whitespace
print(s.split(" "))     # ['', '', 'hello', '', '', 'world', '', '']  ← splits on every space
print("  trim me  ".strip())    # "trim me"           ← removes leading/trailing whitespace
print("-".join(["a", "b", "c"])) # "a-b-c"           ← separator goes BETWEEN items
print("hello".replace("l", "L")) # "heLLo"            ← replaces all occurrences, new string
```

**Why:** `split()` with no argument is "smart" — it treats any run of whitespace
as one delimiter and never produces empty strings. `split(" ")` is "dumb" — one
space = one cut. Use the no-arg form for word tokenisation; use `split(delim)`
when the delimiter is meaningful (e.g., CSV).

Time: O(n) for all operations · Space: O(n)
</details>

---

<a id="q7"></a>
### Q7 · char-frequency-array — Build a frequency array for lowercase letters 🟢

```python
char_freq("hello")   # {'h':1, 'e':1, 'l':2, 'o':1}
# Also show the 26-element array approach using ord().
```

<details>
<summary>Hint</summary>
`ord(c) - ord('a')` maps 'a'→0, 'b'→1, ..., 'z'→25. Always subtract `ord('a')` for lowercase input.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter

def char_freq_dict(s: str) -> dict:
    return dict(Counter(s))   # ← clean and readable

def char_freq_array(s: str) -> list:
    freq = [0] * 26
    for c in s.lower():
        if c.isalpha():
            freq[ord(c) - ord('a')] += 1   # ← 'a'=0, 'b'=1, ..., 'z'=25
    return freq

print(char_freq_dict("hello"))        # {'h':1, 'e':1, 'l':2, 'o':1}
arr = char_freq_array("hello")
print(arr[ord('l') - ord('a')])       # 2  ← count of 'l'
```

**Why:** The array approach is O(1) space (fixed 26 slots) and is faster
in practice for anagram / frequency comparisons because comparing two
26-element lists is cheaper than comparing two dicts. The common bug is using
`ord('A')` instead of `ord('a')` for lowercase input — that gives indices
32–57 which are out of range for a 26-element array.

Time: O(n) · Space: O(1) (26 fixed)
</details>

---

<a id="q8"></a>
### Q8 · caesar-cipher — Shift every letter by k positions 🟢

```python
caesar("hello", 3)   # "khoor"
caesar("khoor", -3)  # "hello"
caesar("Hello, World!", 13)  # "Uryyb, Jbeyq!"
```

Non-letter characters must be passed through unchanged.

<details>
<summary>Hint</summary>
Use `ord(c) - ord('a')`, add the shift, wrap with `% 26`, then `chr(result + ord('a'))`. Handle upper and lower separately.
</details>

<details>
<summary>Answer</summary>

```python
def caesar(text: str, shift: int) -> str:
    result = []
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')   # ← correct base
            shifted = (ord(c) - base + shift) % 26          # ← wrap with modulo
            result.append(chr(base + shifted))
        else:
            result.append(c)   # ← pass non-letters through unchanged
    return "".join(result)     # ← build string once at the end

print(caesar("hello", 3))           # "khoor"
print(caesar("Hello, World!", 13))  # "Uryyb, Jbeyq!"
```

**Why:** `% 26` handles both positive and negative shifts (Python modulo
is always non-negative). Using separate `base` values for upper and lower
letters keeps the two alphabets independent. Building the result as a list
and joining once is the standard O(n) string-building pattern.

Time: O(n) · Space: O(n)
</details>

---

<a id="q9"></a>
### Q9 · palindrome-two-pointer — Check if a string is a palindrome 🟡

Use the two-pointer approach. Do not use slicing.

```python
is_palindrome("racecar")  # True
is_palindrome("hello")    # False
is_palindrome("a")        # True
is_palindrome("")         # True
```

<details>
<summary>Hint</summary>
Place `left=0` and `right=len(s)-1`. Move inward while `s[left] == s[right]`; return False on first mismatch.
</details>

<details>
<summary>Answer</summary>

```python
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:   # ← mismatch: not a palindrome
            return False
        left += 1
        right -= 1
    return True   # ← all pairs matched

print(is_palindrome("racecar"))   # True
print(is_palindrome("hello"))     # False
print(is_palindrome(""))          # True
```

**Why:** Two pointers avoids creating a reversed copy. The slice approach
`s == s[::-1]` is O(n) time but also O(n) space. Two pointers are O(n) time
and O(1) space — interviewers prefer this because it shows you understand
memory.

Time: O(n) · Space: O(1)
</details>

---

<a id="q10"></a>
### Q10 · palindrome-with-nonalnum — Valid palindrome ignoring punctuation 🟡

LeetCode 125. A string is a valid palindrome if, after keeping only
alphanumeric characters and lowercasing, it reads the same forwards and
backwards.

```python
valid_palindrome("A man, a plan, a canal: Panama")  # True
valid_palindrome("race a car")                       # False
valid_palindrome(" ")                                # True
```

<details>
<summary>Hint</summary>
Use `isalnum()` to filter, `lower()` to normalise, then apply the two-pointer approach — no extra string needed.
</details>

<details>
<summary>Answer</summary>

```python
def valid_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():   # ← skip non-alnum from left
            left += 1
        while left < right and not s[right].isalnum():  # ← skip non-alnum from right
            right -= 1
        if s[left].lower() != s[right].lower():          # ← compare case-insensitive
            return False
        left += 1
        right -= 1
    return True

print(valid_palindrome("A man, a plan, a canal: Panama"))  # True
print(valid_palindrome("race a car"))                       # False
```

**Why:** Skipping non-alphanumeric in-place keeps space O(1). The alternative
— building a cleaned string first with `''.join(c.lower() for c in s if c.isalnum())`
— is also correct but uses O(n) extra space. The in-place two-pointer approach
is preferred in interviews.

Time: O(n) · Space: O(1)
</details>

---

<a id="q11"></a>
### Q11 · anagram-detection-counter — Are two strings anagrams? 🟡

```python
is_anagram("listen", "silent")   # True
is_anagram("hello", "world")     # False
is_anagram("Listen", "Silent")   # True  (case-insensitive)
is_anagram("rat", "car")         # False
```

<details>
<summary>Hint</summary>
Normalize case first, then compare `Counter` objects or sorted strings.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter

def is_anagram(s: str, t: str) -> bool:
    return Counter(s.lower()) == Counter(t.lower())  # ← normalize + compare

# Alternative without Counter — O(n log n) via sorting
def is_anagram_sort(s: str, t: str) -> bool:
    return sorted(s.lower()) == sorted(t.lower())

print(is_anagram("listen", "silent"))   # True
print(is_anagram("Listen", "Silent"))   # True
print(is_anagram("hello", "world"))     # False
```

**Why:** Two strings are anagrams if and only if they have identical character
frequencies. `Counter` builds that frequency map in O(n). Sorting also works
but is O(n log n). The Counter approach is preferred for large strings.

Time: O(n) · Space: O(1) (at most 26 lowercase letters)
</details>

---

<a id="q12"></a>
### Q12 · anagram-detection-freq-array — Anagram check without Counter 🟡

Implement anagram detection using a 26-element frequency array. No imports.

```python
is_anagram_array("listen", "silent")  # True
is_anagram_array("ab", "a")           # False  (different lengths)
```

<details>
<summary>Hint</summary>
Increment for characters in `s`, decrement for characters in `t`. If any element is non-zero at the end, not an anagram.
</details>

<details>
<summary>Answer</summary>

```python
def is_anagram_array(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    freq = [0] * 26
    for a, b in zip(s.lower(), t.lower()):
        freq[ord(a) - ord('a')] += 1   # ← count up for s
        freq[ord(b) - ord('a')] -= 1   # ← count down for t
    return all(f == 0 for f in freq)   # ← all zeros = perfect match

print(is_anagram_array("listen", "silent"))  # True
print(is_anagram_array("ab", "a"))           # False
```

**Why:** By incrementing for one string and decrementing for the other in
the same pass, we avoid two separate loops. The `zip` stops at the shorter
string — but the length check at the top already guards that.

Time: O(n) · Space: O(1)
</details>

---

<a id="q13"></a>
### Q13 · group-anagrams — Group a list of words by their anagram family 🟡

```python
group_anagrams(["eat","tea","tan","ate","nat","bat"])
# [["eat","tea","ate"], ["tan","nat"], ["bat"]]  (order within groups can vary)
```

<details>
<summary>Hint</summary>
Use sorted characters as a dictionary key — all anagrams will produce the same sorted key.
</details>

<details>
<summary>Answer</summary>

```python
from collections import defaultdict

def group_anagrams(words: list) -> list:
    groups = defaultdict(list)
    for w in words:
        key = "".join(sorted(w.lower()))   # ← canonical form: sorted chars
        groups[key].append(w)
    return list(groups.values())

result = group_anagrams(["eat","tea","tan","ate","nat","bat"])
for group in sorted(result, key=len, reverse=True):
    print(group)
# ['eat', 'tea', 'ate']
# ['tan', 'nat']
# ['bat']
```

**Why:** Sorting the characters of a word gives its **canonical form**. All
anagrams of a word produce the same canonical form, so they naturally map to
the same dictionary key. Sorting each word costs O(k log k) where k is its
length; for n words the total is O(n * k log k).

Time: O(n * k log k) where k = average word length · Space: O(n * k)
</details>

---

<a id="q14"></a>
### Q14 · longest-no-repeat-substring — Sliding window, no repeats 🟡

LeetCode 3. Find the length of the longest substring without repeating characters.

```python
length_of_longest(s="abcabcbb")  # 3  ("abc")
length_of_longest(s="bbbbb")     # 1  ("b")
length_of_longest(s="pwwkew")    # 3  ("wke")
```

<details>
<summary>Hint</summary>
Use a dict `{char: last_seen_index}`. When a repeat is found, jump `left` to `seen[c] + 1` — but only if `seen[c] >= left`.
</details>

<details>
<summary>Answer</summary>

```python
def length_of_longest(s: str) -> int:
    seen = {}          # ← char → last seen index
    left = 0
    max_len = 0

    for right, c in enumerate(s):
        if c in seen and seen[c] >= left:   # ← repeat inside current window
            left = seen[c] + 1              # ← jump left past the repeat
        seen[c] = right                     # ← update last seen position
        max_len = max(max_len, right - left + 1)

    return max_len

print(length_of_longest("abcabcbb"))  # 3
print(length_of_longest("bbbbb"))     # 1
print(length_of_longest("pwwkew"))    # 3
```

**Why:** The `seen[c] >= left` guard is critical — without it, a character
seen before the window's current left boundary would incorrectly shrink
the window. Using the dict instead of a set lets us jump `left` directly
to `seen[c] + 1`, avoiding character-by-character shrinking.

Time: O(n) · Space: O(min(n, alphabet_size))
</details>

---

<a id="q15"></a>
### Q15 · minimum-window-substring — Cover all chars of t in s 🟡

LeetCode 76. Find the minimum window in `s` that contains all characters of `t`.

```python
min_window("ADOBECODEBANC", "ABC")  # "BANC"
min_window("a", "a")                # "a"
min_window("a", "aa")               # ""
```

<details>
<summary>Hint</summary>
Track `have` (satisfied char counts) and `need` (required char counts). Shrink from left whenever `have == len(need_distinct)`. When shrinking, decrement `have` if the removed character drops below its required count.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter

def min_window(s: str, t: str) -> str:
    if not s or not t:
        return ""

    need = Counter(t)           # ← required frequencies
    window = {}                 # ← current window frequencies
    have = 0                    # ← distinct chars whose count is satisfied
    total_needed = len(need)    # ← how many distinct chars we must satisfy

    result = ""
    min_len = float("inf")
    left = 0

    for right, c in enumerate(s):
        window[c] = window.get(c, 0) + 1
        if c in need and window[c] == need[c]:
            have += 1                           # ← one more char satisfied

        while have == total_needed:             # ← valid window: try to shrink
            if right - left + 1 < min_len:
                min_len = right - left + 1
                result = s[left:right + 1]
            lc = s[left]
            window[lc] -= 1
            if lc in need and window[lc] < need[lc]:
                have -= 1                       # ← CRITICAL: update after removing
            left += 1

    return result

print(min_window("ADOBECODEBANC", "ABC"))  # "BANC"
```

**Why:** The common bug is forgetting to decrement `have` when the left
pointer removes a character that drops its count below the required value.
This is the shrink-update mistake from `common_mistakes.md`.

Time: O(n + m) · Space: O(m) where m = len(t)
</details>

---

<a id="q16"></a>
### Q16 · string-compression — Run-length encode a string 🟡

```python
compress("aabcccccaaa")  # "a2b1c5a3"
compress("abcd")         # "abcd"  (compressed is not shorter — return original)
compress("aabb")         # "aabb"  (a2b2 is same length — return original)
```

<details>
<summary>Hint</summary>
Walk through the string tracking the current character and its run count. Use a list to build the result, join once at the end.
</details>

<details>
<summary>Answer</summary>

```python
def compress(s: str) -> str:
    if not s:
        return s

    parts = []              # ← collect pieces, join once
    count = 1

    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            parts.append(s[i - 1] + str(count))  # ← flush previous run
            count = 1
    parts.append(s[-1] + str(count))              # ← flush last run

    compressed = "".join(parts)
    return compressed if len(compressed) < len(s) else s

print(compress("aabcccccaaa"))  # "a2b1c5a3"
print(compress("abcd"))         # "abcd"
```

**Why:** Building via list + join avoids O(n²) string concatenation. The
comparison at the end is a common requirement: return the original if compression
does not save space.

Time: O(n) · Space: O(n)
</details>

---

<a id="q17"></a>
### Q17 · valid-palindrome-ii — Palindrome with at most one deletion 🟡

LeetCode 680. Given a string, return True if it can be a palindrome after
deleting at most one character.

```python
valid_palindrome_ii("aba")     # True
valid_palindrome_ii("abca")    # True  (remove 'c')
valid_palindrome_ii("abc")     # False
```

<details>
<summary>Hint</summary>
Two pointers from both ends. On first mismatch, try skipping the left character OR skipping the right character — if either remaining substring is a palindrome, return True.
</details>

<details>
<summary>Answer</summary>

```python
def valid_palindrome_ii(s: str) -> bool:

    def is_pal(left: int, right: int) -> bool:
        while left < right:
            if s[left] != s[right]:
                return False
            left += 1
            right -= 1
        return True

    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            # ← try skipping left char or right char
            return is_pal(left + 1, right) or is_pal(left, right - 1)
        left += 1
        right -= 1
    return True

print(valid_palindrome_ii("abca"))   # True
print(valid_palindrome_ii("abc"))    # False
```

**Why:** We only need to make one deletion decision. On the first mismatch,
one of the two characters must be the one to delete — try both and see if
the remaining window is a palindrome.

Time: O(n) · Space: O(1)
</details>

---

<a id="q18"></a>
### Q18 · word-frequency-counter — Count word frequencies 🟡

```python
word_freq("to be or not to be")
# {'to': 2, 'be': 2, 'or': 1, 'not': 1}
```

Handle mixed case and ignore punctuation.

<details>
<summary>Hint</summary>
`split()` tokenises on whitespace; strip punctuation with `strip(".,!?")` or `isalpha()` filtering.
</details>

<details>
<summary>Answer</summary>

```python
import re
from collections import Counter

def word_freq(text: str) -> dict:
    # Remove punctuation, lowercase, split on whitespace
    words = re.findall(r"[a-z]+", text.lower())  # ← clean tokenisation
    return dict(Counter(words))

def word_freq_manual(text: str) -> dict:
    freq = {}
    for word in text.lower().split():
        word = word.strip(".,!?;:")    # ← strip common punctuation
        if word:
            freq[word] = freq.get(word, 0) + 1
    return freq

print(word_freq("To be, or not to be!"))
# {'to': 2, 'be': 2, 'or': 1, 'not': 1}
```

**Why:** Use `split()` (no argument) — it handles multiple spaces and
leading/trailing whitespace cleanly. Always lowercase before counting to
avoid treating "To" and "to" as different words.

Time: O(n) · Space: O(unique words)
</details>

---

<a id="q19"></a>
### Q19 · find-all-anagrams-in-string — Sliding window anagram search 🟡

LeetCode 438. Find all start indices in string `s` where an anagram of
string `p` begins.

```python
find_anagrams("cbaebabacd", "abc")  # [0, 6]
find_anagrams("abab", "ab")         # [0, 1, 2]
```

<details>
<summary>Hint</summary>
Use a fixed-size window of length `len(p)`. Maintain a frequency counter for the window; slide one character at a time.
</details>

<details>
<summary>Answer</summary>

```python
from collections import Counter

def find_anagrams(s: str, p: str) -> list:
    result = []
    need = Counter(p)         # ← target frequencies
    window = Counter(s[:len(p)])  # ← initial window
    k = len(p)

    if window == need:
        result.append(0)

    for i in range(k, len(s)):
        # Add new right character
        window[s[i]] += 1
        # Remove outgoing left character
        old = s[i - k]
        window[old] -= 1
        if window[old] == 0:
            del window[old]  # ← keep counter clean
        if window == need:
            result.append(i - k + 1)

    return result

print(find_anagrams("cbaebabacd", "abc"))  # [0, 6]
print(find_anagrams("abab", "ab"))         # [0, 1, 2]
```

**Why:** A fixed-size sliding window means we do O(1) work per step — one
add, one remove. Comparing two Counter objects of size at most 26 is O(1).
The naive approach (compute Counter for every window) is O(n * m).

Time: O(n) · Space: O(1) (counters bounded by alphabet size)
</details>

---

<a id="q20"></a>
### Q20 · string-comparison-sort — Sort strings and numbers correctly 🟡

```python
sort_numerically(["10", "9", "2", "100", "21"])
# ["2", "9", "10", "21", "100"]

sort_versions(["1.10.0", "1.9.0", "1.2.0", "1.11.0"])
# ["1.2.0", "1.9.0", "1.10.0", "1.11.0"]
```

<details>
<summary>Hint</summary>
Use `key=int` for number-strings; parse each component as int for version strings.
</details>

<details>
<summary>Answer</summary>

```python
def sort_numerically(strings: list) -> list:
    return sorted(strings, key=int)   # ← key=int converts before comparing

def sort_versions(versions: list) -> list:
    def version_key(v: str):
        return tuple(int(x) for x in v.split("."))   # ← compare component by component
    return sorted(versions, key=version_key)

print(sort_numerically(["10", "9", "2", "100", "21"]))
# ['2', '9', '10', '21', '100']

print(sort_versions(["1.10.0", "1.9.0", "1.2.0", "1.11.0"]))
# ['1.2.0', '1.9.0', '1.10.0', '1.11.0']
```

**Why:** Default string sort is **lexicographic** — "10" < "9" because '1' < '9'.
Number-strings need `key=int`. Version strings need per-component int parsing
because "1.10" > "1.9" numerically but "1.10" < "1.9" lexicographically.

Time: O(n log n) · Space: O(n)
</details>

---

<a id="q21"></a>
### Q21 · longest-common-prefix — Find the longest common prefix 🟡

```python
longest_common_prefix(["flower","flow","flight"])   # "fl"
longest_common_prefix(["dog","racecar","car"])       # ""
longest_common_prefix(["abc"])                        # "abc"
```

<details>
<summary>Hint</summary>
Vertical scan: compare character by character across all strings at the same index position.
</details>

<details>
<summary>Answer</summary>

```python
def longest_common_prefix(words: list) -> str:
    if not words:
        return ""
    # Use the first word as reference
    for i, c in enumerate(words[0]):
        for word in words[1:]:
            if i >= len(word) or word[i] != c:   # ← mismatch or word too short
                return words[0][:i]
    return words[0]   # ← all chars matched

# Alternative: sort and compare first/last
def longest_common_prefix_sort(words: list) -> str:
    words = sorted(words)
    first, last = words[0], words[-1]
    i = 0
    while i < len(first) and i < len(last) and first[i] == last[i]:
        i += 1
    return first[:i]

print(longest_common_prefix(["flower","flow","flight"]))  # "fl"
print(longest_common_prefix(["dog","racecar","car"]))     # ""
```

**Why:** Vertical scan stops as soon as a mismatch is found — no extra
memory needed. The sort-based approach is elegant: the lexicographically
smallest and largest words in a sorted list bracket all others, so their
common prefix is the answer.

Time: O(n * m) where m = shortest word length · Space: O(1)
</details>

---

<a id="q22"></a>
### Q22 · kmp-lps-build — Build the KMP failure (LPS) array 🟠

Given a pattern string, build its **LPS array** (Longest Proper Prefix
which is also a Suffix). This is the preprocessing step in KMP.

```python
build_lps("ABCABD")   # [0, 0, 0, 1, 2, 0]
build_lps("AAAA")     # [0, 1, 2, 3]
build_lps("ABCDE")    # [0, 0, 0, 0, 0]
build_lps("AACAAAB")  # [0, 1, 0, 1, 2, 2, 0]
```

<details>
<summary>Hint</summary>
Maintain `length` = the length of the current longest matching prefix-suffix. On mismatch fall back to `lps[length - 1]` (NOT `lps[length]` — that is the classic off-by-one bug).
</details>

<details>
<summary>Answer</summary>

```python
def build_lps(pattern: str) -> list:
    m = len(pattern)
    lps = [0] * m
    length = 0   # ← length of current longest matching prefix-suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]   # ← FALL BACK: lps[length-1] not lps[length]!
                # do NOT increment i here
            else:
                lps[i] = 0
                i += 1

    return lps

print(build_lps("ABCABD"))   # [0, 0, 0, 1, 2, 0]
print(build_lps("AAAA"))     # [0, 1, 2, 3]
print(build_lps("AACAAAB"))  # [0, 1, 0, 1, 2, 2, 0]
```

**Why:** The fall-back `lps[length - 1]` is the subtlest part of KMP. When
`pattern[i] != pattern[length]` we cannot restart at 0 — we still have a
partial prefix match of length `lps[length - 1]`. Using `lps[length]` instead
skips one position too far and produces wrong LPS values.

Time: O(m) · Space: O(m)
</details>

---

<a id="q23"></a>
### Q23 · kmp-full-search — Full KMP pattern search 🟠

Use the LPS array to search for all occurrences of `pattern` inside `text`.

```python
kmp_search("AABABAB", "ABAB")          # [1, 3]
kmp_search("AABAACAADAABAABA", "AABA") # [0, 9, 12]
kmp_search("hello", "ll")              # [2]
kmp_search("aaaa", "aa")               # [0, 1, 2]
```

<details>
<summary>Hint</summary>
After a full match at position `i - len(pattern)`, set `j = lps[j - 1]` to continue searching (overlapping matches count).
</details>

<details>
<summary>Answer</summary>

```python
def build_lps(pattern: str) -> list:
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length:
            length = lps[length - 1]   # ← correct fallback
        else:
            lps[i] = 0
            i += 1
    return lps

def kmp_search(text: str, pattern: str) -> list:
    if not pattern:
        return []
    lps = build_lps(pattern)
    matches = []
    j = 0   # ← index into pattern

    for i, c in enumerate(text):   # ← index into text
        while j > 0 and c != pattern[j]:
            j = lps[j - 1]          # ← smart fallback, not restart from 0
        if c == pattern[j]:
            j += 1
        if j == len(pattern):
            matches.append(i - j + 1)   # ← match starts here
            j = lps[j - 1]              # ← look for more (overlapping) matches

    return matches

print(kmp_search("AABAACAADAABAABA", "AABA"))  # [0, 9, 12]
print(kmp_search("aaaa", "aa"))                 # [0, 1, 2]
```

**Why:** KMP avoids O(nm) by never re-examining characters in the text.
When a mismatch occurs after j matches, `lps[j-1]` tells us the next
valid alignment — we have already matched `lps[j-1]` characters implicitly.

Time: O(n + m) · Space: O(m)
</details>

---

<a id="q24"></a>
### Q24 · longest-palindromic-substring — Expand around center 🟠

LeetCode 5. Find the longest palindromic substring.

```python
longest_palindrome("babad")   # "bab" or "aba"
longest_palindrome("cbbd")    # "bb"
longest_palindrome("a")       # "a"
longest_palindrome("racecar") # "racecar"
```

<details>
<summary>Hint</summary>
For each index, expand outward treating it as the center of both an odd-length palindrome and an even-length palindrome. Track the best start/end seen.
</details>

<details>
<summary>Answer</summary>

```python
def longest_palindrome(s: str) -> str:

    def expand(left: int, right: int) -> tuple:
        """Expand around center while chars match."""
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - 1   # ← last valid positions

    best_start, best_end = 0, 0

    for i in range(len(s)):
        # Odd-length palindromes: center is s[i]
        l, r = expand(i, i)
        if r - l > best_end - best_start:
            best_start, best_end = l, r

        # Even-length palindromes: center is between s[i] and s[i+1]
        l, r = expand(i, i + 1)
        if r - l > best_end - best_start:
            best_start, best_end = l, r

    return s[best_start:best_end + 1]

print(longest_palindrome("babad"))    # "bab"
print(longest_palindrome("cbbd"))     # "bb"
print(longest_palindrome("racecar"))  # "racecar"
```

**Why:** Each center expansion is O(n) in the worst case; with n centers
the total is O(n²). Manacher's algorithm achieves O(n) but is rarely
expected in interviews. The expand-around-center approach is the expected
answer at most levels.

Time: O(n²) · Space: O(1)
</details>

---

<a id="q25"></a>
### Q25 · minimum-window-hard-variant — Window with at most k distinct chars 🟠

Find the length of the longest substring with at most `k` distinct characters.

```python
longest_k_distinct("eceba", k=2)   # 3  ("ece")
longest_k_distinct("aa", k=1)      # 2  ("aa")
longest_k_distinct("aabacbebebe", k=3)  # 7  ("cbebebe")
```

<details>
<summary>Hint</summary>
Expand right freely; when `len(window) > k`, shrink from the left until `len(window) == k`. Track maximum window size.
</details>

<details>
<summary>Answer</summary>

```python
def longest_k_distinct(s: str, k: int) -> int:
    if k == 0:
        return 0

    window = {}   # ← char → frequency in current window
    left = 0
    max_len = 0

    for right, c in enumerate(s):
        window[c] = window.get(c, 0) + 1      # ← expand right

        while len(window) > k:                  # ← too many distinct chars
            lc = s[left]
            window[lc] -= 1
            if window[lc] == 0:
                del window[lc]                  # ← remove from window map
            left += 1

        max_len = max(max_len, right - left + 1)

    return max_len

print(longest_k_distinct("eceba", 2))         # 3
print(longest_k_distinct("aa", 1))            # 2
print(longest_k_distinct("aabacbebebe", 3))   # 7
```

**Why:** This is the variable-size sliding window template. The window is
valid as long as `len(window) <= k`. When we exceed k distinct characters,
we shrink from the left one step at a time, removing characters from the
map and deleting their key when their count drops to zero.

Time: O(n) · Space: O(k)
</details>

---

## Navigation

**[Back to README](../README.md)**

**Prev:** [← Interview Q&A](./interview.md) &nbsp;|&nbsp; **Next:** [Recursion — Theory →](../04_recursion/theory.md)

**Related Topics:** [Theory](./theory.md) · [Visual Explanation](./visual_explanation.md) · [Cheat Sheet](./cheetsheet.md) · [Real World Usage](./real_world_usage.md) · [Common Mistakes](./common_mistakes.md) · [Interview Q&A](./interview.md)
