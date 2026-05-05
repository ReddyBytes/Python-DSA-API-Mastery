"""
Regular Expressions — Practice Problems
All problems use only stdlib (re module). Run directly with python3.
"""

import re


# ─────────────────────────────────────────────
# PROBLEM 1: Extract structured data from log lines
# ─────────────────────────────────────────────
print("PROBLEM 1: Log Line Parser")

log_text = """
2024-01-15 14:23:45 ERROR [user_service] Failed to authenticate user@example.com: timeout after 3000ms
2024-01-15 14:23:47 INFO  [payment_service] Payment processed: $149.99 for order #ORD-2024-001
2024-01-15 14:23:49 WARN  [cache_service] Cache miss rate: 87% — consider increasing TTL
2024-01-15 14:23:51 DEBUG [auth_service] Token validated for admin@company.org
2024-01-15 14:23:53 ERROR [db_service] Connection pool exhausted: 50/50 connections in use
"""

log_pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>INFO|WARN|ERROR|DEBUG)\s+"
    r"\[(?P<service>[^\]]+)\]\s+"
    r"(?P<message>.+)"
)

entries = [m.groupdict() for m in log_pattern.finditer(log_text)]
print(f"  Parsed {len(entries)} log entries")

errors = [e for e in entries if e["level"] == "ERROR"]
print(f"  ERROR entries: {len(errors)}")
for e in errors:
    print(f"    [{e['service']}] {e['message'][:50]}")

# Extract all emails from log
emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", log_text)
print(f"  Emails found: {emails}")


# ─────────────────────────────────────────────
# PROBLEM 2: Data extraction with groups
# ─────────────────────────────────────────────
print("\nPROBLEM 2: Data Extraction")

text = """
Order #ORD-2024-001: $149.99  (shipped to 10001)
Order #ORD-2024-002: $29.99   (shipped to 90210)
Order #ORD-2024-003: $1,299.00 (shipped to 60601)
Server: 192.168.1.100  Backup: 10.0.0.50
"""

# Extract order IDs
order_ids = re.findall(r"#(ORD-\d{4}-\d{3})", text)
print(f"  Order IDs: {order_ids}")

# Extract prices (dollar amounts)
prices = re.findall(r"\$[\d,]+(?:\.\d{2})?", text)
print(f"  Prices: {prices}")

# Extract ZIP codes
zips = re.findall(r"\b\d{5}\b", text)
print(f"  ZIP codes: {zips}")

# Extract IP addresses
ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)
print(f"  IP addresses: {ips}")


# ─────────────────────────────────────────────
# PROBLEM 3: String transformation with re.sub()
# ─────────────────────────────────────────────
print("\nPROBLEM 3: String Transformation")

# Task 1: Reformat dates from YYYY-MM-DD to DD/MM/YYYY
dates_text = "Events: 2024-01-15, 2024-03-22, 2024-12-01"
reformatted = re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", dates_text)
print(f"  Dates reformatted: {reformatted}")

# Task 2: Redact all email addresses
sensitive = "Contact john@example.com or support@company.org for help"
redacted = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[EMAIL]", sensitive)
print(f"  Redacted: {redacted}")

# Task 3: Normalize whitespace (collapse multiple spaces/tabs/newlines to single space)
messy = "This   has  \t  lots   of \n  whitespace"
clean = re.sub(r"\s+", " ", messy).strip()
print(f"  Cleaned: {clean!r}")

# Task 4: camelCase to snake_case
def camel_to_snake(name):
    # Insert underscore before uppercase letters that follow lowercase
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return s.lower()

names = ["getUserName", "processPaymentData", "HTTPSConnection"]
for name in names:
    print(f"  {name!r} → {camel_to_snake(name)!r}")


# ─────────────────────────────────────────────
# PROBLEM 4: Validation patterns
# ─────────────────────────────────────────────
print("\nPROBLEM 4: Input Validation")

