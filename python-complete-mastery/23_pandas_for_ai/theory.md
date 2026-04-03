# 🐼 Pandas for AI — The Complete Mastery Guide

> *"Before a model can learn from data, a human has to clean it.*
> *Pandas is the tool that makes that possible."*

---

## 🗺️ What You Will Master

```
┌─────────────────────────────────────────────────────────────────────────┐
│  BEGINNER         INTERMEDIATE          ADVANCED          AI ENGINEER    │
│                                                                          │
│  • Series vs      • apply / map         • groupby         • Load JSONL  │
│    DataFrame      • str methods         • pivot_table     • Clean data  │
│  • read_csv       • type casting        • merge / join    • Filter rows │
│  • head/info      • fillna / dropna     • chunksize       • to_jsonl    │
│  • loc / iloc     • duplicates          • memory types    • Fine-tune   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# 📖 The Story — Why You Are Here

You just downloaded a dataset to fine-tune your LLM.

It is a CSV with 50,000 rows: user questions, expected answers, source documents, and quality ratings.

You open it in a text editor and immediately see problems:

- Row 847: answer column is empty.
- Row 2,301: duplicate of row 112.
- Row 5,000: quality rating is the string `"four"` instead of the number `4`.
- Row 12,400: question is just `"???"`.
- Dozens of rows have ratings below 3 — noisy, low-quality examples that will hurt training.

You cannot feed this directly to your model.

Before you can train anything, you need to:

1. Load the data and understand its shape.
2. Find and remove missing rows.
3. Find and remove duplicates.
4. Fix incorrect data types.
5. Filter out low-quality examples.
6. Format the clean data as `{prompt, completion}` pairs.
7. Export as JSONL — the format OpenAI and most fine-tuning pipelines expect.

Pandas is the tool every AI engineer uses for exactly this.

This guide teaches you the whole workflow — from raw messy CSV to clean JSONL ready for training.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`DataFrame` / `Series` basics · `read_csv` / `to_csv` · Indexing (`loc`, `iloc`) · `groupby` · `merge` / `join` · Handling missing data (`fillna`, `dropna`)

**Should Learn** — Important for real projects, comes up regularly:
`apply` / `map` / `applymap` · Chaining methods · `query()` · `pivot_table` · Time series basics · `explode()` · `cut()` / `qcut()`

**Good to Know** — Useful in specific situations:
MultiIndex · `resample()` / `rolling()` · Categorical dtype · `eval()` · Named groupby aggregations · Copy semantics (view vs copy)

**Reference** — Know it exists, look up when needed:
Sparse dtypes · HDF5 export · `pd.testing` · Fuzzy merges · DST edge cases

---

# 1️⃣ What is Pandas — Series vs DataFrame

Pandas is a Python library for working with structured, tabular data.

Think of it as a programmable spreadsheet — but one that can handle millions of rows, chain transformations, and export to any format.

There are two core data structures.

---

## Series — One Column of Data

A Series is a one-dimensional labeled array.

```python
import pandas as pd

ratings = pd.Series([5, 4, 3, 5, 2], name="rating")
print(ratings)
# 0    5
# 1    4
# 2    3
# 3    5
# 4    2
# Name: rating, dtype: int64
```

Each value has an index label (0, 1, 2 ...) and a data type.

You can use custom index labels:

```python
scores = pd.Series([95, 82, 78], index=["Alice", "Bob", "Charlie"])
print(scores["Alice"])   # 95
```

---

## DataFrame — A Full Table

A DataFrame is a two-dimensional table with named columns and row indices.

It is the workhorse of Pandas — almost everything you do will be on a DataFrame.

```python
data = {
    "question": ["What is Python?", "What is a tensor?", "What is Python?"],
    "answer":   ["A programming language", "A multi-dimensional array", None],
    "rating":   [5, 4, 3]
}

df = pd.DataFrame(data)
print(df)
#             question                    answer  rating
# 0    What is Python?        A programming language       5
# 1  What is a tensor?  A multi-dimensional array       4
# 2    What is Python?                      None       3
```

Think of each column as a Series, and the DataFrame as a dict of Series sharing the same index.

---

# 2️⃣ Loading Data

## From CSV (most common for datasets)

```python
df = pd.read_csv("training_data.csv")

