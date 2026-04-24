# ⚡ Pandas for AI — Cheatsheet

```
┌─────────────────────────────────────────────────────────────────────────┐
│               PANDAS FOR AI ENGINEERING — QUICK REFERENCE               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📥 Loading Data

```python
import pandas as pd

df = pd.read_csv("data.csv")                             # CSV
df = pd.read_csv("data.csv", nrows=1000)                 # first 1000 rows only
df = pd.read_json("data.json")                           # JSON
df = pd.read_json("data.jsonl", lines=True)              # JSONL (newline-delimited)
df = pd.read_parquet("data.parquet")                     # Parquet (fast + compressed)
df = pd.DataFrame({"col1": [1,2], "col2": [3,4]})        # from dict
df = pd.DataFrame([{"a": 1}, {"a": 2}])                  # from list of dicts

# Large files — chunked loading:
chunks = [chunk for chunk in pd.read_csv("big.csv", chunksize=10_000)]
df = pd.concat(chunks, ignore_index=True)
```

---

## 🔍 Inspecting Data

```python
df.head()                     # first 5 rows
df.tail()                     # last 5 rows
df.shape                      # (rows, cols) tuple
df.columns                    # column names
df.dtypes                     # data type of each column
df.info()                     # full summary: names, non-nulls, dtypes, memory
df.describe()                 # statistics for numeric columns
df["col"].value_counts()      # frequency of each value
df["col"].nunique()           # count of unique values
df["col"].unique()            # array of unique values
df.isnull().sum()             # missing values per column
df.duplicated().sum()         # count duplicate rows
```

---

## 🎯 Selecting Data

```python
df["col"]                          # one column → Series
df[["col1", "col2"]]               # multiple columns → DataFrame

# loc — label-based (end is INCLUSIVE):
df.loc[0]                          # row by index label
df.loc[0, "col"]                   # single cell
df.loc[0:4, "col1":"col2"]         # rows and columns by name

# iloc — position-based (end is EXCLUSIVE like Python):
df.iloc[0]                         # first row
df.iloc[0, 1]                      # row 0, column 1 (by position)
df.iloc[0:5]                       # rows 0-4
df.iloc[:, 0:2]                    # all rows, first 2 columns
df.iloc[-1]                        # last row
```

---

## 🔎 Filtering Rows

```python
df[df["rating"] >= 4]                              # comparison
df[df["answer"].notna()]                           # not null
df[df["answer"].isna()]                            # is null
df[df["source"] == "wikipedia"]                    # equality
df[df["source"].isin(["wikipedia", "arxiv"])]      # multiple values

# Combine conditions — use & and | not 'and'/'or':
df[(df["rating"] >= 4) & (df["answer"].notna())]
df[(df["source"] == "arxiv") | (df["rating"] == 5)]

# String filtering:
df[df["question"].str.contains("Python")]
df[df["question"].str.startswith("What")]
df[df["question"].str.len() > 20]
```

---

## 🧹 Cleaning — Missing Values

```python
df.isnull().sum()                              # count missing per column
df.dropna()                                    # drop rows with ANY null
df.dropna(subset=["answer"])                   # drop rows with null in 'answer'
df.dropna(subset=["answer", "rating"])         # drop rows with null in either

df["col"].fillna("default")                    # fill with string
df["col"].fillna(df["col"].median())           # fill with median
df["col"].fillna(method="ffill")               # forward fill

# Always assign back (pandas returns a copy):
df = df.dropna(subset=["answer"])
df = df.fillna("unknown")
```

---

## 🧹 Cleaning — Duplicates

```python
df.duplicated().sum()                                    # count duplicates
df.duplicated(subset=["question"]).sum()                 # duplicates by column

df = df.drop_duplicates()                                # remove all duplicates
df = df.drop_duplicates(subset=["question"])             # deduplicate on one column
df = df.drop_duplicates(subset=["question"], keep="last")  # keep last occurrence
```

---

## 🔄 Transforming Data

```python
# apply — function to each element or row:
df["col"] = df["col"].apply(str.strip)
df["col"] = df["col"].apply(lambda x: x.lower() if isinstance(x, str) else x)
df["new"] = df.apply(lambda row: f"{row['a']} {row['b']}", axis=1)  # row-wise