def validate(label, pattern, tests):
    compiled = re.compile(pattern)
    for value, expected in tests:
        result = bool(compiled.fullmatch(value))
        status = "✓" if result == expected else "✗"
        print(f"  {status} {label}: {value!r} → {result} (expected {expected})")

# ZIP code validation
validate("ZIP", r"\d{5}(?:-\d{4})?", [
    ("12345", True),
    ("12345-6789", True),
    ("1234", False),
    ("123456", False),
    ("abcde", False),
])

# Simple password validation: 8+ chars, at least one digit, one uppercase
def valid_password(pwd):
    if not re.search(r"[A-Z]", pwd): return False
    if not re.search(r"\d", pwd): return False
    if len(pwd) < 8: return False
    return True

passwords = [("Secret1!", True), ("secret1!", False), ("SECRET!", False), ("Sec1", False)]
for pwd, expected in passwords:
    result = valid_password(pwd)
    status = "✓" if result == expected else "✗"
    print(f"  {status} Password: {pwd!r} → {result}")


# ─────────────────────────────────────────────
# PROBLEM 5: Lookahead and lookbehind
# ─────────────────────────────────────────────
print("\nPROBLEM 5: Lookahead / Lookbehind")

css = "font-size: 16px; margin: 8px; opacity: 0.5; padding: 24px;"
# Extract only the px values (numbers before "px")
px_vals = re.findall(r"\d+(?=px)", css)
print(f"  px values: {px_vals}")   # ['16', '8', '24']

prices_text = "$9.99 €5.00 £12.50 $149.99"
# Extract only dollar amounts (numbers after $)
dollar_amounts = re.findall(r"(?<=\$)\d+(?:\.\d{2})?", prices_text)
print(f"  Dollar amounts: {dollar_amounts}")   # ['9.99', '149.99']

code = "python3 django flask python2 python"
# Find "python" NOT followed by "2"
modern_python = re.findall(r"python(?!2)\d?", code)
print(f"  Modern python refs: {modern_python}")   # ['python3', 'python']


# ─────────────────────────────────────────────
# PROBLEM 6: Real-world pipeline — parse CSV with quoted fields
# ─────────────────────────────────────────────
print("\nPROBLEM 6: Parse Quoted CSV Line")

def parse_csv_line(line):
    """Handle quoted fields that may contain commas."""
    # Match quoted field (allow commas inside) or unquoted field
    pattern = r'"([^"]*)"|((?:[^,"])+)'
    matches = re.finditer(pattern, line)
    return [m.group(1) if m.group(1) is not None else m.group(2).strip()
            for m in matches]

csv_lines = [
    'Alice,30,"New York, NY",Engineer',
    'Bob,25,London,"Software, Data"',
    '"Jane Doe",28,Berlin,Analyst',
]

for line in csv_lines:
    fields = parse_csv_line(line)
    print(f"  {fields}")


# ─────────────────────────────────────────────
# PROBLEM 7: Tokenizer — split code into tokens
# ─────────────────────────────────────────────
print("\nPROBLEM 7: Simple Expression Tokenizer")

def tokenize(expression):
    """Tokenize a math expression into numbers, operators, and parens."""
    token_pattern = re.compile(
        r"(?P<NUMBER>\d+(?:\.\d+)?)"   # integer or float
        r"|(?P<OP>[+\-*/^])"           # operators
        r"|(?P<PAREN>[()])"            # parentheses
        r"|(?P<WS>\s+)"               # whitespace (to skip)
    )
    tokens = []
    for m in token_pattern.finditer(expression):
        if m.lastgroup != "WS":
            tokens.append((m.lastgroup, m.group()))
    return tokens

expr = "3.14 * (2 + 10) / 4"
tokens = tokenize(expr)
print(f"  Expression: {expr!r}")
print(f"  Tokens: {tokens}")

print("\n✅ Regular expressions practice complete!")