# With options:
df = pd.read_csv(
    "training_data.csv",
    sep=",",              # delimiter
    header=0,             # row 0 is the header
    encoding="utf-8",
    nrows=1000,           # load only first 1000 rows (useful for testing)
)
```

## From JSON

```python
df = pd.read_json("training_data.json")

# Newline-delimited JSON (JSONL):
df = pd.read_json("training_data.jsonl", lines=True)
```

## From Parquet (columnar format — efficient for large AI datasets)

```python
df = pd.read_parquet("training_data.parquet")
```

Parquet is faster and smaller than CSV for large datasets. Many Hugging Face datasets use it.

## From a Python dict or list

```python
# From dict (column-oriented):
df = pd.DataFrame({
    "prompt":     ["What is AI?", "What is ML?"],
    "completion": ["Artificial intelligence", "Machine learning"]
})

# From list of dicts (row-oriented — common when building from API responses):
rows = [
    {"prompt": "What is AI?",  "completion": "Artificial intelligence"},
    {"prompt": "What is ML?",  "completion": "Machine learning"},
]
df = pd.DataFrame(rows)
```

## Chunked loading for huge files

```python
# Process in chunks of 10,000 rows — never loads entire file into memory:
chunks = []
for chunk in pd.read_csv("huge_dataset.csv", chunksize=10_000):
    # filter each chunk before keeping it:
    clean_chunk = chunk.dropna(subset=["answer"])
    chunks.append(clean_chunk)

df = pd.concat(chunks, ignore_index=True)
```

---

# 3️⃣ Inspecting Data

Before cleaning anything, understand what you have.

```python
df.head()           # first 5 rows
df.head(10)         # first 10 rows
df.tail()           # last 5 rows
df.shape            # (rows, columns) as tuple → (50000, 4)
df.columns          # Index(['question', 'answer', 'rating', 'source'])
df.dtypes           # data type of each column
df.info()           # summary: column names, non-null counts, dtypes, memory
df.describe()       # statistics for numeric columns: mean, std, min, max
```

Example output of `df.info()`:

```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 50000 entries, 0 to 49999
Data columns (total 4 columns):
 #   Column    Non-Null Count  Dtype
---  ------    --------------  -----
 0   question  49850 non-null  object
 1   answer    47200 non-null  object   ← 2800 missing answers!
 2   rating    50000 non-null  object   ← should be int, not object
 3   source    50000 non-null  object
```

Check unique values and frequencies:

```python
df["rating"].value_counts()
# 5    15000
# 4    12000
# 3     8000
# four   500   ← string mixed in!
# 2     4000
# 1     500

df["rating"].nunique()        # how many unique values
df["source"].unique()         # array of unique values
df.duplicated().sum()         # how many duplicate rows total
df.isnull().sum()             # missing values per column
```

---

# 4️⃣ Selecting Data

## Column access

```python
df["question"]               # returns a Series
df[["question", "answer"]]   # returns a DataFrame (double brackets = list of columns)
```

## loc — label-based selection

`loc` uses the actual index labels (row names) and column names.

```python
df.loc[0]                           # row with index label 0
df.loc[0, "question"]               # single cell
df.loc[0:4]                         # rows 0 through 4 (inclusive!)
df.loc[0:4, "question":"rating"]    # rows and columns by name range
```

## iloc — position-based selection

`iloc` uses integer positions (like a list).

```python
df.iloc[0]              # first row (position 0)
df.iloc[0, 1]           # row 0, column 1
df.iloc[0:5]            # first 5 rows (exclusive end, like Python slicing)
df.iloc[:, 0:2]         # all rows, first 2 columns
df.iloc[-1]             # last row
```

Key difference:

```python
# loc — end is INCLUSIVE:
df.loc[0:4]     # rows 0, 1, 2, 3, 4