# map — element-wise replacement:
df["rating"] = df["rating"].map({"one": 1, "two": 2, "three": 3, "four": 4, "five": 5})

# String methods (vectorized — no loop needed):
df["col"].str.lower()
df["col"].str.strip()
df["col"].str.replace("old", "new", regex=False)
df["col"].str.contains("keyword")
df["col"].str.len()
df["col"].str[:100]                    # truncate to 100 chars

# Type casting:
df["rating"] = df["rating"].astype(int)
df["rating"] = df["rating"].astype(float)
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")  # safe: bad values → NaN
```

---

## ➕ Adding and Removing Columns

```python
df["new_col"] = "constant"                              # constant value
df["length"]  = df["question"].str.len()                # from calculation
df["flag"]    = df["rating"] >= 4                       # boolean column
df["prompt"]  = df["question"].apply(lambda q: f"Q: {q}")  # from apply

df = df.drop(columns=["source"])                        # remove column
df = df.drop(columns=["source", "version"])             # remove multiple
df = df.rename(columns={"question": "prompt", "answer": "completion"})
df = df[["prompt", "completion", "rating"]]             # reorder columns
df = df.reset_index(drop=True)                          # reset row index
```

---

## 📊 Grouping and Aggregating

```python
df.groupby("source").size()                              # count rows per group
df.groupby("source")["rating"].mean()                    # mean rating per source
df.groupby("source")["rating"].agg(["mean", "count", "max"])

df.groupby("source").agg(
    count      = ("rating", "count"),
    avg_rating = ("rating", "mean"),
    max_rating = ("rating", "max"),
)

pd.pivot_table(df, values="rating", index="source", aggfunc="mean")
```

---

## 🔃 Sorting and Ranking

```python
df.sort_values("rating")                                 # ascending
df.sort_values("rating", ascending=False)                # descending
df.sort_values(["source", "rating"], ascending=[True, False])

df["rank"] = df["rating"].rank(ascending=False, method="dense")
```

---

## 🔗 Merging and Joining

```python
# merge (SQL-style join):
pd.merge(df1, df2, on="id")                              # inner join (default)
pd.merge(df1, df2, on="id", how="left")                  # left join
pd.merge(df1, df2, left_on="q_id", right_on="id")        # different column names

# concat (stack rows or columns):
pd.concat([df1, df2], ignore_index=True)                 # stack rows
pd.concat([df1, df2], axis=1)                            # stack columns
```

---

## 📤 Exporting Data

```python
df.to_csv("out.csv", index=False)                        # CSV (no row numbers)
df.to_json("out.json", orient="records")                 # JSON array of objects
df.to_json("out.jsonl", orient="records", lines=True)    # JSONL (one per line)
df.to_parquet("out.parquet", index=False)                # Parquet

# Manual JSONL export (full control):
import json
with open("fine_tuning.jsonl", "w") as f:
    for record in df.to_dict(orient="records"):
        f.write(json.dumps(record) + "\n")
```

---

## 🤖 AI Fine-Tuning Pipeline — One Block

```python
import pandas as pd, json

# 1. Load
df = pd.read_csv("raw.csv")

# 2. Fix types
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

# 3. Remove nulls
df = df.dropna(subset=["answer", "rating"])
df["rating"] = df["rating"].astype(int)

# 4. Deduplicate
df = df.sort_values("rating", ascending=False)
df = df.drop_duplicates(subset=["question"], keep="first")

# 5. Filter quality
df = df[df["rating"] >= 4].copy()

# 6. Format for fine-tuning
df["prompt"]     = df["question"].apply(lambda q: f"Answer clearly:\n\n{q}")
df["completion"] = df["answer"].str.strip()
df = df[["prompt", "completion"]].reset_index(drop=True)

