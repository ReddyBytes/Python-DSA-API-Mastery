# 🔤 Regular Expressions in Python

---

You have a text file with 10,000 log lines. Some look like this:
```
2024-01-15 14:23:45 ERROR [user_service] Failed to authenticate user@example.com: timeout after 3000ms
2024-01-15 14:23:47 INFO  [payment_service] Payment processed: $149.99 for order #ORD-2024-001
```

You need to extract: every timestamp, every email address, every dollar amount, every order ID, and every service name. These patterns are structured but not uniform.

You could write dozens of string split operations, index calculations, and conditional checks. Or you could write one pattern per concept, in a language designed for exactly this kind of text matching. That language is regular expressions.

**Regular expressions** (regex) are patterns that describe sets of strings. They're the universal tool for parsing, extracting, and transforming text.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`re.search()` · `re.findall()` · `re.sub()` · Character classes `[...]` · Quantifiers `+`, `*`, `?`, `{n,m}` · Groups `(...)` · Anchors `^`, `$`

**Should Learn** — Important for real projects, comes up regularly:
Named groups `(?P<name>...)` · Non-capturing groups `(?:...)` · Lookahead `(?=...)` / lookbehind `(?<=...)` · Flags (`re.IGNORECASE`, `re.MULTILINE`) · Compiled patterns `re.compile()`

**Good to Know** — Useful in specific situations:
Non-greedy quantifiers `+?`, `*?` · `re.fullmatch()` · `re.split()` · `re.DOTALL` · Backreferences `\1`

**Reference** — Know it exists, look up when needed:
Atomic groups · Possessive quantifiers · `regex` module (third-party, more features) · POSIX character classes

---

## 1️⃣ The Core Functions

```python
import re

text = "The price is $99.99 for item #A123. Contact: user@example.com"

# search — find first match anywhere in string
match = re.search(r"\$[\d.]+", text)
if match:
    print(match.group())    # $99.99
    print(match.start())    # start position
    print(match.end())      # end position
    print(match.span())     # (start, end) tuple

# findall — return list of all matches
emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
print(emails)    # ['user@example.com']

# finditer — iterator of match objects (memory efficient for large text)
for m in re.finditer(r"\b[A-Z]\d{3}\b", text):
    print(m.group(), "at position", m.start())

# sub — replace matches
clean = re.sub(r"\$[\d.]+", "[PRICE]", text)
print(clean)   # "The price is [PRICE] for item #A123. Contact: user@example.com"

# sub with backreference
text2 = "2024-01-15"
reformatted = re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", text2)
print(reformatted)   # 15/01/2024

# split
parts = re.split(r"[,;\s]+", "one, two;three  four")
print(parts)   # ['one', 'two', 'three', 'four']

# fullmatch — pattern must match the entire string
valid = re.fullmatch(r"\d{5}", "12345")    # ZIP code validation
invalid = re.fullmatch(r"\d{5}", "1234")   # None — doesn't match fully
```

---

## 2️⃣ Pattern Building Blocks

```
METACHARACTERS
.        Any character except newline
^        Start of string (or line with re.MULTILINE)
$        End of string (or line with re.MULTILINE)
\b       Word boundary (between \w and \W)
\B       Non-word boundary

CHARACTER CLASSES
\d       Digit: [0-9]
\D       Non-digit: [^0-9]
\w       Word character: [a-zA-Z0-9_]
\W       Non-word character
\s       Whitespace: [ \t\n\r\f\v]
\S       Non-whitespace
[abc]    Any of a, b, c
[^abc]   Any except a, b, c
[a-z]    Range: lowercase letters
[A-Za-z0-9] Alphanumeric

QUANTIFIERS
*        0 or more (greedy)
+        1 or more (greedy)
?        0 or 1 (greedy)
{n}      Exactly n times
{n,m}    Between n and m times
{n,}     At least n times
*?       0 or more (non-greedy/lazy)
+?       1 or more (non-greedy)

GROUPS
(...)         Capturing group
(?:...)       Non-capturing group (doesn't create a \1 backreference)
(?P<name>...) Named capturing group
\1, \2        Backreference to group 1, 2
|             Alternation: A|B (match A or B)
```

---

## 3️⃣ Common Patterns

```python
import re

# Email address
EMAIL = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# Phone number (US)
PHONE = r"(?:\+1\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"

# URL
URL = r"https?://[^\s/$.?#].[^\s]*"

# IP address
IP = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"

# Date formats
DATE_ISO = r"\d{4}-\d{2}-\d{2}"                     # 2024-01-15
DATE_US  = r"\d{1,2}/\d{1,2}/\d{2,4}"               # 1/15/2024 or 01/15/24

# Time
TIME_24H = r"\b([01]?\d|2[0-3]):([0-5]\d)(?::([0-5]\d))?\b"   # 14:23:45

# Credit card (basic)
CREDIT_CARD = r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"

# ZIP code (US)
ZIP = r"\b\d{5}(?:-\d{4})?\b"

# Currency amount
MONEY = r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?"

# Hex color
HEX_COLOR = r"#(?:[0-9a-fA-F]{3}){1,2}\b"

# HTML tag (basic)
HTML_TAG = r"</?[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?\s*/?>"
```