# iloc — end is EXCLUSIVE (like Python ranges):
df.iloc[0:4]    # rows 0, 1, 2, 3
```

## Boolean filtering

```python
df[df["rating"] >= 4]                          # rows where rating >= 4
df[df["answer"].notna()]                       # rows where answer is not null
df[df["question"].str.len() > 10]              # rows where question > 10 chars

# Combine conditions (use & and |, not 'and'/'or'):
df[(df["rating"] >= 4) & (df["answer"].notna())]

# Filter with isin:
df[df["source"].isin(["wikipedia", "arxiv"])]
```

---

# 5️⃣ Cleaning Data

## Handling missing values

```python
df.isnull()                     # boolean DataFrame — True where value is missing
df.isnull().sum()               # count missing per column
df.isnull().sum() / len(df)     # proportion missing per column

# Drop rows where ANY column is null:
df.dropna()

# Drop rows where specific columns are null:
df.dropna(subset=["answer"])           # drop rows missing 'answer'
df.dropna(subset=["answer", "question"])  # drop rows missing either

# Drop columns where more than 50% of values are missing:
df.dropna(axis=1, thresh=int(0.5 * len(df)))

# Fill missing values:
df["answer"].fillna("No answer available")         # fill with a string
df["rating"].fillna(df["rating"].median())         # fill with median
df["answer"].fillna(method="ffill")                # forward fill (use previous value)
```

Important: Pandas methods return a new DataFrame by default — they do not modify in place.

```python
# These do NOT change df:
df.dropna(subset=["answer"])
df.fillna("unknown")

# These DO update df:
df = df.dropna(subset=["answer"])
df = df.fillna("unknown")

# Or use inplace=True (less recommended in modern pandas):
df.dropna(subset=["answer"], inplace=True)
```

## Handling duplicates

```python
df.duplicated()                    # boolean Series — True for duplicate rows
df.duplicated().sum()              # count of duplicate rows
df.duplicated(subset=["question"]) # duplicates based on question column only

# View the duplicate rows:
df[df.duplicated(subset=["question"], keep=False)]

# Remove duplicates (keep first occurrence):
df = df.drop_duplicates()
df = df.drop_duplicates(subset=["question"])       # deduplicate on question only
df = df.drop_duplicates(subset=["question"], keep="last")  # keep last occurrence
```

---

# 6️⃣ Transforming Data

## apply — apply a function to each row or column

```python
# Apply to a column (Series):
df["question_length"] = df["question"].apply(len)

# Apply a custom function:
def clean_text(text):
    return text.strip().lower()

df["question"] = df["question"].apply(clean_text)

# Apply to each row (axis=1):
def make_pair(row):
    return f"Q: {row['question']} A: {row['answer']}"

df["qa_pair"] = df.apply(make_pair, axis=1)
```

## map — element-wise transformation (simpler than apply)

```python
# Replace values with a dict mapping:
rating_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
df["rating"] = df["rating"].map(rating_map)

# Apply a function element-by-element:
df["rating"] = df["rating"].map(lambda x: int(x) if str(x).isdigit() else None)
```

## String methods (vectorized — no loop needed)

Pandas has a `.str` accessor with all standard string operations:

```python
df["question"].str.lower()                    # lowercase
df["question"].str.upper()                    # uppercase
df["question"].str.strip()                    # remove leading/trailing whitespace
df["question"].str.replace("?", "", regex=False)   # replace characters
df["question"].str.contains("Python")         # boolean — does it contain?
df["question"].str.startswith("What")         # boolean — does it start with?
df["question"].str.len()                      # length of each string
df["question"].str.split(" ")                 # split into list
df["question"].str[:50]                       # truncate to 50 characters
```

## Type casting

```python
df["rating"].astype(int)          # convert to int
df["rating"].astype(float)        # convert to float
df["rating"].astype(str)          # convert to string
df["rating"].astype("category")   # category dtype — saves memory for repeated values

# Safe conversion with error handling:
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
# errors="coerce" → invalid values become NaN instead of raising an error
```

---

# 7️⃣ Adding and Removing Columns

## Adding columns

```python
# From a constant:
df["version"] = "v1"

# From a calculation:
df["question_length"] = df["question"].str.len()

