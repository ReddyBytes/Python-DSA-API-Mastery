# 🔤 Regular Expressions — Cheatsheet

## Core Functions

```python
import re

re.search(pattern, string)      # first match anywhere → match object or None
re.match(pattern, string)       # match at START only → match object or None
re.fullmatch(pattern, string)   # entire string must match → match object or None
re.findall(pattern, string)     # all matches → list of strings (or tuples with groups)
re.finditer(pattern, string)    # all matches → iterator of match objects
re.sub(pattern, repl, string)   # replace all matches → new string
re.split(pattern, string)       # split by pattern → list
re.compile(pattern, flags)      # compile for reuse → Pattern object
```

---

## Match Object Methods

```python
m = re.search(r"\d+", "abc123")
m.group()        # full match string: '123'
m.group(1)       # first capturing group
m.group("name")  # named group
m.groups()       # tuple of all groups
m.groupdict()    # dict of named groups
m.start()        # start index of match
m.end()          # end index
m.span()         # (start, end) tuple
```

---

## Metacharacters

```
.        Any character except newline
^        Start of string (or line with re.MULTILINE)
$        End of string (or line with re.MULTILINE)
\b       Word boundary
\B       Non-word boundary
\A       Absolute start of string
\Z       Absolute end of string
```

---

## Character Classes

```
\d       Digit: [0-9]
\D       Non-digit: [^0-9]
\w       Word: [a-zA-Z0-9_]
\W       Non-word
\s       Whitespace: [ \t\n\r\f\v]
\S       Non-whitespace

[abc]    Any of a, b, c
[^abc]   Any EXCEPT a, b, c
[a-z]    Range: lowercase
[A-Za-z0-9]  Alphanumeric
```

---

## Quantifiers

```
*        0 or more (greedy)
+        1 or more (greedy)
?        0 or 1 (greedy)
{n}      Exactly n
{n,m}    n to m times
{n,}     At least n times
*?       0 or more (lazy/non-greedy)
+?       1 or more (lazy)
??       0 or 1 (lazy)
```

---

## Groups

```
(...)         Capturing group — creates \1 backreference
(?:...)       Non-capturing group — no backreference
(?P<name>...) Named capturing group
\1, \2        Backreference in pattern
\g<name>      Named backreference in sub() replacement
|             Alternation: A|B
```

---

## Lookahead / Lookbehind

```
(?=...)    Positive lookahead  — assert what follows (not consumed)
(?!...)    Negative lookahead  — assert NOT followed by
(?<=...)   Positive lookbehind — assert what precedes (not consumed)
(?<!...)   Negative lookbehind — assert NOT preceded by
```

```python
re.findall(r"\d+(?=px)", "16px 8px 0.5")     # ['16', '8']  (digits before px)
re.findall(r"(?<=\$)\d+\.\d{2}", "$9.99")    # ['9.99']  (digits after $)
re.findall(r"python(?!2)", "python3 python2") # ['python']  (not followed by 2)
```

---

## Flags

```python
re.IGNORECASE  / re.I   # case-insensitive matching
re.MULTILINE   / re.M   # ^ and $ match each line start/end
re.DOTALL      / re.S   # . matches newlines too
re.VERBOSE     / re.X   # allow whitespace and comments in pattern
re.ASCII       / re.A   # \w \d \s match ASCII only

# Combine flags
re.findall(r"^\w+", text, re.MULTILINE | re.IGNORECASE)
```

---

## Common Patterns

```python
EMAIL       = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_US    = r"(?:\+1\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
URL         = r"https?://[^\s/$.?#].[^\s]*"
IP          = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
DATE_ISO    = r"\d{4}-\d{2}-\d{2}"              # 2024-01-15
DATE_US     = r"\d{1,2}/\d{1,2}/\d{2,4}"        # 1/15/2024
TIME_24H    = r"\b([01]?\d|2[0-3]):([0-5]\d)(?::([0-5]\d))?\b"
MONEY       = r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?"
ZIP         = r"\b\d{5}(?:-\d{4})?\b"
HEX_COLOR   = r"#(?:[0-9a-fA-F]{3}){1,2}\b"
CREDIT_CARD = r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
SLUG        = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
```

---

## Named Groups + Structured Extraction

```python
log_pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>INFO|WARN|ERROR|DEBUG)\s+"
    r"\[(?P<service>[^\]]+)\]\s+"
    r"(?P<message>.+)"
)

m = log_pattern.search(line)
if m:
    m.groupdict()   # {'date': '...', 'time': '...', 'level': '...', ...}

# finditer for multiple log lines
entries = [m.groupdict() for m in log_pattern.finditer(log_text)]
```

---

## sub() with Backreferences

```python
# Reformat date: 2024-01-15 → 15/01/2024
re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", "2024-01-15")

# Mask email domain
re.sub(r"(@)[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,})", r"\1***\2", "user@example.com")

# Wrap numbers in brackets
re.sub(r"\b(\d+)\b", r"[\1]", "buy 5 items at 10 dollars")
```

---

## Compiled Pattern (Performance)

```python
# Compile once, reuse many times in loops
pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

for line in lines:
    emails   = pattern.findall(line)
    redacted = pattern.sub("[REDACTED]", line)
```

---

## Quick Pitfalls

| Pitfall | Wrong | Right |
|---|---|---|
| Greedy vs lazy | `<(.*)>` matches `a>b</a` | `<(.*?)>` matches `a` |
| match vs search | `re.match()` only at start | `re.search()` anywhere |
| Missing raw string | `"\n"` = newline in regex | `r"\n"` = literal `\n` |
| `-` in char class | `[a-z0-9-]` can be ambiguous | `[a-z0-9\-]` or `[a-z0-9-]` at end |

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