# 7. Export JSONL
with open("fine_tuning.jsonl", "w") as f:
    for record in df.to_dict(orient="records"):
        f.write(json.dumps(record) + "\n")

print(f"Exported {len(df)} training examples.")
```

---

## 🧠 Memory Optimization

```python
# Use category dtype for columns with few unique values:
df["source"] = df["source"].astype("category")

# Downcast numeric columns:
df["rating"] = pd.to_numeric(df["rating"], downcast="integer")

# Check memory usage:
df.memory_usage(deep=True)
df.memory_usage(deep=True).sum() / 1e6    # total in MB
```

---

## ⚡ Quick Rules

```
✓  Always assign back: df = df.dropna(...)
✓  Use pd.to_numeric(errors="coerce") for unsafe type conversion
✓  Use & and | for combining filters — never 'and'/'or'
✓  Use .copy() after filtering to avoid SettingWithCopyWarning
✓  reset_index(drop=True) after filtering/sorting
✓  lines=True for JSONL export/import
✓  index=False for CSV/Parquet export (omits row numbers)
✓  chunksize for files too large to load at once
✗  Never modify a slice without .copy()
✗  Never use inplace=True — it's being deprecated
```

---

## Time Series

```python
# Parse dates
df['date'] = pd.to_datetime(df['date'])
df = pd.read_csv('data.csv', parse_dates=['date'])

# .dt accessor
df['date'].dt.year / .month / .day / .hour / .dayofweek
df['date'].dt.is_weekend          # custom: (df['date'].dt.dayofweek >= 5)
df['date'].dt.floor('H')          # round down to hour

# Set as index for time operations
df = df.set_index('date')

# Resample — change time frequency
df.resample('D').sum()            # daily totals
df.resample('W').mean()           # weekly means
df.resample('H').agg({'val': 'mean', 'count': 'sum'})

# Rolling window
df['col'].rolling(window=7).mean()           # 7-period moving average
df['col'].rolling(window=7, min_periods=1).std()

# Exponential weighted moving average
df['col'].ewm(span=7).mean()                 # recent values weighted more

# Shift / lag features
df['lag1'] = df['col'].shift(1)              # previous period
df['lead1'] = df['col'].shift(-1)            # next period
df['pct_change'] = df['col'].pct_change()    # period-over-period %
```

---

## String Operations

```python
# All via .str accessor — vectorized, no loops needed
df['col'].str.lower() / .upper() / .strip() / .title()
df['col'].str.len()                              # character count
df['col'].str.replace('old', 'new', regex=False)
df['col'].str.replace(r'\s+', ' ', regex=True)  # collapse whitespace

# Filtering
df[df['col'].str.contains('pattern', na=False)]
df[df['col'].str.startswith('prefix')]
df[df['col'].str.endswith('suffix')]

# Extraction
df['col'].str.extract(r'(\d{3}-\d{4})')         # first capture group → column
df['col'].str.extractall(r'(\w+@\w+)')           # all matches → multi-index

# Split and expand
df['col'].str.split(',', expand=True)            # → separate columns
df['col'].str.findall(r'#\w+')                   # all hashtags → list per row

# Encoding check
df['col'].str.contains(r'[^\x00-\x7F]', na=False)  # find non-ASCII
```

---

## Pivot, Melt, and Reshape

```python
# melt — wide to long
df_long = df.melt(
    id_vars=['id', 'name'],              # keep these as identifiers
    value_vars=['jan', 'feb', 'mar'],    # collapse these into rows
    var_name='month',                    # column name for old headers
    value_name='revenue'                 # column name for values
)

# pivot — long to wide (no aggregation, fails on duplicates)
df_wide = df_long.pivot(index='id', columns='month', values='revenue')

# pivot_table — long to wide with aggregation
pd.pivot_table(df,
    values='revenue', index='region',
    columns='product', aggfunc='sum',
    fill_value=0, margins=True          # margins=True adds row/column totals
)

# stack / unstack — move column labels into/out of index
df.stack()                  # column labels → inner index level
df.unstack()                # inner index level → column labels
df.unstack(level=0)         # specify which level to unstack

