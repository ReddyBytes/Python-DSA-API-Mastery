# 🎯 Pandas for AI — Interview Preparation Guide

> *"Interviewers don't just test whether you know Pandas syntax.*
> *They test whether you've actually used it to prepare real data."*

---

## 🧠 What Interviewers Actually Evaluate

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Level        What They Want to See                                       │
├──────────────────────────────────────────────────────────────────────────┤
│  0–2 years    Basic operations: load, filter, clean, export               │
│  2–5 years    groupby, apply vs map, memory awareness, dtype handling     │
│  5+ years     Full dataset pipelines, chunking, JSONL prep, fine-tuning  │
└──────────────────────────────────────────────────────────────────────────┘

AI engineer signal: they ask about JSONL, fine-tuning format, and how
you handle 10M-row datasets that don't fit in memory.
```

---

# 🟢 Level 1 — Beginner (0 to 2 Years)

---

**Q1: What is a DataFrame? How is it different from a regular Python list or dict?**

<details>
<summary>💡 Show Answer</summary>

**Weak answer:**
> "A DataFrame is like a table with rows and columns."

**Strong answer:**
> "A DataFrame is a two-dimensional, labeled data structure built on top of NumPy arrays.
> Unlike a Python list (which is just ordered values) or dict (which is key-value pairs),
> a DataFrame gives you: named columns, a row index, mixed types per column,
> and a rich API for filtering, grouping, merging, and transforming data — all without loops.
> It's essentially a programmable spreadsheet that operates on entire columns at once using vectorized operations,
> which makes it orders of magnitude faster than iterating with Python for-loops."

```python
import pandas as pd

# List: no column names, no vectorized ops
data = [["Alice", 5], ["Bob", 3]]

# DataFrame: named columns, rich API, vectorized
df = pd.DataFrame(data, columns=["name", "rating"])
df[df["rating"] >= 4]          # filter — no loop needed
df["rating"].mean()            # aggregation — no loop needed
```

</details>

<br>

**Q2: What is the difference between `loc` and `iloc`?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "`loc` is label-based — you use the actual index label and column name.
> `iloc` is position-based — you use integer positions like Python list indices.
> The critical difference is in slicing: `loc[0:4]` includes row 4 (end is inclusive),
> while `iloc[0:4]` excludes row 4 (end is exclusive, like Python's `range`).
> After filtering, the index can have gaps — so `iloc[0]` always means the first row,
> while `loc[0]` might fail if row 0 was dropped."

```python
df = pd.DataFrame({"score": [90, 80, 70, 60]}, index=[10, 20, 30, 40])

df.loc[10]        # row with index label 10 → score = 90
df.iloc[0]        # first row by position → score = 90

df.loc[10:30]     # rows 10, 20, 30 (inclusive)
df.iloc[0:2]      # rows at positions 0, 1 (exclusive end) → rows 10, 20
```

</details>

<br>

**Q3: How do you handle missing values in Pandas?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "First I inspect: `df.isnull().sum()` to count missing values per column and understand the scale.
> Then I decide based on context:
> If the column is critical (like 'answer' in a training dataset), I drop rows with `dropna(subset=['answer'])`.
> If the column is supplementary, I fill with a sensible default using `fillna()`.
> I always assign back because Pandas returns copies by default — methods do not modify in place."

```python
df.isnull().sum()                          # diagnose
df = df.dropna(subset=["answer"])          # drop critical missing
df["source"] = df["source"].fillna("unknown")   # fill non-critical

# Safe numeric conversion (bad values → NaN, not error):
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df = df.dropna(subset=["rating"])
df["rating"] = df["rating"].astype(int)
```

</details>

<br>

**Q4: How do you remove duplicate rows?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "I use `drop_duplicates()`. For a training dataset, I often deduplicate on a specific column —
> for example, remove rows where the same question appears more than once,
> keeping the version with the highest rating."

```python
df.duplicated().sum()                              # count duplicates

# Deduplicate on full row:
df = df.drop_duplicates()

# Deduplicate on 'question' column, keep highest-rated version:
df = df.sort_values("rating", ascending=False)
df = df.drop_duplicates(subset=["question"], keep="first")
df = df.reset_index(drop=True)
```

</details>

<br>

**Q5: How do you filter rows based on a condition?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "I use boolean indexing. You write a condition that returns a boolean Series,
> then pass it inside square brackets. For multiple conditions, combine with `&` (and) or `|` (or) —
> not Python's `and`/`or` keywords, which don't work on Series."

```python
df[df["rating"] >= 4]                              # single condition
df[df["answer"].notna()]                           # not null

