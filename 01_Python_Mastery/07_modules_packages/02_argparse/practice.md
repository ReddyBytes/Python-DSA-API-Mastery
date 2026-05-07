# 💻 Practice — argparse

> For hints and answers, expand the dropdowns. Work through each problem in `practice_local.py` first.

---

## Quick Index

| Q# | Topic | Difficulty |
|---|---|---|
| Q1 | Minimum parser — positional filename argument | 🟢 Beginner |
| Q2 | Optional flag — store_true and default value | 🟢 Beginner |
| Q3 | Type validation — int, float, invalid input | 🟢 Beginner |
| Q4 | choices= — restricted values with auto error | 🟡 Intermediate |
| Q5 | nargs — one or more filenames | 🟡 Intermediate |
| Q6 | required= — mandatory optional argument | 🟡 Intermediate |
| Q7 | Argument groups — visual organization in --help | 🟡 Intermediate |
| Q8 | Mutually exclusive — --quiet vs --verbose | 🟡 Intermediate |
| Q9 | metavar and dest — display vs attribute name | 🟡 Intermediate |
| Q10 | Subcommands — upload and download sub-parsers | 🟠 Advanced |
| Q11 | Custom type — positive_int with ArgumentTypeError | 🟠 Advanced |
| Q12 | Capstone — complete file converter CLI | 🟠 Advanced |

---

## Q1 🟢 · Minimum Parser — Positional Filename Argument

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

Build an `ArgumentParser` with a single positional argument called `filename`. Parse the list `["data.csv"]` and print `args.filename`.

<details>
<summary>Hint</summary>

Positional arguments are added with just a name string — no `--` prefix. Use `parser.parse_args(["data.csv"])` to test without real `sys.argv`.

</details>

<details>
<summary>Answer</summary>

```python
import argparse

parser = argparse.ArgumentParser(description="Process a file")
parser.add_argument("filename", help="Input file to process")

args = parser.parse_args(["data.csv"])
print(args.filename)   # data.csv
```

Key points:
- `"filename"` (no `--`) is a positional argument — required by default
- `parse_args(["data.csv"])` simulates `python script.py data.csv` without touching `sys.argv`
- The attribute name on `args` matches exactly what you passed to `add_argument`

</details>

---

## Q2 🟢 · Optional Flag — store_true and Default Value

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

Add two optional arguments to a parser:
- `--verbose` flag that stores `True` when present (no value needed)
- `--output` that accepts a value and defaults to `"output.txt"` when not provided

Parse `["--verbose"]` and show both attribute values.

<details>
<summary>Hint</summary>

Use `action="store_true"` for a boolean flag. Use `default=` to set the fallback value when an argument is absent.

</details>

<details>
<summary>Answer</summary>

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("--output", default="output.txt", help="Output file path")

args = parser.parse_args(["--verbose"])
print(args.verbose)   # True
print(args.output)    # output.txt  ← default, since --output was not passed
```

Key points:
- `action="store_true"` means: if the flag is present, set the attribute to `True`; if absent, `False`
- `default=` applies when the argument is not provided at all
- `--output` without `action=` expects a value after it: `--output result.csv`

</details>

---

## Q3 🟢 · Type Validation — int, float, Invalid Input

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

Add `--count` (type `int`) and `--rate` (type `float`) arguments. Show:
1. Successful parse of `["--count", "5", "--rate", "0.75"]`
2. What argparse outputs when you pass `["--count", "abc"]`

<details>
<summary>Hint</summary>

Use `type=int` and `type=float`. For the error case, call `parse_args` inside a `try/except SystemExit` block — argparse calls `sys.exit(2)` on invalid input.

</details>

<details>
<summary>Answer</summary>

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--count", type=int, help="Number of items")
parser.add_argument("--rate", type=float, help="Processing rate")

# Case 1: valid input
args = parser.parse_args(["--count", "5", "--rate", "0.75"])
print(args.count)   # 5    ← int, not "5"
print(args.rate)    # 0.75 ← float, not "0.75"

# Case 2: invalid input — argparse prints an error and exits
# error: argument --count: invalid int value: 'abc'
try:
    parser.parse_args(["--count", "abc"])
except SystemExit:
    pass  # argparse already printed the error message
```

Key points:
- `type=int` means argparse calls `int("5")` for you — no manual conversion needed
- On failure, argparse prints: `error: argument --count: invalid int value: 'abc'` and exits with code 2
- Always use `type=` for numeric args — without it, `args.count` would be the string `"5"`

</details>

---

## Q4 🟡 · choices= — Restricted Values with Auto Error

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