# From a condition:
df["is_high_quality"] = df["rating"] >= 4

# From apply:
df["prompt"] = df["question"].apply(lambda q: f"Answer this question: {q}")
```

## Removing columns

```python
df.drop(columns=["source"])                      # drop one column
df.drop(columns=["source", "version"])           # drop multiple
df = df.drop(columns=["source"])                 # assign back to keep change
```

## Renaming columns

```python
df.rename(columns={"question": "prompt", "answer": "completion"})
df = df.rename(columns={"question": "prompt", "answer": "completion"})
```

## Reordering columns

```python
df = df[["prompt", "completion", "rating"]]      # select in desired order
```

---

# 8️⃣ Grouping and Aggregating

## groupby

```python
# Count rows per source:
df.groupby("source").size()

# Mean rating per source:
df.groupby("source")["rating"].mean()

# Multiple aggregations at once:
df.groupby("source").agg(
    count=("rating", "count"),
    avg_rating=("rating", "mean"),
    max_rating=("rating", "max")
)
```

## agg with custom functions

```python
df.groupby("source")["question"].agg(["count", "nunique"])
df.groupby("source")["rating"].agg(lambda x: (x >= 4).sum())  # count high-quality
```

## pivot_table

```python
pd.pivot_table(
    df,
    values="rating",
    index="source",
    aggfunc="mean"
)
```

---

# 9️⃣ Sorting and Ranking

## Sorting

```python
df.sort_values("rating")                          # ascending
df.sort_values("rating", ascending=False)         # descending
df.sort_values(["source", "rating"], ascending=[True, False])  # multi-column sort
df = df.sort_values("rating", ascending=False).reset_index(drop=True)
```

## Ranking

```python
df["rank"] = df["rating"].rank(ascending=False, method="dense")
```

## Reset index after filtering/sorting

After filtering rows, the index has gaps. Reset it:

```python
df = df.reset_index(drop=True)   # drop=True discards the old index
```

---

# 🔟 Merging and Joining DataFrames

When you have data spread across multiple files — e.g., questions in one CSV and metadata in another.

## merge — SQL-style join

```python
# Inner join (keep only rows that match in both):
merged = pd.merge(df_questions, df_metadata, on="question_id")

# Left join (keep all rows from left, fill nulls for unmatched):
merged = pd.merge(df_questions, df_metadata, on="question_id", how="left")

# Merge on different column names:
merged = pd.merge(df_questions, df_metadata,
                  left_on="q_id", right_on="question_id")
```

## concat — stack DataFrames vertically or horizontally

```python
# Stack rows (add more rows):
combined = pd.concat([df_batch1, df_batch2, df_batch3], ignore_index=True)

# Stack columns (add more columns):
combined = pd.concat([df_questions, df_answers], axis=1)
```

## join — index-based join

```python
df1.join(df2, on="question_id")
```

---

# 1️⃣1️⃣ Exporting Data

```python
df.to_csv("clean_data.csv", index=False)           # index=False skips row numbers
df.to_json("clean_data.json", orient="records")    # list of dicts
df.to_parquet("clean_data.parquet", index=False)   # efficient binary format
df.to_excel("clean_data.xlsx", index=False)        # Excel
```

## Exporting as JSONL (the standard fine-tuning format)

JSONL is one JSON object per line. OpenAI, Mistral, and most fine-tuning tools require this.

```python
import json

with open("fine_tuning_data.jsonl", "w") as f:
    for record in df.to_dict(orient="records"):
        f.write(json.dumps(record) + "\n")
```

Or with pandas directly:

```python
df.to_json("fine_tuning_data.jsonl", orient="records", lines=True)
```

---

# 1️⃣2️⃣ Real AI Engineering Examples

This is the full workflow from raw CSV to clean JSONL.

---

## Step 1 — Load and inspect the raw dataset

```python
import pandas as pd
import json

df = pd.read_csv("raw_training_data.csv")

print(df.shape)          # (50000, 4)
print(df.head())
print(df.info())
print(df.isnull().sum())
print(df["rating"].value_counts())
```

Expected output:

```
(50000, 4)
           question         answer  rating      source