# Multiple conditions — must use & and | with parentheses:
df[(df["rating"] >= 4) & (df["answer"].notna())]

# String filtering:
df[df["question"].str.contains("Python")]
```

</details>


# 🟡 Level 2 — Intermediate (2 to 5 Years)

---

**Q6: What is the difference between `apply`, `map`, and vectorized operations? Which should you prefer?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "`apply` calls a Python function on each element or row — it's flexible but slow because it's a loop under the hood.
> `map` is similar but for element-wise replacement, usually with a dict or a simpler function.
> Vectorized operations (like `.str.lower()`, `.astype()`, arithmetic) work on the whole Series at once using NumPy.
> You should always prefer vectorized first, then map, then apply — in that order.
> For AI data prep, most common operations have a vectorized equivalent."

```python
# Slowest — Python loop via apply:
df["question"] = df["question"].apply(lambda x: x.lower())

# Faster — vectorized string method:
df["question"] = df["question"].str.lower()

# apply is justified for complex multi-column logic:
def build_prompt(row):
    return f"Context: {row['source']}\nQ: {row['question']}"

df["prompt"] = df.apply(build_prompt, axis=1)

# map for simple replacements:
df["rating"] = df["rating"].map({"four": 4, "five": 5})
```

</details>

<br>

**Q7: How does `groupby` work? Walk me through an example.**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "`groupby` splits the DataFrame into groups by a column's unique values,
> then applies an aggregation function to each group, then combines the results.
> It's the Pandas equivalent of SQL's GROUP BY.
> I often use it in data prep to understand the distribution of my dataset —
> e.g., how many examples per source, or the average quality rating per topic."

```python
# Count examples per source:
df.groupby("source").size()

# Average rating per source:
df.groupby("source")["rating"].mean()

# Multiple aggregations at once:
df.groupby("source").agg(
    count      = ("rating", "count"),
    avg_rating = ("rating", "mean"),
    max_rating = ("rating", "max"),
)

# Find which sources have enough high-quality examples:
df[df["rating"] >= 4].groupby("source").size().sort_values(ascending=False)
```

</details>

<br>

**Q8: How do you optimize memory usage in Pandas when working with large datasets?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "Three main techniques:
> First, use `category` dtype for string columns with few unique values — like source names or categories.
> Second, downcast numeric columns — use int32 instead of int64, float32 instead of float64.
> Third, for files that don't fit in RAM, use `chunksize` in `read_csv` to process in batches.
> A typical 50M-row dataset might go from 4GB to 800MB with these changes."

```python
# Check current memory:
df.memory_usage(deep=True).sum() / 1e6    # in MB

# Use category for low-cardinality strings:
df["source"] = df["source"].astype("category")
df["topic"]  = df["topic"].astype("category")

# Downcast integers:
df["rating"] = pd.to_numeric(df["rating"], downcast="integer")

# Process large files in chunks:
results = []
for chunk in pd.read_csv("huge.csv", chunksize=50_000):
    clean = chunk.dropna(subset=["answer"])
    clean = clean[clean["rating"].astype(float) >= 4]
    results.append(clean)

df = pd.concat(results, ignore_index=True)
```

</details>

<br>

**Q9: What is `SettingWithCopyWarning` and how do you fix it?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "It appears when you try to modify a DataFrame that is a slice of another DataFrame.
> Pandas is warning you that you may be modifying a copy, not the original.
> The fix is to use `.copy()` when you create a subset you intend to modify."

```python
# This may trigger the warning:
subset = df[df["rating"] >= 4]
subset["prompt"] = "Q: " + subset["question"]   # warning: modifying a slice?

# Fix — call .copy() explicitly:
subset = df[df["rating"] >= 4].copy()
subset["prompt"] = "Q: " + subset["question"]   # safe — you own this copy
```

</details>

<br>

**Q10: How do you merge two DataFrames? What is the difference between merge types?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "`pd.merge` works like SQL joins.
> Inner join keeps only rows that match in both DataFrames.
> Left join keeps all rows from the left DataFrame and fills unmatched right columns with NaN.
> Right join is the opposite.
> Outer join keeps everything and fills gaps with NaN.
> For AI data prep, I often use left join when enriching a dataset with optional metadata —
> so I keep all my training examples even if metadata is missing."

```python
# Inner join: only questions that have metadata:
result = pd.merge(df_questions, df_metadata, on="question_id")

