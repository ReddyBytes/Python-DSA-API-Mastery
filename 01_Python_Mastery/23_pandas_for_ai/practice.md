# Pandas for AI — Practice

## Quick Index

| Q | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | time series — DatetimeIndex creation | 🟢 |
| [Q2](#q2) | time series — resample to hourly | 🟢 |
| [Q3](#q3) | time series — rolling window mean | 🟡 |
| [Q4](#q4) | time series — shift and diff for lag features | 🟡 |
| [Q5](#q5) | string operations — str accessor basics | 🟢 |
| [Q6](#q6) | string operations — str.contains with regex | 🟢 |
| [Q7](#q7) | string operations — str.extract with named groups | 🟡 |
| [Q8](#q8) | string operations — str.split expand | 🟡 |
| [Q9](#q9) | groupby advanced — agg dict | 🟢 |
| [Q10](#q10) | groupby advanced — transform vs agg | 🟡 |
| [Q11](#q11) | groupby advanced — groupby+apply | 🟡 |
| [Q12](#q12) | groupby advanced — named aggregation | 🟡 |
| [Q13](#q13) | pivot/melt — pivot_table | 🟢 |
| [Q14](#q14) | pivot/melt — melt wide to long | 🟢 |
| [Q15](#q15) | pivot/melt — wide_to_long / stack | 🟡 |
| [Q16](#q16) | pivot/melt — stack and unstack | 🟡 |
| [Q17](#q17) | query and eval — query() with variables | 🟢 |
| [Q18](#q18) | query and eval — eval() for computed columns | 🟢 |
| [Q19](#q19) | query and eval — chained query | 🟡 |
| [Q20](#q20) | query and eval — performance comparison | 🟠 |
| [Q21](#q21) | sql integration — read_sql with SQLite | 🟢 |
| [Q22](#q22) | sql integration — to_sql with if_exists | 🟢 |
| [Q23](#q23) | sql integration — merge vs SQL JOIN | 🟡 |
| [Q24](#q24) | sql integration — read_sql_query with params | 🟡 |
| [Q25](#q25) | ml data prep — train/test split preserving index | 🟢 |
| [Q26](#q26) | ml data prep — StandardScaler on DataFrame | 🟡 |
| [Q27](#q27) | ml data prep — one-hot encoding get_dummies | 🟡 |
| [Q28](#q28) | ml data prep — impute missing values | 🟡 |
| [Q29](#q29) | data validation — assert dtypes | 🟢 |
| [Q30](#q30) | data validation — check for nulls | 🟢 |
| [Q31](#q31) | data validation — validate value ranges | 🟡 |
| [Q32](#q32) | data validation — schema validation with pandera | 🟠 |
| [Q33](#q33) | performance — astype category | 🟢 |
| [Q34](#q34) | performance — query over boolean mask | 🟡 |
| [Q35](#q35) | performance — chunked read_csv | 🟡 |
| [Q36](#q36) | performance — vectorized vs apply benchmark | 🟠 |

Difficulty: 🟢 Basic / 🟡 Intermediate / 🟠 Advanced

---

<a id="q1"></a>

### Q1 · time series — DatetimeIndex creation 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


Given a list of ISO timestamp strings, convert them to a `DatetimeIndex` using `pd.to_datetime()`, then extract the hour and day-of-week for each timestamp as new DataFrame columns.


<details>
<summary>💡 Hint</summary>
Use `pd.to_datetime()` on the column, then access `.dt.hour` and `.dt.day_name()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "ts": ["2024-03-15 08:30:00", "2024-03-16 14:15:00", "2024-03-17 22:45:00"]
})

df["ts"] = pd.to_datetime(df["ts"])          # parse string → datetime64
df["hour"]        = df["ts"].dt.hour          # 0–23
df["day_of_week"] = df["ts"].dt.day_name()    # "Friday", "Saturday", ...

print(df)
```

**Why:** `pd.to_datetime()` converts strings to `datetime64[ns]`, unlocking the `.dt` accessor for all calendar-aware properties.
</details>

---

<a id="q2"></a>

### Q2 · time series — resample to hourly 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


You have a DataFrame with a `datetime64` index and a `latency_ms` column at per-minute granularity. Resample to produce hourly mean, max, and count — all in one call.


<details>
<summary>💡 Hint</summary>
Set the datetime column as the index first, then use `.resample("h").agg(...)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.read_csv("api_logs.csv", parse_dates=["timestamp"])
df = df.set_index("timestamp").sort_index()   # required before resample

hourly = df["latency_ms"].resample("h").agg(
    mean_latency="mean",
    max_latency="max",
    request_count="count",
)

print(hourly.head())
```

**Why:** `resample()` requires a `DatetimeIndex`; frequency string `"h"` means hourly buckets.
</details>

---

<a id="q3"></a>

### Q3 · time series — rolling window mean 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Using the same `latency_ms` column, compute a 24-period rolling mean and a rolling max over 10 periods. Ensure the rolling mean starts computing even when fewer than 24 values are available.


<details>
<summary>💡 Hint</summary>
Use `rolling(window=24, min_periods=1).mean()` to avoid NaN gaps at the start.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

# rolling mean: fills up gradually; set min_periods to avoid leading NaNs
df["rolling_24_mean"] = df["latency_ms"].rolling(window=24, min_periods=1).mean()

# rolling max: detect sustained high latency over 10 steps
df["rolling_10_max"]  = df["latency_ms"].rolling(window=10).max()

print(df[["latency_ms", "rolling_24_mean", "rolling_10_max"]].head(30))
```

**Why:** Without `min_periods=1`, the first 23 rows produce `NaN`; with it, the window computes on however many rows are available.
</details>

---

<a id="q4"></a>

### Q4 · time series — shift and diff for lag features 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Create three new columns on a time-series DataFrame: a 1-step lag of `latency_ms`, a 2-step lag, and the first difference (rate of change between consecutive rows). Then drop rows with `NaN` introduced by the shift.


<details>
<summary>💡 Hint</summary>
Use `.shift(1)`, `.shift(2)`, and `.diff(1)`, then `dropna()` at the end.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df["latency_lag_1"] = df["latency_ms"].shift(1)   # value from 1 step ago
df["latency_lag_2"] = df["latency_ms"].shift(2)   # value from 2 steps ago
df["latency_delta"] = df["latency_ms"].diff(1)    # current minus previous

df = df.dropna()   # remove rows where shifts produced NaN

print(df.head())
```

**Why:** Lag features let a model ask "what was the value before this one?" — one of the strongest signals in time-series ML. `diff(1)` equals `value - shift(1)`.
</details>

---

<a id="q5"></a>

### Q5 · string operations — str accessor basics 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Given a `raw_text` column with inconsistent casing and extra whitespace, produce three new columns: lowercase version, stripped version, and character length. Confirm that `None` values produce `NaN` without raising an error.


<details>
<summary>💡 Hint</summary>
Chain `.str.lower()`, `.str.strip()`, and `.str.len()` — all handle `None` gracefully.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "raw_text": ["  Hello World  ", "hello world", "HELLO WORLD", None]
})

df["lower"]    = df["raw_text"].str.lower()    # None → NaN, no error
df["stripped"] = df["raw_text"].str.strip()
df["length"]   = df["raw_text"].str.len()      # NaN for None row

print(df)
```

**Why:** The `.str` accessor propagates `NaN` automatically — you never need a guard like `if isinstance(x, str)` when using vectorized string methods.
</details>

---

<a id="q6"></a>

### Q6 · string operations — str.contains with regex 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Filter a DataFrame's `text` column to keep only rows that contain a URL (matching the pattern `https?://\S+`). Also create a boolean column `has_pii` that flags rows containing an SSN pattern (`\b\d{3}-\d{2}-\d{4}\b`).


<details>
<summary>💡 Hint</summary>
Pass `regex=True, na=False` to `.str.contains()` — `na=False` treats missing values as non-matches.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

# Keep rows containing a URL
df_with_url = df[df["text"].str.contains(r"https?://\S+", regex=True, na=False)]

# Flag rows that look like they contain an SSN
df["has_pii"] = df["text"].str.contains(
    r"\b\d{3}-\d{2}-\d{4}\b",
    regex=True,
    na=False,            # NaN rows → False, not NaN
)

df_clean = df[~df["has_pii"]]   # remove potential PII rows
print(f"Rows after PII filter: {len(df_clean)}")
```

**Why:** `na=False` is critical — without it, rows with `NaN` text produce `NaN` in the boolean mask, which causes filtering errors.
</details>

---

<a id="q7"></a>

### Q7 · string operations — str.extract with named groups 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


A `log_line` column contains entries like `"/api/v1/predict 200 45ms"`. Use `str.extract()` with named capture groups to pull `endpoint`, `status_code`, and `latency_ms` into separate columns, then concatenate them onto the original DataFrame.


<details>
<summary>💡 Hint</summary>
Use `(?P<name>...)` syntax for named groups. The result of `str.extract()` is a DataFrame with one column per group.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "log_line": ["/api/v1/predict 200 45ms", "/api/v2/embed 404 12ms"]
})

pattern = r"(?P<endpoint>/\S+)\s+(?P<status_code>\d{3})\s+(?P<latency_ms>\d+)ms"
extracted = df["log_line"].str.extract(pattern)
# extracted: DataFrame with columns endpoint, status_code, latency_ms

df = pd.concat([df, extracted], axis=1)
print(df)
```

**Why:** Named groups (`(?P<name>...)`) self-document the pattern and produce correctly named columns automatically — no need to rename after extraction.
</details>

---

<a id="q8"></a>

### Q8 · string operations — str.split expand 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


Split a `full_name` column (format: `"FirstName LastName"`) into two separate columns `first` and `last`. Then take a `tags` column where each row is a comma-separated string and explode it into one row per tag.


<details>
<summary>💡 Hint</summary>
Use `str.split(" ", expand=True)` for the fixed split. For variable tags, `str.split(",")` then `explode()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "full_name": ["Alice Smith", "Bob Jones"],
    "tags": ["python,ml,ai", "pandas,data"]
})

# Split fixed structure into two columns
df[["first", "last"]] = df["full_name"].str.split(" ", expand=True)
#                                        ↑ expand=True → DataFrame not list Series

# Explode variable-length comma-separated tags
exploded = df.assign(tag=df["tags"].str.split(",")).explode("tag")
print(exploded[["full_name", "tag"]])
```

**Why:** `expand=True` returns a DataFrame instead of a Series of lists, enabling direct multi-column assignment. `explode()` converts list-per-row into one-row-per-item.
</details>

---

<a id="q9"></a>

### Q9 · groupby advanced — agg dict 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Group a user scores DataFrame by `user_id` and compute mean score, max score, and total request count in a single `.agg()` call using a dictionary of aggregations.


<details>
<summary>💡 Hint</summary>
Pass a dict to `.agg()`: `{"score": ["mean", "max"], "request_id": "count"}`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "user_id":    ["A", "A", "B", "B", "B"],
    "score":      [80,  90,  70,  85,  95],
    "request_id": [1,   2,   3,   4,   5],
})

summary = df.groupby("user_id").agg(
    mean_score=("score",      "mean"),
    max_score=("score",       "max"),
    request_count=("request_id", "count"),
)

print(summary)
```

**Why:** Named aggregation syntax `(column, function)` lets you control output column names directly in the `.agg()` call — cleaner than renaming afterwards.
</details>

---

<a id="q10"></a>

### Q10 · groupby advanced — transform vs agg 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Using the same user scores DataFrame, add a `group_mean` column that shows each user's average score broadcast back to every row (same shape as input). Then compute a z-score normalized `score_z` within each group.


<details>
<summary>💡 Hint</summary>
`transform()` returns the same number of rows as the input — use it instead of `agg()` when you need to add a column rather than collapse rows.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "user_id": ["A", "A", "B", "B", "B"],
    "score":   [80,  90,  70,  85,  95],
})

# transform: one value per original row, aligned to group
df["group_mean"] = df.groupby("user_id")["score"].transform("mean")

# z-score within each group
df["score_z"] = df.groupby("user_id")["score"].transform(
    lambda x: (x - x.mean()) / x.std()
)

print(df)
```

**Why:** `agg()` shrinks the DataFrame (one row per group); `transform()` keeps the original shape and broadcasts group statistics back to every row.
</details>

---

<a id="q11"></a>

### Q11 · groupby advanced — groupby+apply 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Filter out groups that have fewer than 2 samples using `groupby().filter()`. Then use `groupby().apply()` to compute the IQR (Q75 - Q25) per user group.


<details>
<summary>💡 Hint</summary>
`filter(lambda x: len(x) >= 2)` drops entire groups. `apply(lambda x: x.quantile(0.75) - x.quantile(0.25))` computes IQR per group.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "user_id": ["A", "A", "B", "B", "B", "C"],  # C has only 1 sample
    "score":   [80,  90,  70,  85,  95,  60],
})

# Drop groups with fewer than 2 rows
df_filtered = df.groupby("user_id").filter(lambda x: len(x) >= 2)
# C is dropped

# Compute IQR per group via apply
iqr_per_user = df_filtered.groupby("user_id")["score"].apply(
    lambda x: x.quantile(0.75) - x.quantile(0.25)
)

print(iqr_per_user)
```

**Why:** `filter()` removes entire groups based on a condition; `apply()` handles arbitrary per-group computations that don't fit into standard aggregation functions.
</details>

---

<a id="q12"></a>

### Q12 · groupby advanced — named aggregation 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


Using `pd.NamedAgg`, produce a summary table that includes: mean score, max score, p25 and p75 quantiles, and the count of samples — all named explicitly in the `.agg()` call.


<details>
<summary>💡 Hint</summary>
Use `pd.NamedAgg(column="score", aggfunc=...)` syntax, or the equivalent tuple shorthand `("score", func)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "user_id": ["A", "A", "B", "B", "B"],
    "score":   [80,  90,  70,  85,  95],
})

summary = df.groupby("user_id").agg(
    mean_score=pd.NamedAgg(column="score", aggfunc="mean"),
    max_score=pd.NamedAgg(column="score",  aggfunc="max"),
    p25=pd.NamedAgg(column="score",        aggfunc=lambda x: x.quantile(0.25)),
    p75=pd.NamedAgg(column="score",        aggfunc=lambda x: x.quantile(0.75)),
    n_samples=pd.NamedAgg(column="score",  aggfunc="count"),
)

print(summary)
```

**Why:** `pd.NamedAgg` makes the column-function mapping explicit and self-documenting; it's the preferred production pattern over the older dict-of-lists syntax.
</details>

---

<a id="q13"></a>

### Q13 · pivot/melt — pivot_table 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Given a sales DataFrame with columns `region`, `product`, `sales`, `units`, build a pivot table that shows total `sales` per region (rows) × product (columns), with `0` replacing missing cells and an "All" totals column.


<details>
<summary>💡 Hint</summary>
Use `pd.pivot_table(..., aggfunc="sum", fill_value=0, margins=True)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

sales = pd.DataFrame({
    "region":  ["North", "North", "South", "South"],
    "product": ["A",     "B",     "A",     "B"],
    "sales":   [100,     200,     150,     180],
    "units":   [10,      20,      15,      18],
})

pt = pd.pivot_table(
    sales,
    values="sales",
    index="region",
    columns="product",
    aggfunc="sum",
    fill_value=0,
    margins=True,
    margins_name="Total",
)

print(pt)
```

**Why:** `pivot_table()` handles duplicate (index, column) combinations via aggregation — unlike `pivot()` which raises a `ValueError` on duplicates.
</details>

---

<a id="q14"></a>

### Q14 · pivot/melt — melt wide to long 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


Convert a wide DataFrame with columns `student`, `math`, `science`, `english` into long format with columns `student`, `subject`, `score`. Each original score column should become a row.


<details>
<summary>💡 Hint</summary>
Use `df.melt(id_vars=..., value_vars=..., var_name=..., value_name=...)`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df_wide = pd.DataFrame({
    "student": ["Alice", "Bob"],
    "math":    [85,      90],
    "science": [78,      88],
    "english": [92,      75],
})

df_long = df_wide.melt(
    id_vars="student",                            # anchor — stays as-is
    value_vars=["math", "science", "english"],    # columns to collapse into rows
    var_name="subject",                           # new column: old column names
    value_name="score",                           # new column: old values
)

print(df_long)
```

**Why:** `melt()` converts wide format to long format — required before most groupby, merge, and seaborn plotting operations that expect one observation per row.
</details>

---

<a id="q15"></a>

### Q15 · pivot/melt — wide_to_long / stack 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


Take a multi-metric wide DataFrame (columns: `user_id`, `score_jan`, `score_feb`, `count_jan`, `count_feb`) and use `pd.wide_to_long()` to reshape it into long format with columns `user_id`, `month`, `score`, `count`.


<details>
<summary>💡 Hint</summary>
`pd.wide_to_long(df, stubnames=["score", "count"], i="user_id", j="month", sep="_")` handles multiple metric prefixes at once.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "user_id":    [1,   2],
    "score_jan":  [80,  70],
    "score_feb":  [85,  75],
    "count_jan":  [10,  8],
    "count_feb":  [12,  9],
})

df_long = pd.wide_to_long(
    df,
    stubnames=["score", "count"],  # metric prefixes
    i="user_id",                   # row identifier
    j="month",                     # new column for the suffix (jan/feb)
    sep="_",                       # separator between stub and suffix
    suffix=r"\w+",                 # suffix pattern (word characters)
).reset_index()

print(df_long)
```

**Why:** `pd.wide_to_long()` handles the case where multiple metrics share a suffix pattern — more concise than calling `melt()` twice and merging the results.
</details>

---

<a id="q16"></a>

### Q16 · pivot/melt — stack and unstack 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Create a DataFrame with a MultiIndex from a `pivot_table` call (rows: region, columns: product with sub-columns sales and units). Then use `stack()` to move the product level from columns into the row index, and `unstack()` to reverse it.


<details>
<summary>💡 Hint</summary>
After a `pivot_table` with multiple `values`, the columns form a MultiIndex. `stack()` rotates the innermost column level into the row index.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

sales = pd.DataFrame({
    "region":  ["North", "North", "South", "South"],
    "product": ["A",     "B",     "A",     "B"],
    "sales":   [100,     200,     150,     180],
})

pt = pd.pivot_table(sales, values="sales",
                    index="region", columns="product", aggfunc="sum")

stacked = pt.stack()      # product level moves from columns → inner index level
print(stacked)

unstacked = stacked.unstack()   # reverse: inner index → columns
print(unstacked)
```

**Why:** `stack()` and `unstack()` are the MultiIndex equivalents of `melt()` and `pivot()` — use them when working with DataFrames that already have multi-level column headers.
</details>

---

<a id="q17"></a>

### Q17 · query and eval — query() with variables 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


Filter a DataFrame to rows where `score >= min_score` and `status == target_status`, where both values are Python variables. Write the filter using `df.query()` with `@` variable injection instead of f-strings.


<details>
<summary>💡 Hint</summary>
Prefix variable names with `@` inside the query string to inject Python scope variables.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "age":    [25, 34, 45, 28],
    "score":  [88, 92, 76, 95],
    "status": ["active", "inactive", "active", "active"],
})

min_score     = 85
target_status = "active"

# @ injects Python variable — no string formatting needed
result = df.query("score >= @min_score and status == @target_status")

print(result)
```

**Why:** The `@` prefix makes the variable source explicit. Using f-strings to inject values into query strings is both fragile and a SQL-injection-style risk for user-provided inputs.
</details>

---

<a id="q18"></a>

### Q18 · query and eval — eval() for computed columns 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


Use `df.eval()` to add two new columns in a single call: `score_pct` (score divided by 100) and `composite` (score × 0.7 + age × 0.3). Then add a third column using a Python variable via `@`.


<details>
<summary>💡 Hint</summary>
Multi-line `eval()` can define multiple columns in one call using a triple-quoted string.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "age":   [25, 34, 45, 28],
    "score": [88, 92, 76, 95],
})

# Multiple column assignments in one eval call
df.eval("""
    score_pct = score / 100
    composite = score * 0.7 + age * 0.3
""", inplace=True)

# Inject a Python variable with @
baseline = 70
df.eval("score_above_baseline = score - @baseline", inplace=True)

print(df)
```

**Why:** Multi-line `eval()` computes derived columns in one compiled pass — cleaner than multiple assignment lines and avoids intermediate array allocations on large DataFrames.
</details>

---

<a id="q19"></a>

### Q19 · query and eval — chained query 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


Build a filtering pipeline that: (1) uses `eval()` to create `token_density = quality_score / token_count`, (2) then uses `query()` to keep only rows where `token_count >= 50`, `token_count <= 512`, `language == 'en'`, and `token_density >= @min_density`.


<details>
<summary>💡 Hint</summary>
`eval()` first to create the derived column, then `query()` can reference it. Multi-condition query strings use `and` not `&`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "token_count":   [40,  100, 300, 600],
    "quality_score": [3.0, 4.0, 3.5, 4.5],
    "language":      ["en", "en", "fr", "en"],
})

# Step 1: add derived column with eval
df = df.eval("token_density = quality_score / token_count")

# Step 2: filter with chained query
min_density = 0.01
df_final = df.query(
    "token_count >= 50 and token_count <= 512"
    " and language == 'en'"
    " and token_density >= @min_density"
)

print(df_final)
```

**Why:** `eval()` → `query()` is the clean pattern for pipelines that need to derive columns before filtering on them — reads like a written specification.
</details>

---

<a id="q20"></a>

### Q20 · query and eval — performance comparison 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


Write a benchmark that compares the speed of boolean indexing vs `query()` on a 500,000-row DataFrame with a three-condition filter. Use `%timeit` or `timeit.timeit()` to measure both, and explain when `query()` wins.


<details>
<summary>💡 Hint</summary>
Create a large DataFrame with `np.random`, then compare `df[(df.a > 0) & (df.b < 0.5) & (df.c >= 90)]` vs `df.query("a > 0 and b < 0.5 and c >= 90")`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd
import numpy as np
import timeit

rng = np.random.default_rng(42)
df = pd.DataFrame({
    "a": rng.standard_normal(500_000),
    "b": rng.uniform(0, 1, 500_000),
    "c": rng.integers(0, 100, 500_000),
})

# Boolean indexing: creates intermediate boolean arrays
t_bool = timeit.timeit(
    lambda: df[(df["a"] > 0) & (df["b"] < 0.5) & (df["c"] >= 90)],
    number=50
)

# query(): numexpr backend avoids intermediate allocations
t_query = timeit.timeit(
    lambda: df.query("a > 0 and b < 0.5 and c >= 90"),
    number=50
)

print(f"Boolean: {t_bool:.3f}s | Query: {t_query:.3f}s")
```

**Why:** `query()` with the `numexpr` engine avoids creating three separate boolean arrays, reducing memory pressure — the advantage grows with DataFrame size and number of conditions.
</details>

---

<a id="q21"></a>

### Q21 · sql integration — read_sql with SQLite 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


Create an in-memory SQLite database, write a DataFrame to it using `to_sql()`, then read it back using `pd.read_sql()` with a filtered SQL query.


<details>
<summary>💡 Hint</summary>
Use `sqlite3.connect(":memory:")` for a no-file-needed database. Pass the connection to both `to_sql()` and `read_sql()`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd
import sqlite3

df = pd.DataFrame({
    "prompt":        ["What is Python?", "What is ML?", "What is a tensor?"],
    "quality_score": [5, 4, 3],
    "label":         ["positive", "positive", "negative"],
})

conn = sqlite3.connect(":memory:")     # in-RAM database, no file needed

df.to_sql("training_data", conn, if_exists="replace", index=False)

df_back = pd.read_sql(
    "SELECT * FROM training_data WHERE quality_score >= 4",
    conn,
)

print(df_back)
conn.close()
```

**Why:** `sqlite3.connect(":memory:")` is the fastest way to prototype SQL-based data transformations — no server, no files, and works on any machine with Python.
</details>

---

<a id="q22"></a>

### Q22 · sql integration — to_sql with if_exists 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


Demonstrate all three `if_exists` modes of `to_sql()`: `"replace"` (drops and recreates), `"append"` (adds rows), and `"fail"` (raises if table exists). Show the row count at each step.


<details>
<summary>💡 Hint</summary>
Write batch 1 with `"replace"`, then batch 2 with `"append"`. For `"fail"`, wrap in `try/except`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd
import sqlite3

conn = sqlite3.connect(":memory:")

batch1 = pd.DataFrame({"text": ["a", "b"], "score": [4, 5]})
batch2 = pd.DataFrame({"text": ["c", "d"], "score": [3, 4]})

# replace: drop and recreate
batch1.to_sql("samples", conn, if_exists="replace", index=False)
count = pd.read_sql("SELECT COUNT(*) AS n FROM samples", conn).iloc[0, 0]
print(f"After replace: {count} rows")  # 2

# append: add rows to existing table
batch2.to_sql("samples", conn, if_exists="append", index=False)
count = pd.read_sql("SELECT COUNT(*) AS n FROM samples", conn).iloc[0, 0]
print(f"After append: {count} rows")   # 4

# fail: raises ValueError if table already exists
try:
    batch1.to_sql("samples", conn, if_exists="fail", index=False)
except ValueError as e:
    print(f"fail mode raised: {e}")

conn.close()
```

**Why:** `"replace"` is safe in development but destructive in production — always use `"append"` or `"fail"` when the table holds data you care about.
</details>

---

<a id="q23"></a>

### Q23 · sql integration — merge vs SQL JOIN 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Show the Pandas equivalent of an SQL LEFT JOIN and INNER JOIN using `pd.merge()`. Load both "tables" as DataFrames, merge on `user_id`, and verify that the left join preserves all rows from the left DataFrame even when no match exists on the right.


<details>
<summary>💡 Hint</summary>
`pd.merge(left, right, on="user_id", how="left")` is a LEFT JOIN; `how="inner"` (default) is INNER JOIN.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

users = pd.DataFrame({
    "user_id": [1, 2, 3, 4],
    "name":    ["Alice", "Bob", "Carol", "Dave"],
})

scores = pd.DataFrame({
    "user_id": [1, 2, 3],   # user 4 has no score
    "score":   [88, 92, 76],
})

# INNER JOIN: only users with scores (user 4 dropped)
inner = pd.merge(users, scores, on="user_id")
print(f"Inner join rows: {len(inner)}")   # 3

# LEFT JOIN: all users, NaN score for user 4
left = pd.merge(users, scores, on="user_id", how="left")
print(f"Left join rows: {len(left)}")     # 4
print(left)
```

**Why:** LEFT JOIN is the safe default when enriching a dataset with optional metadata — you preserve all source rows and fill gaps with `NaN` rather than silently dropping them.
</details>

---

<a id="q24"></a>

### Q24 · sql integration — read_sql_query with params 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


Use `pd.read_sql()` with a parameterized query (using `%(name)s` placeholders) to pull rows where `label = 'positive'` and `quality >= 4`. Never use f-strings to inject values into SQL — demonstrate the correct pattern.


<details>
<summary>💡 Hint</summary>
Pass a `params` dict to `pd.read_sql()`. For SQLite, use `?` placeholders and pass a list/tuple instead.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd
import sqlite3

conn = sqlite3.connect(":memory:")

df = pd.DataFrame({
    "text":    ["good example", "bad example", "great example"],
    "label":   ["positive", "negative", "positive"],
    "quality": [5, 2, 4],
})
df.to_sql("samples", conn, if_exists="replace", index=False)

# SQLite uses ? placeholders; pass values as a list
df_filtered = pd.read_sql(
    "SELECT * FROM samples WHERE label = ? AND quality >= ?",
    conn,
    params=["positive", 4],   # ← values injected safely, no SQL injection risk
)

print(df_filtered)
conn.close()
```

**Why:** Parameterized queries prevent SQL injection. Never use f-strings or string concatenation to insert values into SQL queries — even for internal pipelines where "you control the data."
</details>

---

<a id="q25"></a>

### Q25 · ml data prep — train/test split preserving index 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


Split a 1,000-row DataFrame into 70% train / 15% val / 15% test using stratified sampling on the `label` column. After splitting, verify that: (1) the three sets don't overlap, and (2) the class distribution is preserved in each split.


<details>
<summary>💡 Hint</summary>
Call `train_test_split` twice: first to carve out the 30% temp set, then to split temp 50/50 into val and test.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

rng = np.random.default_rng(42)
df = pd.DataFrame({
    "feature": rng.standard_normal(1000),
    "label":   rng.choice([0, 1], 1000, p=[0.8, 0.2]),  # imbalanced
})

# Step 1: 70% train, 30% temp
df_train, df_temp = train_test_split(
    df, test_size=0.30, stratify=df["label"], random_state=42
)

# Step 2: split temp into 15% val, 15% test
df_val, df_test = train_test_split(
    df_temp, test_size=0.50, stratify=df_temp["label"], random_state=42
)

# Verify no overlap
assert set(df_train.index).isdisjoint(set(df_val.index))
assert set(df_train.index).isdisjoint(set(df_test.index))

for name, split in [("train", df_train), ("val", df_val), ("test", df_test)]:
    dist = split["label"].value_counts(normalize=True).round(3)
    print(f"{name}: {dist.to_dict()}")
```

**Why:** `stratify=` preserves class ratios across splits — without it, a random split could put nearly all of the rare class in one split, making evaluation unreliable.
</details>

---

<a id="q26"></a>

### Q26 · ml data prep — StandardScaler on DataFrame 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)


Standardize numeric feature columns using training-set statistics only. Fit the mean and std on `df_train`, then apply the same transformation to `df_val` and `df_test`. Verify that the training set has approximately mean=0 and std=1 after scaling.


<details>
<summary>💡 Hint</summary>
Compute `mean` and `std` from `df_train` only, then apply `(x - mean) / std` to all three splits. Never `fit_transform` on val or test.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd
import numpy as np

feature_cols = ["age", "score", "latency_ms"]

# Fit stats on TRAINING SET ONLY
train_mean = df_train[feature_cols].mean()
train_std  = df_train[feature_cols].std().replace(0, 1)  # avoid division by zero

# Apply to all splits using training stats
df_train[feature_cols] = (df_train[feature_cols] - train_mean) / train_std
df_val[feature_cols]   = (df_val[feature_cols]   - train_mean) / train_std
df_test[feature_cols]  = (df_test[feature_cols]  - train_mean) / train_std

# Verify
print(df_train[feature_cols].mean().round(4))   # should be ~0
print(df_train[feature_cols].std().round(4))    # should be ~1
```

**Why:** Fitting the scaler on val or test data leaks test-set statistics into the model's training process — a subtle but severe form of data leakage.
</details>

---

<a id="q27"></a>

### Q27 · ml data prep — one-hot encoding get_dummies 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)


One-hot encode a `color` column (values: `"red"`, `"blue"`, `"green"`) using `pd.get_dummies()`. Use `drop_first=True` to avoid multicollinearity, and use `dtype=int` so the output is integers rather than booleans.


<details>
<summary>💡 Hint</summary>
`pd.get_dummies(df, columns=["color"], drop_first=True, dtype=int)` drops one category to avoid the dummy variable trap.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "item":  ["hat", "shirt", "shoes", "bag"],
    "color": ["red", "blue", "green", "red"],
    "price": [20,    35,     50,      15],
})

df_encoded = pd.get_dummies(
    df,
    columns=["color"],
    drop_first=True,    # drops "blue" to avoid multicollinearity (k-1 dummies)
    prefix="color",     # column names: color_green, color_red
    dtype=int,          # 0/1 integers instead of True/False booleans
)

print(df_encoded.columns.tolist())
print(df_encoded)
```

**Why:** `drop_first=True` removes one dummy column (the "reference category") — linear models need this to avoid perfect collinearity among the encoded columns.
</details>

---

<a id="q28"></a>

### Q28 · ml data prep — impute missing values 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)


Handle missing values in a DataFrame: fill numeric column `age` with the training-set median, fill categorical column `region` with `"unknown"`, and drop any rows where the `label` column is null. Apply all changes without using `inplace=True`.


<details>
<summary>💡 Hint</summary>
Compute median from `df_train["age"]` only. Use `fillna()` and `dropna(subset=["label"])`, always assigning back.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

# Compute imputation value from training data only
age_median = df_train["age"].median()

# Apply to all splits
df_train["age"]    = df_train["age"].fillna(age_median)
df_val["age"]      = df_val["age"].fillna(age_median)
df_test["age"]     = df_test["age"].fillna(age_median)

# Fill categorical missing with placeholder
df_train["region"] = df_train["region"].fillna("unknown")
df_val["region"]   = df_val["region"].fillna("unknown")
df_test["region"]  = df_test["region"].fillna("unknown")

# Drop rows with missing target — never impute labels
df_train = df_train.dropna(subset=["label"])
df_val   = df_val.dropna(subset=["label"])

print(f"Train nulls: {df_train.isnull().sum().sum()}")
```

**Why:** Using training-set statistics for imputation on val/test avoids leakage. Labels must never be imputed — a row with an unknown target cannot be a valid training or evaluation example.
</details>

---

<a id="q29"></a>

### Q29 · data validation — assert dtypes 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)


Write a function that accepts a DataFrame and an expected schema dict (`{column: dtype_string}`) and raises a `ValueError` listing all type mismatches and missing columns. Test it with a DataFrame that has a wrong dtype.


<details>
<summary>💡 Hint</summary>
Compare `str(df[col].dtype)` against the expected string. Collect all violations before raising.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

def validate_schema(df, expected_schema):
    violations = []
    for col, expected in expected_schema.items():
        if col not in df.columns:
            violations.append(f"MISSING: '{col}'")
        elif str(df[col].dtype) != expected:
            violations.append(
                f"TYPE_MISMATCH: '{col}' expected={expected} actual={df[col].dtype}"
            )
    if violations:
        raise ValueError("Schema validation failed:\n" + "\n".join(violations))
    print("Schema OK")

df = pd.DataFrame({
    "user_id": ["a", "b"],
    "score":   [1.0, 2.0],
    "label":   ["0", "1"],    # ← wrong dtype: should be int64
})

SCHEMA = {"user_id": "object", "score": "float64", "label": "int64"}

try:
    validate_schema(df, SCHEMA)
except ValueError as e:
    print(e)
```

**Why:** Catching dtype mismatches at ingestion time — before any computation — prevents silent numeric errors like treating integer labels as strings in a loss function.
</details>

---

<a id="q30"></a>

### Q30 · data validation — check for nulls 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)


Write a null-rate audit that: (1) prints the null count and null rate per column, (2) raises an error if any "critical" column has any nulls at all, and (3) warns (but does not raise) if any column has a null rate above 5%.


<details>
<summary>💡 Hint</summary>
`df.isnull().mean()` gives the rate per column. Use `assert` for critical columns.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

def null_audit(df, critical_cols=None, max_null_rate=0.05):
    report = pd.DataFrame({
        "null_count": df.isnull().sum(),
        "null_rate":  df.isnull().mean().round(4),
    }).sort_values("null_rate", ascending=False)

    print(report[report["null_count"] > 0])

    # Hard fail on critical columns
    if critical_cols:
        for col in critical_cols:
            n = df[col].isnull().sum()
            assert n == 0, f"Critical column '{col}' has {n} nulls"

    # Soft warning on high null rate
    high = report[report["null_rate"] > max_null_rate]
    for col, row in high.iterrows():
        print(f"WARNING: '{col}' null rate = {row['null_rate']:.1%}")

null_audit(df, critical_cols=["label", "score"], max_null_rate=0.05)
```

**Why:** Separating "hard failures" (critical columns must have zero nulls) from "soft warnings" (high null rate columns) lets a pipeline fail fast on showstoppers while logging issues that need investigation.
</details>

---

<a id="q31"></a>

### Q31 · data validation — validate value ranges 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q31](./practice_local.py)


Assert that a `score` column is within [0, 100], a `probability` column is within [0.0, 1.0], and an `age` column is within [0, 120]. For any violation, include the actual min and max in the error message.


<details>
<summary>💡 Hint</summary>
Use `df["col"].between(low, high).all()` with `assert`, and include `df["col"].min()` and `df["col"].max()` in the message.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.DataFrame({
    "score":       [0, 50, 100, 105],   # 105 is out of range
    "probability": [0.0, 0.5, 1.0, 0.3],
    "age":         [0, 25, 90, 120],
})

range_checks = {
    "score":       (0, 100),
    "probability": (0.0, 1.0),
    "age":         (0, 120),
}

for col, (low, high) in range_checks.items():
    ok = df[col].between(low, high).all()
    assert ok, (
        f"'{col}' out of range [{low}, {high}]: "
        f"min={df[col].min()}, max={df[col].max()}"
    )
```

**Why:** Including the actual min/max in the error message makes it immediately actionable — you see the bad value without having to re-run queries to diagnose it.
</details>

---

<a id="q32"></a>

### Q32 · data validation — schema validation with pandera 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q32](./practice_local.py)


Use `pandera` to define a `DataFrameSchema` that enforces: `score` is float in [0.0, 100.0], `label` is integer in {0, 1}, `source` is a non-null string. Validate a DataFrame against it and handle the `SchemaError` gracefully.


<details>
<summary>💡 Hint</summary>
Use `pa.DataFrameSchema({"col": pa.Column(dtype, checks=[pa.Check...])})`. `pa.Check.isin()` validates allowed values.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd
import pandera as pa

schema = pa.DataFrameSchema({
    "score": pa.Column(
        float,
        checks=[pa.Check.ge(0.0), pa.Check.le(100.0)],
        nullable=False,
    ),
    "label": pa.Column(
        int,
        checks=[pa.Check.isin([0, 1])],
        nullable=False,
    ),
    "source": pa.Column(str, nullable=False),
})

df = pd.DataFrame({
    "score":  [85.0, 92.0, -5.0],   # -5 violates ge(0)
    "label":  [0,    1,    2],       # 2 violates isin([0, 1])
    "source": ["reddit", "news", "arxiv"],
})

try:
    schema.validate(df, lazy=True)   # lazy=True collects ALL errors, not just first
except pa.errors.SchemaErrors as e:
    print(e.failure_cases)           # DataFrame of failing rows and checks
```

**Why:** `pandera` provides declarative schema validation that reads like a contract — far more maintainable than scattered `assert` statements, and `lazy=True` gives you all failures at once.
</details>

---

<a id="q33"></a>

### Q33 · performance — astype category 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q33](./practice_local.py)


Convert a `status` column (values: `"active"`, `"inactive"`, `"pending"`) from `object` dtype to `category` dtype. Measure the memory usage before and after. Also demonstrate setting `dtype='category'` at CSV read time.


<details>
<summary>💡 Hint</summary>
Use `.memory_usage(deep=True)` to compare bytes before and after. At read time, pass `dtype={"status": "category"}` to `read_csv`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd
import numpy as np

rng = np.random.default_rng(42)
df = pd.DataFrame({
    "status": rng.choice(["active", "inactive", "pending"], size=1_000_000)
})

before = df["status"].memory_usage(deep=True)
print(f"Before (object): {before / 1e6:.1f} MB")

df["status"] = df["status"].astype("category")  # stores integers + 3-entry lookup

after = df["status"].memory_usage(deep=True)
print(f"After (category): {after / 1e6:.1f} MB")
print(f"Reduction: {(1 - after/before):.1%}")

# At read time (best practice for large CSVs):
# df = pd.read_csv("data.csv", dtype={"status": "category", "region": "category"})
```

**Why:** For 1M rows with 3 unique values, `category` dtype stores 3 strings once plus 1M small integers — versus `object` storing 1M full string pointers. Typical reduction is 10–50x.
</details>

---

<a id="q34"></a>

### Q34 · performance — query over boolean mask 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q34](./practice_local.py)


Compare `query()` and boolean indexing on a 300,000-row DataFrame with a two-condition filter involving a `@variable`. Show that `query()` with the `numexpr` engine avoids intermediate array allocations and explain when it is and is not faster.


<details>
<summary>💡 Hint</summary>
Use `engine="numexpr"` explicitly in `query()`. Time both with `timeit`. Note: `query()` has string-parsing overhead that makes it slower on tiny DataFrames.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd
import numpy as np
import timeit

rng = np.random.default_rng(42)
df = pd.DataFrame({
    "price":  rng.uniform(10, 500, 300_000),
    "status": rng.choice(["active", "inactive"], 300_000),
})

threshold = 100.0

# Boolean indexing: creates two intermediate boolean arrays
t1 = timeit.timeit(
    lambda: df[(df["price"] > threshold) & (df["status"] == "active")],
    number=100,
)

# query() with numexpr: single compiled pass, no intermediate arrays
t2 = timeit.timeit(
    lambda: df.query("price > @threshold and status == 'active'",
                     engine="numexpr"),
    number=100,
)

print(f"Boolean: {t1:.3f}s | Query: {t2:.3f}s")
# query() wins on large DataFrames; boolean wins on small ones (< ~10k rows)
```

**Why:** `query()` parsing overhead dominates on small DataFrames; the `numexpr` savings only outweigh that cost at ~10k+ rows with multiple conditions.
</details>

---

<a id="q35"></a>

### Q35 · performance — chunked read_csv 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q35](./practice_local.py)


Read a large CSV file in chunks of 100,000 rows. For each chunk, filter to rows where `quality_score >= 3`, compute a derived column `text_len`, and collect only rows where `text_len > 50`. Combine all filtered chunks into a final DataFrame.


<details>
<summary>💡 Hint</summary>
Pass `chunksize=100_000` to `pd.read_csv()` — it returns an iterator. Filter each chunk before appending to keep memory constant.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

results = []

for chunk in pd.read_csv("large_dataset.csv", chunksize=100_000):
    # Filter and derive before accumulating — keeps memory usage constant
    chunk = chunk[chunk["quality_score"] >= 3]
    chunk["text_len"] = chunk["text"].str.len()
    chunk = chunk[chunk["text_len"] > 50]
    results.append(chunk)

df_final = pd.concat(results, ignore_index=True)
print(f"Final rows: {len(df_final):,}")
```

**Why:** Processing and filtering each chunk before collecting it keeps memory usage proportional to `chunksize`, not to total file size — the key to handling files that don't fit in RAM.
</details>

---

<a id="q36"></a>

### Q36 · performance — vectorized vs apply benchmark 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q36](./practice_local.py)


Benchmark four approaches for cleaning a 500,000-row text column (strip + lowercase): (1) Python loop with `iterrows()`, (2) `apply(lambda x: ...)`, (3) `.str` accessor chain, (4) `numpy.vectorize`. Report the speedups and explain why the `.str` accessor wins for string operations.


<details>
<summary>💡 Hint</summary>
Use `timeit.timeit()` with `number=5` for the slow methods and `number=100` for fast ones. Expect `iterrows` to be ~100–1000x slower than `.str`.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd
import numpy as np
import timeit

rng = np.random.default_rng(42)
texts = rng.choice(["  Hello World  ", "  PANDAS  ", "  test data  "], 500_000)
df = pd.DataFrame({"text": texts})

# Method 1: iterrows (Python loop — very slow)
t1 = timeit.timeit(
    lambda: [row["text"].strip().lower() for _, row in df.iterrows()],
    number=1,
)

# Method 2: apply with lambda (Python loop via apply)
t2 = timeit.timeit(
    lambda: df["text"].apply(lambda x: x.strip().lower()),
    number=5,
) / 5

# Method 3: .str accessor chain (vectorized C code)
t3 = timeit.timeit(
    lambda: df["text"].str.strip().str.lower(),
    number=50,
) / 50

# Method 4: numpy.vectorize (still a Python loop, just wrapped)
vfunc = np.vectorize(lambda x: x.strip().lower())
t4 = timeit.timeit(
    lambda: vfunc(df["text"].values),
    number=10,
) / 10

print(f"iterrows:  {t1:.3f}s")
print(f"apply:     {t2:.3f}s")
print(f"np.vect:   {t4:.3f}s")
print(f".str:      {t3:.3f}s  ← winner")
```

**Why:** `.str.strip().str.lower()` delegates to Cython/C-level string operations on the entire array in one pass. `apply()` and `np.vectorize()` are both Python-speed loops — `np.vectorize` is not actually vectorized, it just hides the loop.
</details>