0   What is Python?  A language...       5   wikipedia
1   What is a GPU?     None          NaN   arxiv
...

<class 'pandas.core.frame.DataFrame'>
 #   Column    Non-Null Count  Dtype
 0   question  49850 non-null  object
 1   answer    47200 non-null  object
 2   rating    49500 non-null  object
 3   source    50000 non-null  object

question       150
answer        2800
rating         500
source           0
dtype: int64

5       15000
4       12000
3        8000
four      500
2        4000
1         500
```

Already you can see: 2,800 missing answers, 500 missing ratings, 500 ratings that are strings.

---

## Step 2 — Clean: fix types, remove nulls, deduplicate

```python
# Fix string ratings like "four" → NaN (we'll drop them):
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

# Remove rows with missing answer or rating:
df = df.dropna(subset=["answer", "rating"])

# Convert rating to int now that nulls are gone:
df["rating"] = df["rating"].astype(int)

# Remove duplicate questions (keep highest-rated version):
df = df.sort_values("rating", ascending=False)
df = df.drop_duplicates(subset=["question"], keep="first")

# Reset index:
df = df.reset_index(drop=True)

print(f"Remaining rows: {len(df)}")   # e.g., 44,500
```

---

## Step 3 — Filter: keep only high-quality examples

```python
df_quality = df[df["rating"] >= 4].copy()
print(f"High-quality rows: {len(df_quality)}")   # e.g., 27,000
```

---

## Step 4 — Transform: format as prompt/completion pairs

```python
def build_prompt(question):
    return f"Answer the following question clearly and accurately:\n\n{question}"

df_quality["prompt"]     = df_quality["question"].apply(build_prompt)
df_quality["completion"] = df_quality["answer"].str.strip()

# Keep only the columns needed for fine-tuning:
df_final = df_quality[["prompt", "completion"]]
print(df_final.head(2))
```

Output:

```
                                              prompt                  completion
0  Answer the following question clearly...\n\nW...  A programming language...
1  Answer the following question clearly...\n\nW...  A multi-dimensional array
```

---

## Step 5 — Export as JSONL for fine-tuning

```python
output_path = "fine_tuning_data.jsonl"

with open(output_path, "w") as f:
    for record in df_final.to_dict(orient="records"):
        f.write(json.dumps(record) + "\n")

print(f"Saved {len(df_final)} examples to {output_path}")
```

Verify the output:

```python
# Read back and inspect:
with open(output_path) as f:
    for i, line in enumerate(f):
        print(json.loads(line))
        if i >= 2:
            break
```

Output:

```
{"prompt": "Answer the following question...\n\nWhat is Python?", "completion": "A programming language..."}
{"prompt": "Answer the following question...\n\nWhat is a tensor?", "completion": "A multi-dimensional array"}
```

This is now ready to pass directly to the OpenAI fine-tuning API or any HuggingFace trainer.

---

# 🧠 Final Mental Model

Pandas gives you a programmable spreadsheet.

For AI engineers, the core workflow is always:

```
Load → Inspect → Clean → Filter → Transform → Export
```

Every step is a Pandas operation:

```
Load        → read_csv, read_json, read_parquet
Inspect     → head, info, describe, value_counts, isnull
Clean       → dropna, fillna, drop_duplicates, to_numeric
Filter      → boolean indexing: df[df["rating"] >= 4]
Transform   → apply, map, str methods, astype, rename
Export      → to_csv, to_json (lines=True), to_parquet
```

The model does not care how you cleaned the data.

It only cares that the data is clean.

Pandas is how you get it there.

---

# 🔁 Navigation

| | |
|---|---|
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Previous | [../21_data_engineering_applications/theory.md](../21_data_engineering_applications/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Numpy For Ai — Interview Q&A](../22_numpy_for_ai/interview.md) &nbsp;|&nbsp; **Next:** [Cheat Sheet →](./cheatsheet.md)

**Related Topics:** [Cheat Sheet](./cheatsheet.md) · [Interview Q&A](./interview.md)