# Left join: keep all questions, add metadata where available:
result = pd.merge(df_questions, df_metadata, on="question_id", how="left")

# Stack multiple dataset files:
combined = pd.concat([df_batch1, df_batch2, df_batch3], ignore_index=True)
```

</details>


# 🔵 Level 3 — Advanced and AI Engineer (5+ Years)

---

**Q11: How do you prepare a fine-tuning dataset with Pandas from start to finish?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "The full pipeline is: Load → Inspect → Fix types → Remove nulls → Deduplicate → Filter quality → Format prompt/completion → Export as JSONL.
> JSONL is the format expected by OpenAI's fine-tuning API and most HuggingFace trainers —
> one JSON object per line, each with at minimum a 'prompt' and 'completion' key."

```python
import pandas as pd, json

df = pd.read_csv("raw_training_data.csv")
print(df.shape, df.isnull().sum())

# Fix types:
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

# Remove nulls:
df = df.dropna(subset=["answer", "rating"])
df["rating"] = df["rating"].astype(int)

# Deduplicate (keep highest quality):
df = df.sort_values("rating", ascending=False)
df = df.drop_duplicates(subset=["question"], keep="first")

# Filter quality:
df = df[df["rating"] >= 4].copy()

# Format for fine-tuning:
df["prompt"]     = df["question"].apply(lambda q: f"Answer clearly:\n\n{q}")
df["completion"] = df["answer"].str.strip()
df = df[["prompt", "completion"]].reset_index(drop=True)

# Export JSONL:
with open("fine_tuning.jsonl", "w") as f:
    for record in df.to_dict(orient="records"):
        f.write(json.dumps(record) + "\n")

print(f"Exported {len(df)} examples.")
```

</details>

<br>

**Q12: How do you process a dataset that is too large to fit in memory?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "I use `chunksize` in `read_csv` to read and process the file in batches.
> I apply all filtering and cleaning per chunk before collecting results.
> This keeps memory usage constant regardless of file size — O(chunk) instead of O(file).
> For even larger workloads, Dask or Polars are drop-in replacements that add parallelism."

```python
import pandas as pd

results = []

for chunk in pd.read_csv("50gb_dataset.csv", chunksize=50_000):
    # Clean and filter each chunk:
    chunk["rating"] = pd.to_numeric(chunk["rating"], errors="coerce")
    chunk = chunk.dropna(subset=["answer", "rating"])
    chunk = chunk[chunk["rating"] >= 4]
    results.append(chunk)

df = pd.concat(results, ignore_index=True)
print(f"Total clean rows: {len(df)}")
```

</details>

<br>

**Q13: How do you convert a DataFrame to JSONL format for OpenAI fine-tuning?**

<details>
<summary>💡 Show Answer</summary>

**Strong answer:**
> "JSONL is one JSON object per line. OpenAI's fine-tuning format requires each line to have
> a 'messages' key for chat models (with system/user/assistant turns),
> or 'prompt'/'completion' for legacy completions format.
> I use `df.to_dict(orient='records')` to get a list of row dicts,
> then write each with `json.dumps` and a newline."

```python
import json

# Legacy completions format:
df = df.rename(columns={"question": "prompt", "answer": "completion"})

with open("fine_tuning.jsonl", "w") as f:
    for record in df[["prompt", "completion"]].to_dict(orient="records"):
        f.write(json.dumps(record) + "\n")

# Chat format for GPT-3.5/GPT-4 fine-tuning:
with open("chat_fine_tuning.jsonl", "w") as f:
    for _, row in df.iterrows():
        record = {
            "messages": [
                {"role": "system",    "content": "You are a helpful assistant."},
                {"role": "user",      "content": row["question"]},
                {"role": "assistant", "content": row["answer"]},
            ]
        }
        f.write(json.dumps(record) + "\n")
```

</details>

<br>

**Q14: How do you parse and work with datetime data in Pandas? What operations does it unlock?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

Convert string columns to datetime dtype with `pd.to_datetime()`. This unlocks the `.dt` accessor for extracting date components, and enables time-based operations like resampling and rolling windows.

```python
df['date'] = pd.to_datetime(df['date'])          # parse from string
df = df.set_index('date')                         # set as index for time ops

df['date'].dt.year / .month / .day / .hour        # extract components
df['date'].dt.dayofweek                            # 0=Monday, 6=Sunday