Add a `--format` argument restricted to `['json', 'csv', 'yaml']`. Demonstrate:
1. A valid parse with `["--format", "json"]`
2. The auto-generated error when passing `["--format", "xml"]`

<details>
<summary>Hint</summary>

Pass a list to `choices=`. Argparse checks the value against the list after parsing and generates the error message automatically — you don't write validation code.

</details>

<details>
<summary>Answer</summary>

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--format",
    choices=["json", "csv", "yaml"],
    help="Output format"
)

# Case 1: valid
args = parser.parse_args(["--format", "json"])
print(args.format)   # json

# Case 2: invalid — argparse prints:
# error: argument --format: invalid choice: 'xml' (choose from json, csv, yaml)
try:
    parser.parse_args(["--format", "xml"])
except SystemExit:
    pass
```

Key points:
- `choices=` accepts any iterable; argparse checks membership automatically
- The error message lists all valid choices — zero extra code needed
- Works with `type=` too: `choices=[1, 2, 3]` with `type=int` validates after conversion

</details>

---

## Q5 🟡 · nargs — One or More Filenames

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

Add a `--files` argument that accepts one or more filenames. Parse `["--files", "a.txt", "b.txt", "c.txt"]` and show that `args.files` is a list.

Also show what happens when `--files` is given with no filenames after it.

<details>
<summary>Hint</summary>

Use `nargs='+'`. The `+` means "one or more" — it returns a list and errors if the list would be empty. Use `nargs='*'` if zero values should be allowed.

</details>

<details>
<summary>Answer</summary>

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--files", nargs="+", help="One or more input files")

# Multiple values → list
args = parser.parse_args(["--files", "a.txt", "b.txt", "c.txt"])
print(args.files)   # ['a.txt', 'b.txt', 'c.txt']

# Single value still produces a list
args = parser.parse_args(["--files", "only.txt"])
print(args.files)   # ['only.txt']

# No values after --files → error: expected at least one argument
try:
    parser.parse_args(["--files"])
except SystemExit:
    pass
```

Key points:
- `nargs='+'` always returns a list, even for a single value
- `nargs='*'` would return `[]` instead of erroring on zero values
- The values are consumed greedily until the next flag (starting with `-`) or end of input

</details>

---

## Q6 🟡 · required= — Mandatory Optional Argument

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

Build a parser where `--api-key` is required. Show:
1. Successful parse when `--api-key` is provided
2. The error when it is missing

<details>
<summary>Hint</summary>

Add `required=True` to any `add_argument()` call with a `--` prefix. Note: positional arguments are always required by default — `required=` is only relevant for optional (`--`) arguments.

</details>

<details>
<summary>Answer</summary>

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--api-key", required=True, help="API authentication key")

# Case 1: key provided
args = parser.parse_args(["--api-key", "sk-abc123"])
print(args.api_key)   # sk-abc123  ← note: hyphen → underscore in attribute name

# Case 2: missing → error: the following arguments are required: --api-key
try:
    parser.parse_args([])
except SystemExit:
    pass
```

Key points:
- `required=True` makes an optional-style argument (`--`) mandatory
- Argparse maps `--api-key` to `args.api_key` — hyphens become underscores
- Use `dest="api_key"` explicitly if you want to make this conversion obvious in your code

</details>

---

## Q7 🟡 · Argument Groups — Visual Organization in --help

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

Organize a parser into two named groups: "Input options" (with `filename` and `--encoding`) and "Output options" (with `--format` and `--output`). Print the help to show the grouped output.

<details>
<summary>Hint</summary>

Use `parser.add_argument_group("Group Name")` to create a group, then call `add_argument()` on the group object instead of directly on the parser. The groups appear as labeled sections in `--help`.

</details>

<details>
<summary>Answer</summary>

```python
import argparse

parser = argparse.ArgumentParser(description="File processor")

input_group = parser.add_argument_group("Input options")
input_group.add_argument("filename", help="Input file path")
input_group.add_argument("--encoding", default="utf-8", help="File encoding")

output_group = parser.add_argument_group("Output options")
output_group.add_argument("--format", choices=["json", "csv"], help="Output format")
output_group.add_argument("--output", "-o", help="Output file path")

parser.print_help()
```

Output:
```
usage: script.py [-h] [--encoding ENCODING] [--format {json,csv}] [--output OUTPUT] filename

File processor

options:
  -h, --help            show this help message and exit

Input options:
  filename              Input file path
  --encoding ENCODING   File encoding