# Crosstab — frequency counts
pd.crosstab(df['true_label'], df['pred_label'])           # confusion matrix
pd.crosstab(df['a'], df['b'], normalize='all')            # proportions
```

---

## query() and eval()

```python
# query() — readable row filtering
df.query('age > 25 and city == "NYC"')
df.query('score >= @threshold')        # @ prefix references Python variable
df.query('col.str.contains("pattern")')

# eval() — expression against DataFrame
df.eval('revenue = price * quantity', inplace=True)
df.eval('tax = revenue * 0.1', inplace=True)

# When to use: > 100k rows, or chained conditions that need clarity
# On small DataFrames standard boolean indexing is faster
```

---

## SQL Integration

```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@host:5432/db')

# Read
df = pd.read_sql('SELECT * FROM users WHERE active = true', engine)
df = pd.read_sql_query('SELECT id, name FROM users LIMIT 100', engine)

# Read in chunks (large tables)
for chunk in pd.read_sql('SELECT * FROM logs', engine, chunksize=10_000):
    process(chunk)

# Write
df.to_sql('table_name', engine, if_exists='append', index=False)
# if_exists: 'fail' | 'replace' | 'append'

# With pandas read_sql, dtype mapping is automatic
# Force dtypes: dtype={'id': sqlalchemy.types.Integer()}
```

---

## ML Data Preparation

```python
from sklearn.model_selection import train_test_split

# Stratified split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y  # ← preserve class ratio
)

# Check class imbalance
y.value_counts(normalize=True)     # class proportions

# Label encoding
df['label_enc'] = df['cat'].map({'A': 0, 'B': 1, 'C': 2})

# One-hot encoding
pd.get_dummies(df, columns=['city', 'product'], drop_first=True)

# Normalization (fit on train, apply to test)
from sklearn.preprocessing import StandardScaler, MinMaxScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)   # ← transform only, do NOT fit_transform

# Outlier clipping
df['col'] = df['col'].clip(lower=df['col'].quantile(0.01),
                            upper=df['col'].quantile(0.99))
```

---

## Data Validation

```python
# Schema check
assert set(['id', 'label', 'text']).issubset(df.columns), "Missing columns"
assert df['label'].dtype == 'int64', f"Wrong dtype: {df['label'].dtype}"

# Null audit
null_rates = df.isnull().mean().sort_values(ascending=False)
print(null_rates[null_rates > 0])

# Range checks
assert df['age'].between(0, 120).all(), "Invalid age values"
assert df['prob'].between(0, 1).all(), "Probabilities out of range"

# Duplicate check
dupes = df.duplicated(subset=['id']).sum()
assert dupes == 0, f"{dupes} duplicate IDs"

# Value set validation
valid = {'pending', 'active', 'cancelled'}
assert df['status'].isin(valid).all(), f"Unknown statuses: {df['status'].unique()}"
```

---

## Performance

```python
# SLOW — Python loop, avoid:
for i, row in df.iterrows():
    result = row['a'] * row['b']

# FAST — vectorized:
df['result'] = df['a'] * df['b']

# SLOW — apply with lambda:
df['col'].apply(lambda x: x.strip().lower())
# FAST — .str accessor:
df['col'].str.strip().str.lower()

# Categorical dtype — compress low-cardinality string columns
df['status'] = df['status'].astype('category')  # up to 50x less memory
df = pd.read_csv('data.csv', dtype={'status': 'category'})

# Downcast numerics
df['age'] = pd.to_numeric(df['age'], downcast='integer')     # int64 → int8/16/32
df['score'] = pd.to_numeric(df['score'], downcast='float')   # float64 → float32

# Read only needed columns
df = pd.read_csv('big.csv', usecols=['id', 'price', 'date'])

# Profile memory
df.memory_usage(deep=True).sum() / 1024**2  # MB
df.info(memory_usage='deep')
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./README.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Previous | [../21_data_engineering_applications/theory.md](../21_data_engineering_applications/theory.md) |

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./README.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./README.md) · [Interview Q&A](./interview.md)