df.resample('D').sum()                             # aggregate to daily
df['col'].rolling(window=7).mean()                 # 7-day moving average
df['col'].ewm(span=7).mean()                       # exponential weighted
df['col'].shift(1)                                 # lag by 1 period
```

**Why it matters:** Time series features (rolling means, lag values, hour-of-day) are among the most powerful features in production ML models.

</details>

<br>

**Q15: What is the difference between `pivot_table()` and `melt()`? When would you use each?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

- **`melt()`** converts wide format (each variable is a column) to long format (one row per observation). Use it before groupby, merge, or any operation that needs all observations in rows.
- **`pivot_table()`** converts long format to wide format with aggregation. Use it to summarize cross-dimensional data — equivalent to an Excel pivot table.

```python
# Wide → long (melt):
df_long = df.melt(id_vars=['student'], value_vars=['math', 'science'],
                  var_name='subject', value_name='score')

# Long → wide with aggregation (pivot_table):
pd.pivot_table(df, values='sales', index='region',
               columns='product', aggfunc='sum', fill_value=0)

# Confusion matrix using crosstab:
pd.crosstab(y_true, y_pred, normalize='true')  # row-normalized
```

**Why it matters:** Feature engineering often requires reshaping between wide and long formats — ML model inputs are typically wide (one feature per column).

</details>

<br>

**Q16: How does `df.query()` differ from boolean indexing? When is it faster?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

`df.query()` takes a filter expression as a readable string. It is equivalent to boolean indexing for correctness but uses the `numexpr` engine internally, which avoids creating intermediate boolean arrays.

```python
# Equivalent filters:
df[(df['age'] > 25) & (df['city'] == 'NYC')]    # boolean indexing
df.query('age > 25 and city == "NYC"')           # query string

# Reference Python variable with @:
threshold = 0.5
df.query('score >= @threshold')                  # @ prefix for external vars

# eval() for new columns:
df.eval('revenue = price * quantity', inplace=True)
```

`query()` is faster on DataFrames with >100k rows due to numexpr's multi-threaded evaluation. On small DataFrames, the string-parsing overhead makes it slower.

**Why it matters:** Large production datasets benefit from `query()`'s memory efficiency; it also produces cleaner code for complex multi-condition filters.

</details>

<br>

**Q17: How do you read and write DataFrames to a SQL database?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

Use `pd.read_sql()` to pull query results into a DataFrame, and `df.to_sql()` to write back. Both require a SQLAlchemy connection engine.

```python
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@host:5432/db')

# Read
df = pd.read_sql('SELECT * FROM users WHERE active = true', engine)

# Read large table in chunks:
chunks = []
for chunk in pd.read_sql('SELECT * FROM logs', engine, chunksize=10_000):
    chunks.append(chunk[chunk['status'] == 'active'])
df = pd.concat(chunks)

# Write
df.to_sql('table_name', engine, if_exists='append', index=False)
```

`if_exists` options: `'fail'` (raise if table exists), `'replace'` (drop and recreate), `'append'` (add rows).

**Why it matters:** Production ML pipelines pull training data from databases and write predictions back — `read_sql` / `to_sql` is the standard interface.

</details>

<br>

**Q18: How do you create a stratified train/test split with Pandas?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

Use sklearn's `train_test_split` with `stratify=y` to preserve the class distribution in both splits.

```python
from sklearn.model_selection import train_test_split

X = df.drop('label', axis=1)
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42,
    stratify=y   # ← ensures class proportion is same in train and test
)

# Verify class balance:
y_train.value_counts(normalize=True)
y_test.value_counts(normalize=True)
```

Without `stratify`, a random split may put 90% of the rare class in training, making the test set unrepresentative.

**Why it matters:** Class imbalance is the default in real-world datasets (fraud, rare diseases, churn). Stratified splitting is the baseline practice for any classification problem.

</details>

<br>

**Q19: How do you validate data quality in a Pandas pipeline before model training?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

Run checks on schema, nulls, ranges, duplicates, and value sets before any preprocessing step.

```python
def validate_dataset(df):
    # Schema
    assert {'id', 'label', 'text'}.issubset(df.columns), "Missing required columns"
    assert df['label'].dtype == 'int64', f"Wrong label dtype: {df['label'].dtype}"

    # Null rates
    null_rates = df.isnull().mean()
    high_null = null_rates[null_rates > 0.3]
    if len(high_null):
        raise ValueError(f"High null rate columns: {high_null.to_dict()}")

    # Range
    assert df['score'].between(0, 1).all(), "Scores out of [0, 1] range"

    # Duplicates
    dupes = df.duplicated(subset=['id']).sum()
    assert dupes == 0, f"{dupes} duplicate IDs found"

    # Value set
    assert df['status'].isin({'active', 'inactive'}).all(), "Unknown status values"