Output options:
  --format {json,csv}   Output format
  --output OUTPUT, -o OUTPUT
                        Output file path
```

Key points:
- Groups are purely cosmetic — they do not enforce any constraints
- Arguments in groups are parsed identically to top-level arguments
- For constraints (mutual exclusion), use `add_mutually_exclusive_group()` instead

</details>

---

## Q8 🟡 · Mutually Exclusive — --quiet vs --verbose

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

Build a parser where `--quiet` and `--verbose` cannot both be set. Show the error when both are passed.

<details>
<summary>Hint</summary>

Use `parser.add_mutually_exclusive_group()`, then add both arguments to the group object. Argparse enforces the constraint and generates the error automatically.

</details>

<details>
<summary>Answer</summary>

```python
import argparse

parser = argparse.ArgumentParser()

group = parser.add_mutually_exclusive_group()
group.add_argument("--quiet", action="store_true", help="Suppress output")
group.add_argument("--verbose", action="store_true", help="Show detailed output")

# Valid: only one set
args = parser.parse_args(["--verbose"])
print(args.verbose, args.quiet)   # True False

# Valid: neither set
args = parser.parse_args([])
print(args.verbose, args.quiet)   # False False

# Invalid: both set → error: argument --verbose: not allowed with argument --quiet
try:
    parser.parse_args(["--quiet", "--verbose"])
except SystemExit:
    pass
```

Key points:
- Add `required=True` to the group to force the user to pick exactly one
- The group can contain more than two arguments — any combination of more than one triggers the error
- Arguments added to the group still appear in the main `--help` output (not in a separate section)

</details>

---

## Q9 🟡 · metavar and dest — Display vs Attribute Name

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

Add a `--output` argument where:
- The help text shows `FILE` as the placeholder (not `OUTPUT`)
- The attribute on `args` is `output_file` (not `output`)

<details>
<summary>Hint</summary>

Use `metavar='FILE'` to control the placeholder shown in `--help`. Use `dest='output_file'` to control the attribute name on the returned `Namespace`.

</details>

<details>
<summary>Answer</summary>

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--output",
    metavar="FILE",
    dest="output_file",
    help="Write results to FILE"
)

args = parser.parse_args(["--output", "result.json"])
print(args.output_file)   # result.json  ← dest= controls attribute name

# --help shows:
#   --output FILE   Write results to FILE
# (not "--output OUTPUT" which would be the default)
```

Key points:
- `metavar=` only affects the display in `--help` — it has no effect on parsing
- `dest=` renames the attribute on the `Namespace` object returned by `parse_args()`
- Without `dest=`, argparse derives the attribute name from the flag: `--output` → `args.output`, `--api-key` → `args.api_key`

</details>

---

## Q10 🟠 · Subcommands — upload and download Sub-parsers

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

Build a parser with two subcommands:
- `upload <file>` — positional `file` argument
- `download <url> --output <path>` — positional `url` and optional `--output`

Parse both `["upload", "data.csv"]` and `["download", "https://example.com/data", "--output", "local.csv"]`. Show `args.command` and the subcommand-specific attributes.

<details>
<summary>Hint</summary>

Use `parser.add_subparsers(dest="command")` to create the subparser registry. Then call `add_parser("upload")` and `add_parser("download")` on it. Each returns its own parser where you add arguments normally.

</details>

<details>
<summary>Answer</summary>

```python
import argparse

parser = argparse.ArgumentParser(description="File transfer tool")
subparsers = parser.add_subparsers(dest="command", required=True)

# upload subcommand
upload_parser = subparsers.add_parser("upload", help="Upload a file")
upload_parser.add_argument("file", help="File to upload")

# download subcommand
download_parser = subparsers.add_parser("download", help="Download a file")
download_parser.add_argument("url", help="URL to download from")
download_parser.add_argument("--output", default="downloaded_file", help="Save path")

# Parse upload
args = parser.parse_args(["upload", "data.csv"])
print(args.command)   # upload
print(args.file)      # data.csv

# Parse download
args = parser.parse_args(["download", "https://example.com/data", "--output", "local.csv"])
print(args.command)   # download
print(args.url)       # https://example.com/data
print(args.output)    # local.csv
```

Key points:
- `dest="command"` stores the name of the chosen subcommand on `args.command`
- `required=True` ensures an error if no subcommand is given (Python 3.7+)
- Each subparser is fully independent — `args.file` only exists when `command == "upload"`
- Dispatch with `if args.command == "upload": ...` to route execution

</details>

---

## Q11 🟠 · Custom Type — positive_int with ArgumentTypeError

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

