# 🎯 Query and Eval — Readable Filters for Large DataFrames

> Writing `df[df["age"] > 30 & df["score"] >= 90]` in a 20-condition filter is like programming in parenthesis soup. `df.query()` lets you write it like a sentence instead.

As filter conditions grow more complex, boolean indexing becomes hard to read and easy to break. `df[(df['age'] > 30) & (df['city'] == 'NYC') & (df['score'] >= 90)]` is valid Python but terrible for readability and maintenance. **`df.query()`** lets you write the same filter as a plain English string. Beyond readability, for DataFrames with hundreds of thousands of rows, `query()` and `eval()` use the `numexpr` engine under the hood — avoiding intermediate arrays and delivering measurable speed improvements on large-scale filtering and column computation.

---

## df.query() — English-Style Row Filtering

**`df.query()`** accepts a filter expression as a plain string. The column names become variables — no `df["column"]` noise, no nested brackets, just logic.

```python
import pandas as pd

df = pd.DataFrame({
    "age": [25, 34, 45, 28],
    "score": [88, 92, 76, 95],
    "status": ["active", "inactive", "active", "active"],
})

# Standard boolean indexing (hard to read at scale)
result = df[(df["age"] > 30) & (df["score"] >= 90) & (df["status"] == "active")]

# Equivalent with query (reads like a sentence)
result = df.query("age > 30 and score >= 90 and status == 'active'")

# Comparison operators all work: >, <, >=, <=, ==, !=
# Logical operators: and, or, not (NOT & | ~ — those are Python bitwise)

# in / not in operators
result = df.query("status in ['active', 'pending']")
result = df.query("status not in ['banned', 'deleted']")
```

---

## Using Variables with @ — Injecting Python Values

The **`@` prefix** inside a query string refers to a Python variable from the surrounding scope. This makes queries dynamic without string formatting.

```python
min_score = 85
target_status = "active"

# Inject Python variables into the query string
result = df.query("score >= @min_score and status == @target_status")

# Works with lists too
allowed_statuses = ["active", "trial"]
result = df.query("status in @allowed_statuses")

# Works with computed values
threshold = df["score"].median()
above_median = df.query("score > @threshold")
```

Without `@`, query would try to interpret `min_score` as a column name and fail. The `@` makes the scoping explicit.

---

## df.eval() — Creating New Columns With Expressions

**`df.eval()`** evaluates an expression and — when used with `inplace=True` or assignment syntax — creates a new column. It's `query()` for column creation.

```python
# Create a new column from an expression
df.eval("score_normalized = (score - score.mean()) / score.std()", inplace=True)

# Multiple assignments at once
df.eval("""
    score_pct = score / 100
    age_squared = age ** 2
    composite = score * 0.7 + age * 0.3
""", inplace=True)

# Without inplace: returns a new DataFrame
df2 = df.eval("efficiency = output / input_cost")

# Reference Python variables with @
baseline = 70
df.eval("score_above_baseline = score - @baseline", inplace=True)
```

---

## Performance Benefit — The numexpr Backend

Both `query()` and `eval()` can use **numexpr**, a C-based expression evaluator that bypasses Python's overhead. For DataFrames larger than ~100K rows, this can be significantly faster than equivalent Pandas operations.

```python
import numpy as np

# Pandas standard (creates temporary arrays)
result = df[(df["a"] > 0) & (df["b"] < df["c"]) & (df["score"] >= 90)]

# query() with numexpr backend — avoids intermediate allocations
result = df.query("a > 0 and b < c and score >= 90", engine="numexpr")

# Check if numexpr is available
try:
    import numexpr
    print(f"numexpr available: version {numexpr.__version__}")
except ImportError:
    print("numexpr not installed — query uses python engine")

# Install: pip install numexpr
# The "python" engine is always available as fallback
result = df.query("score > 90", engine="python")  # ← explicit fallback
```

The performance gain is most noticeable when: the DataFrame has >100K rows, the filter involves multiple columns, and memory is a bottleneck (numexpr avoids temporaries).

---

## When NOT to Use query() and eval()

`query()` and `eval()` are powerful, but they have real limits:

```python
# 1. Column names with spaces or special characters require backtick quoting
df.query("`request count` > 100")   # ← backticks around problematic names
df.query("`user-id` == 'abc'")

# 2. Method calls don't work inside query strings
# WRONG:
df.query("name.str.startswith('A')")   # ← fails

# RIGHT: use standard boolean indexing for method-based filters
df[df["name"].str.startswith("A")]

# 3. Complex multi-step logic is clearer as standard Python
# A query string with 10 conditions is not more readable than well-spaced boolean indexing

# 4. eval() doesn't support all pandas operations
# WRONG inside eval:
df.eval("first = name.str.split(' ').str[0]")  # ← fails

# 5. Debugging is harder — errors in query strings have less informative tracebacks
```

Rule of thumb: use `query()` for 2–6 condition row filters on clean column names. Use standard indexing for method calls, complex logic, or column names with spaces.

---

## Real Use — Clean, Readable Filter Chains

This example shows the full `query()` + `eval()` workflow applied to a real ML data-cleaning pipeline. **`eval()`** adds derived columns first, then `query()` filters on them — keeping each step readable and the logic close to a written specification. The `@min_density` injection keeps the threshold in a named Python variable rather than hardcoded inside the string.

```python
import pandas as pd

df = pd.read_parquet("model_training_candidates.parquet")

# Without query: deeply nested, error-prone
df_filtered = df[
    (df["token_count"] >= 50) &
    (df["token_count"] <= 512) &
    (df["quality_score"] >= 3.5) &
    (df["language"] == "en") &
    (df["source"] != "synthetic") &
    (~df["contains_pii"])
]

# With query: reads like a spec document
df_filtered = df.query(
    "token_count >= 50 and token_count <= 512"
    " and quality_score >= 3.5"
    " and language == 'en'"
    " and source != 'synthetic'"
    " and not contains_pii"
)

# Add computed columns with eval before filtering
df = df.eval("""
    token_density = quality_score / token_count
    length_flag = token_count > 400
""")

min_density = 0.01
df_final = df.query("token_density >= @min_density and not length_flag")

print(f"Rows after filtering: {len(df_final):,}")
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