```

**Why it matters:** Silent data quality issues (range violations, unexpected nulls, duplicate rows) cause model bugs that surface in production, not in offline evaluation.

</details>

<br>

**Q20: What is categorical dtype and when should you use it?**

<details>
<summary>💡 Show Answer</summary>

**Answer:**

**Categorical dtype** stores repeated string values as integer codes with a lookup table, instead of storing the full string per row.

```python
df['status'] = df['status'].astype('category')   # convert
df['status'].cat.codes                            # integer codes
df['status'].cat.categories                       # unique values lookup

# Set at read time:
df = pd.read_csv('data.csv', dtype={'status': 'category', 'region': 'category'})

# Memory comparison:
# 1M rows, 5 unique values:
# object dtype:     ~50 MB (full string per row)
# category dtype:   ~1 MB  (int8 codes + 5-string table)
```

Use categorical when:
- The column has fewer than ~50 unique values relative to total rows
- The column is used in groupby (categorical groupby is significantly faster)
- Memory is a constraint and the cardinality is low

**Why it matters:** The single most impactful Pandas memory optimization for most real-world datasets with region, status, or label columns.

</details>


# 🔥 Common Candidate Mistakes

```
┌────────────────────────────────────────────────────────────────────────┐
│  MISTAKE                              HOW TO AVOID IT                  │
├────────────────────────────────────────────────────────────────────────┤
│  Forgetting to assign back            df = df.dropna(...) always       │
│  Using 'and'/'or' for filters         Use & and | with parentheses     │
│  Modifying a slice directly           Use .copy() on filtered subsets  │
│  Using apply when str method exists   Prefer vectorized .str ops       │
│  Not using errors="coerce"           pd.to_numeric can crash on mixed  │
│  Forgetting reset_index after filter  Gaps in index cause bugs         │
│  Loading huge file all at once        Use chunksize parameter          │
│  Forgetting index=False in to_csv     Adds an unwanted row number col  │
│  Not knowing JSONL format             AI engineers must know lines=True │
│  Using inplace=True                   Deprecated, inconsistent, avoid  │
└────────────────────────────────────────────────────────────────────────┘
```

---

# ⚡ Rapid-Fire Revision

```
• DataFrame = 2D labeled table; Series = 1D labeled column
• loc = label-based; iloc = position-based
• loc slicing is inclusive; iloc slicing is exclusive (like Python)
• isnull().sum() → count missing per column
• dropna(subset=["col"]) → drop rows missing a specific column
• to_numeric(errors="coerce") → bad values become NaN, not error
• drop_duplicates(subset=["col"]) → deduplicate on one column
• sort_values + drop_duplicates → deduplicate keeping best version
• apply → Python function per element/row (slow, flexible)
• map → dict replacement or simple lambda (medium speed)
• .str.lower() → vectorized (fastest)
• groupby("col").agg(...) → aggregate per group
• pd.merge → SQL-style join; pd.concat → stack rows or columns
• to_json(lines=True) → JSONL export
• to_dict(orient="records") → list of row dicts
• chunksize → process huge files without loading them whole
• category dtype → saves memory for low-cardinality string columns
• Use .copy() after filtering to avoid SettingWithCopyWarning
```

---

# 🏆 Final Interview Mindset

```
When asked about Pandas, the signal interviewers look for:

BEGINNER signal:   "I use it to read CSV files and filter rows."
INTERMEDIATE signal: Explains groupby, apply vs vectorized, memory dtypes.
SENIOR/AI signal:  Walks through a complete data prep pipeline,
                   knows JSONL format, handles large files with chunksize,
                   knows SettingWithCopyWarning, optimizes dtypes.

The difference between a junior data role and an AI engineer role
is often exactly this: have you actually prepared a fine-tuning dataset?
Be ready to walk through the entire pipeline end-to-end.
```

---

# 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Previous | [../21_data_engineering_applications/theory.md](../21_data_engineering_applications/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Cheat Sheet](./cheatsheet.md) &nbsp;|&nbsp; **Next:** [Async Python For Ai — Theory →](../24_async_python_for_ai/theory.md)

**Related Topics:** [Theory](./README.md) · [Cheat Sheet](./cheatsheet.md)