Write a custom type function `positive_int` that:
- Converts the string to an integer
- Raises `argparse.ArgumentTypeError` if the value is 0 or negative

Register it as `type=positive_int` on a `--workers` argument. Show the clean error message vs what happens if you raise `ValueError` instead.

<details>
<summary>Hint</summary>

The `type=` function receives a raw string and must return the converted value or raise `argparse.ArgumentTypeError(message)`. Raising `ValueError` works but produces a less readable error — argparse wraps it in a generic "invalid value" message.

</details>

<details>
<summary>Answer</summary>

```python
import argparse


def positive_int(value: str) -> int:
    """Convert string to int and reject non-positive values."""
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not an integer")
    if n <= 0:
        raise argparse.ArgumentTypeError(f"{n} must be a positive integer (got {n})")
    return n


parser = argparse.ArgumentParser()
parser.add_argument("--workers", type=positive_int, default=1, help="Number of workers")

# Valid
args = parser.parse_args(["--workers", "4"])
print(args.workers)   # 4  ← int

# Zero or negative → clean error:
# error: argument --workers: 0 must be a positive integer (got 0)
try:
    parser.parse_args(["--workers", "0"])
except SystemExit:
    pass

# Non-integer → clean error:
# error: argument --workers: 'abc' is not an integer
try:
    parser.parse_args(["--workers", "abc"])
except SystemExit:
    pass
```

Key points:
- `argparse.ArgumentTypeError` produces: `error: argument --workers: <your message>`
- Raising `ValueError` produces: `error: argument --workers: invalid positive_int value: 'abc'` — less informative
- Custom type functions compose well: `type=positive_int` replaces both the `type=int` and a separate validation step

</details>

---

## Q12 🟠 · Capstone — Complete File Converter CLI

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

Build a CLI for a file converter tool with all of the following:
- Positional `source` argument (the file to convert)
- `--format` restricted to `['json', 'csv', 'parquet']`, required
- `--output-dir` optional, defaults to `"."`
- `--dry-run` flag (store_true)
- `--verbose` flag (store_true)
- Organized into "Conversion options" and "Execution options" argument groups
- A meaningful `description` and `epilog` example

Parse `["data.csv", "--format", "json", "--output-dir", "/tmp", "--verbose"]` and print all attributes.

<details>
<summary>Hint</summary>

Combine `add_argument_group()` for organization, `choices=` for format restriction, `required=True` on `--format`, `action="store_true"` for flags, and `default="."` for the output directory. Put the positional `source` in the input group.

</details>

<details>
<summary>Answer</summary>

```python
import argparse

parser = argparse.ArgumentParser(
    description="Convert data files between formats.",
    epilog="Example: converter.py data.csv --format json --output-dir /tmp",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

# Input group
input_group = parser.add_argument_group("Input")
input_group.add_argument("source", help="Source file to convert")

# Conversion options group
conv_group = parser.add_argument_group("Conversion options")
conv_group.add_argument(
    "--format",
    choices=["json", "csv", "parquet"],
    required=True,
    help="Target output format"
)
conv_group.add_argument(
    "--output-dir",
    default=".",
    metavar="DIR",
    dest="output_dir",
    help="Directory to write converted file (default: current directory)"
)

# Execution options group
exec_group = parser.add_argument_group("Execution options")
exec_group.add_argument(
    "--dry-run",
    action="store_true",
    help="Show what would be done without writing any files"
)
exec_group.add_argument(
    "--verbose",
    action="store_true",
    help="Print detailed progress information"
)

args = parser.parse_args([
    "data.csv",
    "--format", "json",
    "--output-dir", "/tmp",
    "--verbose"
])

print(f"source:     {args.source}")       # data.csv
print(f"format:     {args.format}")       # json
print(f"output_dir: {args.output_dir}")   # /tmp
print(f"dry_run:    {args.dry_run}")      # False
print(f"verbose:    {args.verbose}")      # True
```

This pattern — groups for organization, `required=` on key optional args, `dest=` to normalize hyphenated names, `metavar=` for clean help output — is the standard structure for production CLI tools built with argparse.

</details>

---

## 🔁 Navigation

| | |
|---|---|
| ⬅️ Back to Module | [07_modules_packages/theory.md](../theory.md) |
| 📖 Theory | [theory.md](./theory.md) |
| 💻 Practice Local | [practice_local.py](./practice_local.py) |
| ⬅️ Prev Subfolder | [01_sys_module ←](../01_sys_module/practice.md) |
| ➡️ Next Subfolder | [03_subprocess →](../03_subprocess/practice.md) |