---

## 4️⃣ Named Groups and Complex Extraction

```python
import re

log_line = "2024-01-15 14:23:45 ERROR [user_service] Failed to auth user@example.com: timeout after 3000ms"

# Named groups for structured extraction
pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>INFO|WARN|ERROR|DEBUG)\s+"
    r"\[(?P<service>[^\]]+)\]\s+"
    r"(?P<message>.+)"
)

match = pattern.search(log_line)
if match:
    print(match.group("date"))     # 2024-01-15
    print(match.group("level"))    # ERROR
    print(match.group("service"))  # user_service
    print(match.groupdict())       # dict of all named groups

# Extract all log entries
log_text = """
2024-01-15 14:23:45 ERROR [user_service] auth failed
2024-01-15 14:23:47 INFO  [payment_service] payment ok
2024-01-15 14:23:49 WARN  [cache_service] cache miss
"""

entries = []
for m in pattern.finditer(log_text):
    entries.append(m.groupdict())

import pandas as pd
df = pd.DataFrame(entries)
print(df)
```

---

## 5️⃣ Lookahead and Lookbehind

```python
import re

# Lookahead (?=...) — assert what follows without consuming
# Find numbers followed by "px"
text = "font-size: 16px; margin: 8px; opacity: 0.5;"
px_values = re.findall(r"\d+(?=px)", text)
print(px_values)   # ['16', '8']

# Lookbehind (?<=...) — assert what precedes without consuming
# Find numbers after "$"
prices = "$9.99 and $19.99 and €5.00"
dollar_amounts = re.findall(r"(?<=\$)\d+(?:\.\d{2})?", prices)
print(dollar_amounts)   # ['9.99', '19.99'] (not the €5)

# Negative lookahead (?!...) — not followed by
# Find "python" NOT followed by "2"
text = "python3 is better than python2"
modern = re.findall(r"python(?!2)\d?", text)
print(modern)   # ['python3']
```

---

## 6️⃣ Flags

```python
import re

text = "Hello World\nhello python"

# IGNORECASE (re.I)
re.findall(r"hello", text, re.IGNORECASE)   # ['Hello', 'hello']

# MULTILINE (re.M) — ^ and $ match each line start/end
re.findall(r"^\w+", text, re.MULTILINE)     # ['Hello', 'hello']

# DOTALL (re.S) — . matches newlines too
re.search(r"World.+hello", text, re.DOTALL).group()   # 'World\nhello'

# VERBOSE (re.X) — allow whitespace and comments in pattern
email_pattern = re.compile(r"""
    [a-zA-Z0-9._%+-]+   # username
    @                    # at sign
    [a-zA-Z0-9.-]+      # domain name
    \.                   # dot
    [a-zA-Z]{2,}        # TLD
""", re.VERBOSE)

# Combine flags
re.findall(r"^\w+", text, re.MULTILINE | re.IGNORECASE)
```

---

## 7️⃣ Pre-compiling for Performance

```python
import re

# compile() caches the compiled pattern — use when calling many times
pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# These are now faster in loops
for line in lines:
    match = pattern.search(line)
    emails = pattern.findall(line)
    clean  = pattern.sub("[REDACTED]", line)
```

---

## Common Mistakes to Avoid ⚠️

- **Greedy vs lazy**: `.*` is greedy — it matches as much as possible. `<(.*)>` on `<a>text</a>` matches `a>text</a`, not `a`. Use `<(.*?)>` (non-greedy) to match `a`.
- **Forgetting to escape in character classes**: inside `[...]`, most metacharacters lose their special meaning, but `-` means range unless it's first or last: `[0-9]` is digits, `[0\-9]` is literal 0, -, 9.
- **Using `match` when you want `search`**: `re.match()` only matches at the START of the string. `re.search()` matches anywhere. Forgetting this is a common bug.
- **Not using raw strings**: `\n` in a regex string means newline. `r"\n"` means the literal pattern `\n` (backslash-n). Always use `r"..."` for regex patterns.
- **Catastrophic backtracking**: patterns like `(a+)+b` on long strings of 'a's without 'b' can take exponential time. Test performance on pathological inputs.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Prev Module | [../32_streamlit_flask/theory.md](../32_streamlit_flask/theory.md) |
| ➡️ Next Module | [../99_interview_master/README.md](../99_interview_master/README.md) |

---

**[🏠 Back to README](../README.md)**
