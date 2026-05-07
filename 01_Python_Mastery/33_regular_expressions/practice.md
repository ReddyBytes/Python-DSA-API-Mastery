# Regular Expressions — Practice

## Quick Index

| # | Chapter | Topic | Difficulty |
|---|---------|-------|------------|
| [Q1](#q1) | Core Functions | re.search vs re.match | 🟢 Basic |
| [Q2](#q2) | Core Functions | re.findall | 🟢 Basic |
| [Q3](#q3) | Core Functions | re.sub replacement | 🟢 Basic |
| [Q4](#q4) | Core Functions | re.split | 🟢 Basic |
| [Q5](#q5) | Core Functions | re.fullmatch validation | 🟢 Basic |
| [Q6](#q6) | Pattern Building | Character classes | 🟢 Basic |
| [Q7](#q7) | Pattern Building | Quantifiers | 🟢 Basic |
| [Q8](#q8) | Pattern Building | Anchors ^ and $ | 🟡 Intermediate |
| [Q9](#q9) | Pattern Building | Escape sequences | 🟢 Basic |
| [Q10](#q10) | Pattern Building | Alternation with pipe | 🟡 Intermediate |
| [Q11](#q11) | Common Patterns | Email validation | 🟡 Intermediate |
| [Q12](#q12) | Common Patterns | Phone number | 🟡 Intermediate |
| [Q13](#q13) | Common Patterns | URL extraction | 🟡 Intermediate |
| [Q14](#q14) | Common Patterns | ISO date | 🟢 Basic |
| [Q15](#q15) | Named Groups | (?P<name>...) extraction | 🟡 Intermediate |
| [Q16](#q16) | Named Groups | group() vs groups() vs groupdict() | 🟡 Intermediate |
| [Q17](#q17) | Named Groups | re.sub with backreference | 🟡 Intermediate |
| [Q18](#q18) | Named Groups | Nested groups | 🟠 Advanced |
| [Q19](#q19) | Lookahead/Lookbehind | Positive lookahead (?=...) | 🟡 Intermediate |
| [Q20](#q20) | Lookahead/Lookbehind | Negative lookahead (?!...) | 🟡 Intermediate |
| [Q21](#q21) | Lookahead/Lookbehind | Positive lookbehind (?<=...) | 🟡 Intermediate |
| [Q22](#q22) | Lookahead/Lookbehind | Combined lookahead + lookbehind | 🟠 Advanced |
| [Q23](#q23) | Flags | re.IGNORECASE | 🟢 Basic |
| [Q24](#q24) | Flags | re.MULTILINE with ^ $ | 🟡 Intermediate |
| [Q25](#q25) | Flags | re.DOTALL for newlines | 🟡 Intermediate |
| [Q26](#q26) | Performance | re.compile() pattern reuse | 🟡 Intermediate |
| [Q27](#q27) | Performance | Catastrophic backtracking | 🟠 Advanced |
| [Q28](#q28) | Performance | Raw strings r"..." | 🟢 Basic |

---

## Chapter 1 — Core Functions

### Q1 · Core Functions — re.search vs re.match 🟢 {#q1}

The string `"Error 404: Page not found"` is a server log fragment. Use both `re.match()` and `re.search()` to find the number `404`. Explain why one returns `None` and the other succeeds.

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details><summary>💡 Hint</summary>re.match() only looks at the beginning of the string — 404 is not at position 0.</details>

<details><summary>✅ Answer</summary>

```python
import re

text = "Error 404: Page not found"

# match() — anchors to START of string, fails here
m = re.match(r"\d+", text)
print(m)   # None — "Error" is not digits

# search() — scans forward until it finds a match
s = re.search(r"\d+", text)
print(s.group())   # '404'
print(s.start())   # 6
```

**Why:** `re.match()` is implicitly anchored to the start like `^`, so it only succeeds if the pattern matches at position 0. `re.search()` scans the entire string.

</details>

---

### Q2 · Core Functions — re.findall 🟢 {#q2}

Extract every dollar amount from the string `"Costs: $9.99, $149.00, and $1,299.99 today"`. Return a list of strings including the dollar sign.

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details><summary>💡 Hint</summary>Use \$ to match a literal dollar sign, then match digits with optional comma separators and decimal part.</details>

<details><summary>✅ Answer</summary>

```python
import re

text = "Costs: $9.99, $149.00, and $1,299.99 today"

amounts = re.findall(r"\$[\d,]+(?:\.\d{2})?", text)
print(amounts)   # ['$9.99', '$149.00', '$1,299.99']
```

**Why:** `\$` matches a literal dollar sign (escaped because `$` is a metacharacter), `[\d,]+` matches digits and commas (for thousands separators), and `(?:\.\d{2})?` optionally matches a decimal portion.

</details>

---

### Q3 · Core Functions — re.sub replacement 🟢 {#q3}

Redact all email addresses in a support ticket log: `"User john@example.com contacted support@helpdesk.org for invoice help"`. Replace each email with `[EMAIL]`.

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details><summary>💡 Hint</summary>Build an email pattern: local-part @ domain . TLD. Use re.sub() with the replacement string "[EMAIL]".</details>

<details><summary>✅ Answer</summary>

```python
import re

log = "User john@example.com contacted support@helpdesk.org for invoice help"

EMAIL = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
redacted = re.sub(EMAIL, "[EMAIL]", log)
print(redacted)
# "User [EMAIL] contacted [EMAIL] for invoice help"
```

**Why:** `re.sub()` replaces every non-overlapping match of the pattern with the replacement string. The email pattern covers the local part, `@`, domain, and TLD.

</details>

---

### Q4 · Core Functions — re.split 🟢 {#q4}

Split the messy log entry `"one,  two;three\t\tfour five"` into clean tokens. The separator can be any combination of commas, semicolons, or whitespace.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details><summary>💡 Hint</summary>Use a character class [,;\s] with + to match one or more of any separator character.</details>

<details><summary>✅ Answer</summary>

```python
import re

text = "one,  two;three\t\tfour five"

parts = re.split(r"[,;\s]+", text)
print(parts)   # ['one', 'two', 'three', 'four', 'five']
```

**Why:** `[,;\s]+` matches one or more of: comma, semicolon, or any whitespace character. The `+` ensures consecutive separators collapse into a single split point.

</details>

---

### Q5 · Core Functions — re.fullmatch validation 🟢 {#q5}

Write a function `is_valid_zip(s)` that returns `True` only if the entire string is a valid US ZIP code — either 5 digits (`12345`) or ZIP+4 format (`12345-6789`). It must reject partial matches like `"123456"`.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details><summary>💡 Hint</summary>re.fullmatch() requires the pattern to match the complete string — no leftover characters allowed.</details>

<details><summary>✅ Answer</summary>

```python
import re

def is_valid_zip(s):
    return bool(re.fullmatch(r"\d{5}(?:-\d{4})?", s))

print(is_valid_zip("12345"))       # True
print(is_valid_zip("12345-6789"))  # True
print(is_valid_zip("123456"))      # False — extra digit
print(is_valid_zip("1234"))        # False — too short
print(is_valid_zip("abcde"))       # False — not digits
```

**Why:** `re.fullmatch()` anchors both ends of the match, so `"123456"` fails even though it contains `"12345"`. `re.search()` or `re.match()` would incorrectly accept it.

</details>

---

## Chapter 2 — Pattern Building Blocks

### Q6 · Pattern Building — Character classes 🟢 {#q6}

Extract all hexadecimal color codes from a CSS string: `"color: #ff5733; background: #abc; border: #FFFFFF; opacity: 0.5;"`. A valid hex color is `#` followed by exactly 3 or 6 hex digits (0–9, a–f, A–F).

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details><summary>💡 Hint</summary>Use [0-9a-fA-F] for a hex digit. The pattern needs to match {3} or {6} digits after #.</details>

<details><summary>✅ Answer</summary>

```python
import re

css = "color: #ff5733; background: #abc; border: #FFFFFF; opacity: 0.5;"

HEX_COLOR = r"#(?:[0-9a-fA-F]{3}){1,2}\b"
colors = re.findall(HEX_COLOR, css)
print(colors)   # ['#ff5733', '#abc', '#FFFFFF']
```

**Why:** `(?:[0-9a-fA-F]{3}){1,2}` matches either 3 hex digits (one repetition) or 6 hex digits (two repetitions). The `\b` word boundary prevents partial matches against longer strings.

</details>

---

### Q7 · Pattern Building — Quantifiers 🟢 {#q7}

Given the text `"<a>link</a> and <img src='x'/> and <div class='main'>content</div>"`, extract every HTML tag (including closing and self-closing tags). Use a non-greedy quantifier so `<div class='main'>` doesn't swallow everything.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details><summary>💡 Hint</summary>Inside angle brackets, use .*? (lazy) to stop at the first closing >. Without ?, greedy .* will match from the first < all the way to the last >.</details>

<details><summary>✅ Answer</summary>

```python
import re

html = "<a>link</a> and <img src='x'/> and <div class='main'>content</div>"

tags = re.findall(r"<.*?>", html)
print(tags)
# ['<a>', '</a>', "<img src='x'/>", "<div class='main'>", '</div>']
```

**Why:** `.*?` is non-greedy — it matches as few characters as possible. Greedy `.*` would match from the first `<` to the very last `>` in the string, returning one giant match.

</details>

---

### Q8 · Pattern Building — Anchors ^ and $ 🟡 {#q8}

A config file has lines like `"  debug = True"` (may have leading spaces) and `"# This is a comment"`. Extract the first word of every non-comment line using `re.MULTILINE`. A non-comment line does not start with `#`.

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details><summary>💡 Hint</summary>With re.MULTILINE, ^ matches at the start of each line. Use a negative lookahead (?!#) to skip comment lines.</details>

<details><summary>✅ Answer</summary>

```python
import re

config = """\
# Server config
host = localhost
  port = 8080
# Database
db_name = myapp
"""

# Match first word on lines that do NOT start with #
words = re.findall(r"^(?!#)\s*(\w+)", config, re.MULTILINE)
print(words)   # ['host', 'port', 'db_name']
```

**Why:** `^` with `re.MULTILINE` anchors to each line start. `(?!#)` skips lines beginning with `#`. `\s*` eats optional indentation, then `(\w+)` captures the first word.

</details>

---

### Q9 · Pattern Building — Escape sequences 🟢 {#q9}

Extract all IP addresses from `"Server: 192.168.1.100, DNS: 8.8.8.8, Loopback: 127.0.0.1"`. The dot in an IP is a literal dot, not the regex "any character" wildcard.

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details><summary>💡 Hint</summary>Escape the dot as \. to match a literal period. Without the escape, . matches any character including letters.</details>

<details><summary>✅ Answer</summary>

```python
import re

text = "Server: 192.168.1.100, DNS: 8.8.8.8, Loopback: 127.0.0.1"

IP = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
ips = re.findall(IP, text)
print(ips)   # ['192.168.1.100', '8.8.8.8', '127.0.0.1']
```

**Why:** `\.` matches a literal dot. `(?:\d{1,3}\.){3}` matches three groups of 1–3 digits followed by a literal dot, then `\d{1,3}` matches the final octet. `\b` prevents partial matches inside longer numbers.

</details>

---

### Q10 · Pattern Building — Alternation with pipe 🟡 {#q10}

Find all log level tokens in `"[INFO] server started [ERROR] auth failed [WARN] high memory [DEBUG] loop tick"`. Only match the exact strings INFO, ERROR, WARN, or DEBUG inside square brackets.

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details><summary>💡 Hint</summary>Use alternation: INFO|ERROR|WARN|DEBUG inside the bracket characters. Wrap alternatives in a non-capturing group if you combine with other patterns.</details>

<details><summary>✅ Answer</summary>

```python
import re

log = "[INFO] server started [ERROR] auth failed [WARN] high memory [DEBUG] loop tick"

levels = re.findall(r"\[(?:INFO|ERROR|WARN|DEBUG)\]", log)
print(levels)   # ['[INFO]', '[ERROR]', '[WARN]', '[DEBUG]']

# To get just the level names without brackets:
names = re.findall(r"\[(INFO|ERROR|WARN|DEBUG)\]", log)
print(names)   # ['INFO', 'ERROR', 'WARN', 'DEBUG']
```

**Why:** `(?:INFO|ERROR|WARN|DEBUG)` is a non-capturing group with alternation. Using a capturing group `(...)` instead makes `re.findall()` return only the captured text rather than the full match.

</details>

---

## Chapter 3 — Common Patterns

### Q11 · Common Patterns — Email validation 🟡 {#q11}

Write a function `is_valid_email(s)` that validates a complete email address string. Test it against: `"user@example.com"` (valid), `"user.name+tag@sub.domain.co.uk"` (valid), `"@nodomain.com"` (invalid), `"noatsign.com"` (invalid).

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details><summary>💡 Hint</summary>The email pattern has three parts: local part [a-zA-Z0-9._%+-]+, then @, then domain with at least one dot and a 2+ char TLD.</details>

<details><summary>✅ Answer</summary>

```python
import re

EMAIL = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

def is_valid_email(s):
    return bool(re.fullmatch(EMAIL, s))

print(is_valid_email("user@example.com"))              # True
print(is_valid_email("user.name+tag@sub.domain.co.uk")) # True
print(is_valid_email("@nodomain.com"))                 # False
print(is_valid_email("noatsign.com"))                  # False
```

**Why:** `re.fullmatch()` ensures the entire string must match. The `[a-zA-Z]{2,}` at the end requires at least a 2-character TLD. Using `re.search()` instead would accept garbage like `"invalid!!user@example.com!!"`.

</details>

---

### Q12 · Common Patterns — Phone number 🟡 {#q12}

Extract all US phone numbers from `"Call us: (800) 555-1212 or 800-555-0199 or +1 800 555 0100"`. All three formats are valid. Return just the matched strings.

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details><summary>💡 Hint</summary>The optional country code is (?:\+1\s?)?. The area code may or may not be in parentheses: \(?\d{3}\)?. Separators between groups can be space, dash, or dot.</details>

<details><summary>✅ Answer</summary>

```python
import re

text = "Call us: (800) 555-1212 or 800-555-0199 or +1 800 555 0100"

PHONE = r"(?:\+1\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
phones = re.findall(PHONE, text)
print(phones)
# ['(800) 555-1212', '800-555-0199', '+1 800 555 0100']
```

**Why:** Each segment of the pattern is optional or flexible: `\(?` matches an optional opening paren, `\)?` matches an optional closing paren, and `[\s.-]?` matches an optional separator between digit groups.

</details>

---

### Q13 · Common Patterns — URL extraction 🟡 {#q13}

Extract all URLs from the string `"Visit https://example.com or http://sub.domain.org/path?q=1 for more. Also see ftp://ignore.me"`. Only extract `http://` and `https://` URLs, not ftp.

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

<details><summary>💡 Hint</summary>Start with https?:// to match both http and https. Then match everything that is not whitespace for the rest of the URL.</details>

<details><summary>✅ Answer</summary>

```python
import re

text = "Visit https://example.com or http://sub.domain.org/path?q=1 for more. Also see ftp://ignore.me"

URL = r"https?://[^\s/$.?#].[^\s]*"
urls = re.findall(URL, text)
print(urls)
# ['https://example.com', 'http://sub.domain.org/path?q=1']
```

**Why:** `https?` matches either `http` or `https` (the `s` is optional). `[^\s]*` matches any non-whitespace characters for the rest of the URL. The pattern starts with `https?://` so it will not match `ftp://`.

</details>

---

### Q14 · Common Patterns — ISO date 🟢 {#q14}

Find all ISO-format dates (`YYYY-MM-DD`) in a document: `"Events on 2024-01-15 and 2024-03-22. Next year: 2025-07-04."`. Also show how to reformat each date as `DD/MM/YYYY` using `re.sub()`.

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

<details><summary>💡 Hint</summary>Use \d{4}-\d{2}-\d{2} to find dates. For reformatting, wrap each segment in a capturing group and use backreferences \3/\2/\1 in the replacement.</details>

<details><summary>✅ Answer</summary>

```python
import re

text = "Events on 2024-01-15 and 2024-03-22. Next year: 2025-07-04."

DATE_ISO = r"\d{4}-\d{2}-\d{2}"

# Find all dates
dates = re.findall(DATE_ISO, text)
print(dates)   # ['2024-01-15', '2024-03-22', '2025-07-04']

# Reformat to DD/MM/YYYY
reformatted = re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", text)
print(reformatted)
# "Events on 15/01/2024 and 22/03/2024. Next year: 04/07/2025."
```

**Why:** Capturing groups `(\d{4})`, `(\d{2})`, `(\d{2})` create backreferences `\1`, `\2`, `\3`. The replacement string `r"\3/\2/\1"` reorders them: day/month/year.

</details>

---

## Chapter 4 — Named Groups and Complex Extraction

### Q15 · Named Groups — (?P<name>...) extraction 🟡 {#q15}

Parse this log line using named groups and extract the date, log level, service name, and message into a dict:

```
"2024-01-15 14:23:45 ERROR [user_service] Failed to authenticate user@example.com: timeout"
```

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

<details><summary>💡 Hint</summary>Use (?P<name>...) for each field. Call m.groupdict() at the end to get all named groups as a dict at once.</details>

<details><summary>✅ Answer</summary>

```python
import re

line = "2024-01-15 14:23:45 ERROR [user_service] Failed to authenticate user@example.com: timeout"

pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>INFO|WARN|ERROR|DEBUG)\s+"
    r"\[(?P<service>[^\]]+)\]\s+"
    r"(?P<message>.+)"
)

m = pattern.search(line)
if m:
    print(m.group("date"))     # 2024-01-15
    print(m.group("level"))    # ERROR
    print(m.group("service"))  # user_service
    print(m.groupdict())
    # {'date': '2024-01-15', 'time': '14:23:45', 'level': 'ERROR',
    #  'service': 'user_service', 'message': 'Failed to authenticate ...'}
```

**Why:** Named groups make the pattern self-documenting and let you access captures by name rather than fragile position numbers. `groupdict()` dumps all named captures into a dict — perfect for building DataFrames or structured records.

</details>

---

### Q16 · Named Groups — group() vs groups() vs groupdict() 🟡 {#q16}

Given the match object from parsing `"2024-01-15"` with the pattern `r"(\d{4})-(\d{2})-(\d{2})"`, demonstrate the difference between `group()`, `group(1)`, `groups()`, and `groupdict()`. Then repeat with named groups.

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

<details><summary>💡 Hint</summary>group() with no args returns the full match. group(1) returns the first capturing group. groups() returns a tuple of all groups. groupdict() only works with named groups.</details>

<details><summary>✅ Answer</summary>

```python
import re

# Positional groups
m = re.search(r"(\d{4})-(\d{2})-(\d{2})", "Event: 2024-01-15")
print(m.group())     # '2024-01-15'  — full match
print(m.group(1))    # '2024'        — group 1
print(m.group(2))    # '01'          — group 2
print(m.groups())    # ('2024', '01', '15')  — all groups as tuple

# Named groups
m2 = re.search(
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})",
    "Event: 2024-01-15"
)
print(m2.group("year"))   # '2024'
print(m2.groups())        # ('2024', '01', '15')  — same as positional
print(m2.groupdict())     # {'year': '2024', 'month': '01', 'day': '15'}
```

**Why:** Named groups are still accessible positionally via `group(1)` or `groups()`. `groupdict()` adds the name-keyed dict on top. Use `groupdict()` when building structured records — it survives pattern refactoring.

</details>

---

### Q17 · Named Groups — re.sub with backreference 🟡 {#q17}

Convert camelCase identifiers to snake_case using `re.sub()`. For example: `"getUserName"` → `"get_user_name"`, `"processPaymentData"` → `"process_payment_data"`.

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

<details><summary>💡 Hint</summary>Find places where a lowercase letter is immediately followed by an uppercase letter. Insert an underscore between them using backreferences \1 and \2 in the replacement.</details>

<details><summary>✅ Answer</summary>

```python
import re

def camel_to_snake(name):
    # Insert underscore before uppercase that follows a lowercase or digit
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return s.lower()

print(camel_to_snake("getUserName"))       # get_user_name
print(camel_to_snake("processPaymentData")) # process_payment_data
print(camel_to_snake("HTTPSConnection"))   # h_t_t_p_s_connection
```

**Why:** The two capturing groups `([a-z0-9])` and `([A-Z])` capture the characters on either side of the transition point. The replacement `r"\1_\2"` re-inserts both characters with an underscore between them.

</details>

---

### Q18 · Named Groups — Nested groups 🟠 {#q18}

Parse a time string `"14:23:45"` with a pattern that captures the full time AND each individual component. Show how both the outer and inner groups appear in `groups()`.

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

<details><summary>💡 Hint</summary>When you nest a group inside another, both groups are captured. group(1) is the outer group, group(2) is the first inner group, and so on. Groups are numbered by their opening parenthesis left-to-right.</details>

<details><summary>✅ Answer</summary>

```python
import re

time_str = "14:23:45"

# Outer group captures full time, inner groups capture each part
m = re.search(r"((\d{2}):(\d{2}):(\d{2}))", time_str)

print(m.group(0))    # '14:23:45'  — full match (same as group())
print(m.group(1))    # '14:23:45'  — outer capturing group
print(m.group(2))    # '14'        — hours
print(m.group(3))    # '23'        — minutes
print(m.group(4))    # '45'        — seconds
print(m.groups())    # ('14:23:45', '14', '23', '45')
```

**Why:** Groups are numbered by the position of their opening `(` from left to right. The outer group `((\d{2}):...)` is group 1, and its nested groups get subsequent numbers. `group(0)` always refers to the entire match.

</details>

---

## Chapter 5 — Lookahead and Lookbehind

### Q19 · Lookahead/Lookbehind — Positive lookahead (?=...) 🟡 {#q19}

Extract just the numeric values (without the unit) from a CSS string: `"font-size: 16px; margin: 8px; opacity: 0.5; padding: 24px;"`. Return only the numbers that are immediately followed by `px`.

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

<details><summary>💡 Hint</summary>A positive lookahead (?=px) asserts that "px" follows but does not include it in the match. So \d+(?=px) matches the digits without consuming the "px".</details>

<details><summary>✅ Answer</summary>

```python
import re

css = "font-size: 16px; margin: 8px; opacity: 0.5; padding: 24px;"

px_values = re.findall(r"\d+(?=px)", css)
print(px_values)   # ['16', '8', '24']
```

**Why:** `(?=px)` is a zero-width assertion — the regex engine checks that `px` follows the match position but does not advance past it. So the match result is just the digits, not `16px`. The `0.5` is not captured because it is not followed by `px`.

</details>

---

### Q20 · Lookahead/Lookbehind — Negative lookahead (?!...) 🟡 {#q20}

In the string `"python3 django flask python2 python"`, find all occurrences of the word `python` that are NOT followed by `2`. Return the matches including any trailing digit that belongs to the match.

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

<details><summary>💡 Hint</summary>Use (?!2) after matching "python" to assert it is NOT followed by "2". Then optionally match a trailing digit with \d? to capture python3 as a unit.</details>

<details><summary>✅ Answer</summary>

```python
import re

text = "python3 django flask python2 python"

modern = re.findall(r"python(?!2)\d?", text)
print(modern)   # ['python3', 'python']
```

**Why:** `(?!2)` is a negative lookahead — it asserts the next character is NOT `2`. So `python2` is skipped entirely. `\d?` then optionally captures a trailing digit, picking up the `3` in `python3`.

</details>

---

### Q21 · Lookahead/Lookbehind — Positive lookbehind (?<=...) 🟡 {#q21}

From the string `"$9.99 €5.00 £12.50 $149.99"`, extract only the dollar amounts as numbers — without the dollar sign — while ignoring euro and pound amounts.

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

<details><summary>💡 Hint</summary>Use (?<=\$) as a lookbehind to assert the number is preceded by a dollar sign, without including the $ in the match result.</details>

<details><summary>✅ Answer</summary>

```python
import re

prices = "$9.99 €5.00 £12.50 $149.99"

dollar_amounts = re.findall(r"(?<=\$)\d+(?:\.\d{2})?", prices)
print(dollar_amounts)   # ['9.99', '149.99']
```

**Why:** `(?<=\$)` is a positive lookbehind — it asserts that a `$` immediately precedes the match position without being part of the match. The result is just the number. `€5.00` and `£12.50` are skipped because they are not preceded by `$`.

</details>

---

### Q22 · Lookahead/Lookbehind — Combined lookahead + lookbehind 🟠 {#q22}

Extract word characters that are surrounded by angle brackets — i.e., the tag name from simple HTML tags like `<div>`, `<span>`, `</p>`. Use lookbehind for `<` (or `</`) and lookahead for `>`.

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

<details><summary>💡 Hint</summary>Lookbehind must have a fixed width in Python's re module. Use (?<=<) for opening tags. For closing tags starting with </, a separate pattern or alternation is needed.</details>

<details><summary>✅ Answer</summary>

```python
import re

html = "<div> <span class='x'> </p> <br/> <article>"

# Extract tag names from both opening and closing tags
# Use a pattern that matches the tag name inside angle brackets
tag_names = re.findall(r"</?(\w+)", html)
print(tag_names)   # ['div', 'span', 'p', 'br', 'article']

# Lookahead/lookbehind approach for simple tags (fixed-width lookbehind only)
# Lookbehind for < (1 char), lookahead for > or space or /
names_via_lookaround = re.findall(r"(?<=<)\w+(?=[>\s/])", html)
print(names_via_lookaround)   # ['div', 'span', 'p', 'br', 'article']
```

**Why:** Python's `re` module requires fixed-width lookbehinds, so `(?<=</)` works (2 chars fixed) but `(?<=<\w+)` does not. When the lookbehind approach gets complex, a simple capturing group inside the tag pattern is often cleaner.

</details>

---

## Chapter 6 — Flags

### Q23 · Flags — re.IGNORECASE 🟢 {#q23}

Count how many times the word `"python"` (in any capitalization: Python, PYTHON, python) appears in: `"Python is great. I love python. PYTHON rocks. PyThOn is powerful."`.

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

<details><summary>💡 Hint</summary>Pass re.IGNORECASE (or re.I) as the third argument to re.findall() to make the pattern case-insensitive.</details>

<details><summary>✅ Answer</summary>

```python
import re

text = "Python is great. I love python. PYTHON rocks. PyThOn is powerful."

matches = re.findall(r"\bpython\b", text, re.IGNORECASE)
print(matches)        # ['Python', 'python', 'PYTHON', 'PyThOn']
print(len(matches))   # 4
```

**Why:** `re.IGNORECASE` (shorthand `re.I`) makes the entire pattern case-insensitive. `\b` ensures only the full word matches — without it, `pythonista` would also match.

</details>

---

### Q24 · Flags — re.MULTILINE with ^ $ 🟡 {#q24}

Extract the first word from every line in a multi-line string — but only lines that start with a letter (skip blank lines and lines starting with `#`).

```python
text = "# comment\nfoo bar baz\n\nhello world\n# skip me\ndata science"
```

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

<details><summary>💡 Hint</summary>With re.MULTILINE, ^ matches the start of each line. Add [a-zA-Z] or a negative lookahead to skip comment lines and blank lines.</details>

<details><summary>✅ Answer</summary>

```python
import re

text = "# comment\nfoo bar baz\n\nhello world\n# skip me\ndata science"

first_words = re.findall(r"^([a-zA-Z]\w*)", text, re.MULTILINE)
print(first_words)   # ['foo', 'hello', 'data']
```

**Why:** `re.MULTILINE` makes `^` match at the start of every line, not just the start of the string. `[a-zA-Z]` as the first character naturally skips `#` comment lines and blank lines (which have no letter at position 0).

</details>

---

### Q25 · Flags — re.DOTALL for newlines 🟡 {#q25}

A multi-line HTML block is stored as a string. Extract the content between `<body>` and `</body>` tags, including any newlines. Without the right flag, `.` will not cross line boundaries.

```python
html = "<html>\n<head><title>Test</title></head>\n<body>\nHello\nWorld\n</body>\n</html>"
```

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

<details><summary>💡 Hint</summary>By default, . does not match newline characters. Use re.DOTALL (re.S) to make . match everything including \n.</details>

<details><summary>✅ Answer</summary>

```python
import re

html = "<html>\n<head><title>Test</title></head>\n<body>\nHello\nWorld\n</body>\n</html>"

# Without re.DOTALL — returns None because . won't cross newlines
without_flag = re.search(r"<body>(.*?)</body>", html)
print(without_flag)   # None

# With re.DOTALL — . matches newlines too
with_flag = re.search(r"<body>(.*?)</body>", html, re.DOTALL)
print(with_flag.group(1))
# '\nHello\nWorld\n'
```

**Why:** The default `.` matches any character except `\n`. `re.DOTALL` (alias `re.S`) removes that exception. Use the non-greedy `.*?` so the match stops at the first `</body>` rather than the last one.

</details>

---

## Chapter 7 — Pre-compiling for Performance

### Q26 · Performance — re.compile() pattern reuse 🟡 {#q26}

You have a list of 1000 log lines and need to extract email addresses from each one. Show the compiled-pattern approach and explain why it is more efficient than calling `re.findall()` with a string pattern in a loop.

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)

<details><summary>💡 Hint</summary>re.compile() returns a Pattern object. Call .findall(), .search(), .sub() directly on that object instead of passing the pattern string each time.</details>

<details><summary>✅ Answer</summary>

```python
import re

EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

log_lines = [
    "Error from user@example.com at 14:23",
    "Payment for admin@company.org processed",
    "No email on this line",
    "Two: a@b.com and c@d.org here",
]

# Compiled pattern — parse once, reuse many times
all_emails = []
for line in log_lines:
    found = EMAIL.findall(line)   # ← method on Pattern object
    all_emails.extend(found)

print(all_emails)
# ['user@example.com', 'admin@company.org', 'a@b.com', 'c@d.org']
```

**Why:** `re.compile()` parses and compiles the pattern string into an internal state machine once. Without it, Python re-parses the pattern string on every call inside the loop. Python does cache recently used patterns internally, but `re.compile()` guarantees caching and makes the intent explicit.

</details>

---

### Q27 · Performance — Catastrophic backtracking 🟠 {#q27}

Explain what catastrophic backtracking is, then demonstrate the problem pattern `(a+)+b` and show a safe alternative. Why does this matter in production?

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)

<details><summary>💡 Hint</summary>The problem: nested quantifiers on the same character class create exponential combinations for the backtracking engine to try. Count how many ways "aaaaac" can be split among the inner a+ groups.</details>

<details><summary>✅ Answer</summary>

```python
import re
import time

# DANGEROUS — do not run on long strings of a's without b
# (a+)+b on "aaaaaac" tries exponentially many splits before failing
dangerous = r"(a+)+b"

# Safe alternative: atomic equivalent or possessive (use regex module)
# With stdlib re: flatten the nested quantifier
safe = r"a+b"   # if you only need to match sequences of a followed by b

# Demonstration on a short string (safe to run)
test = "aaac"   # short enough not to hang

start = time.time()
result = re.search(dangerous, test)
elapsed = time.time() - start
print(f"Dangerous pattern on 'aaac': result={result}, time={elapsed:.4f}s")

# The problem grows exponentially: 'a' * 20 + 'c' would hang the process
# Fix: avoid nested quantifiers on the same class
# Use: a+b  OR  use the third-party `regex` module with atomic groups: (?>a+)+b
```

**Why:** `(a+)+` on a string like `"aaaaaac"` gives the engine 2^n ways to partition the `a`s among the inner `a+` groups. When no `b` follows, each partition is tried and fails, causing exponential backtracking. This can hang a server. Rule: never write `(X+)+`, `(X*)+`, or `(X|Y)+` where `X` and `Y` can match the same characters.

</details>

---

### Q28 · Performance — Raw strings r"..." 🟢 {#q28}

Explain why regex patterns should always be written as raw strings. Show what goes wrong without `r""` using the pattern `\b\w+\b` and the newline pattern `\n`. Then compile a verbose email pattern using `re.VERBOSE` and raw strings together.

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)

<details><summary>💡 Hint</summary>In a normal Python string, \b is a backspace character (ASCII 8), not a word boundary. In a raw string r"\b", backslash is literal so the regex engine sees \b correctly.</details>

<details><summary>✅ Answer</summary>

```python
import re

text = "Hello world foo bar"

# Without raw string — \b is backspace (ASCII 8), not word boundary
without_raw = re.findall("\b\w+\b", text)
print(without_raw)   # [] — pattern is wrong, \b = backspace char

# With raw string — \b is the word boundary metacharacter
with_raw = re.findall(r"\b\w+\b", text)
print(with_raw)   # ['Hello', 'world', 'foo', 'bar']

# \n example — in pattern matching a literal newline vs the \n escape sequence
text2 = "line1\nline2"
# r"\n" in regex matches a literal newline character (same as "\n" here)
# but for patterns like r"\d" vs "\d": \d in non-raw string = just "d" backslash escape
# Always use r"..." to be safe and explicit

# Verbose email pattern with raw string
EMAIL = re.compile(r"""
    [a-zA-Z0-9._%+-]+   # username part
    @                   # at sign
    [a-zA-Z0-9.-]+      # domain name
    \.                  # literal dot
    [a-zA-Z]{2,}        # top-level domain
""", re.VERBOSE)

print(bool(EMAIL.fullmatch("user@example.com")))   # True
```

**Why:** Python processes string escape sequences before the regex engine sees the pattern. `"\b"` becomes a backspace byte (ASCII 8). `r"\b"` keeps the backslash literal, so the regex engine correctly interprets `\b` as a word boundary. Always use `r""` for regex patterns.

</details>

---

## Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| ⬅️ Prev Module | [../32_streamlit_flask/theory.md](../32_streamlit_flask/theory.md) |
| ➡️ Next Module | [../99_interview_master/README.md](../99_interview_master/README.md) |

---

**[🏠 Back to README](../README.md)**
