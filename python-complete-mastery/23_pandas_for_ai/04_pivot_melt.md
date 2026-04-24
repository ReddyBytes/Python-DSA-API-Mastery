# 🎯 Pandas Pivot, Melt, and Reshaping — Wide ↔ Long

Imagine a spreadsheet showing monthly sales figures where each month (Jan, Feb, Mar...) gets its own column. That format is easy to scan and looks great in a report — but try running a `groupby` on it and you are stuck. Now imagine a database table where every row is a single observation: one date, one value, one label. That is harder to eyeball but trivially easy to filter, aggregate, and merge. Data scientists call these **wide format** and **long format**, and they constantly reshape between them depending on whether they are building a model, running an analysis, or presenting results. Pandas gives you four core tools — `pivot_table`, `melt`, `stack`, and `unstack` — to flip between these shapes instantly.

---

## 📐 Section 1: Wide vs Long Format

Think of wide format like a pivot report on a whiteboard and long format like a database table behind it. Both hold the same data — they just organize it differently.

**Wide format** has one row per entity and one column per variable. It is compact and readable. The problem: adding a new variable means adding a new column, and most Pandas/ML operations (groupby, merge, seaborn plots) expect the data unpacked as rows.

**Long format** has one row per observation — one entity, one variable, one value. It is verbose but analysis-friendly. Most data pipelines, tidy data principles, and ML feature pipelines expect this shape.

Here is the same data in both shapes:

**Wide:**

| student | math | science | english |
|---------|------|---------|---------|
| Alice   | 85   | 78      | 92      |
| Bob     | 90   | 88      | 75      |

**Long:**

| student | subject | score |
|---------|---------|-------|
| Alice   | math    | 85    |
| Alice   | science | 78    |
| Alice   | english | 92    |
| Bob     | math    | 90    |
| Bob     | science | 88    |
| Bob     | english | 75    |

Wide is great for display. Long is great for analysis. You need both, and you need to move between them cleanly.

---

## 🔄 Section 2: melt() — Wide to Long

`melt()` is the "unpacker." It takes columns and folds them down into rows. Think of it like pulling a wide accordion inward — fewer columns, more rows, same total information.

The key mental model: you have **anchor columns** (identifiers that stay fixed, like `student`) and **measurement columns** (the variables you want to collapse into rows, like `math`, `science`, `english`). After melting, each measurement column becomes a value in a new `subject` column, and its data moves into a new `score` column.

```python
import pandas as pd

df_wide = pd.DataFrame({
    'student': ['Alice', 'Bob'],
    'math': [85, 90],
    'science': [78, 88],
    'english': [92, 75]
})

df_long = df_wide.melt(
    id_vars='student',                          # ← anchor columns — these stay as-is
    value_vars=['math', 'science', 'english'],  # ← columns to collapse into rows
    var_name='subject',                         # ← name of the new column holding old column names
    value_name='score'                          # ← name of the new column holding old values
)

print(df_long)
```

Result:

```
  student  subject  score
0   Alice     math     85
1     Bob     math     90
2   Alice  science     78
3     Bob  science     88
4   Alice  english     92
5     Bob  english     75
```

**`id_vars`** are your identity anchors — they repeat for every melted row. **`value_vars`** are the columns being dissolved. **`var_name`** and **`value_name`** control what the two new columns are called. If you omit `value_vars`, Pandas melts every column that is not in `id_vars`.

---

## 🔃 Section 3: pivot() — Long to Wide (Simple)

`pivot()` is the inverse of `melt()`. It takes a long table and fans it back out into a wide table. Think of opening the accordion back up — rows become columns again.

The three arguments map directly to: what becomes the row labels, what becomes the column headers, and what fills the cells.

```python
# df.pivot(index, columns, values)
df_wide_again = df_long.pivot(
    index='student',    # ← becomes the row index
    columns='subject',  # ← unique values here become new column names
    values='score'      # ← these values fill the cells
)

print(df_wide_again)
```

Result:

```
subject  english  math  science
student
Alice         92    85       78
Bob           75    90       88
```

One critical limitation: **`pivot()` requires uniqueness**. If your (index, columns) combination appears more than once in the data, pivot raises a `ValueError`. For example, if Alice has two math scores, pivot cannot decide which one to place in the cell.

That is exactly when you reach for `pivot_table()`.

---

## 📊 Section 4: pivot_table() — Aggregated Reshaping

`pivot_table()` is the Excel pivot table brought into Python. It handles duplicates by aggregating them — you decide how (sum, mean, count, or a custom function). It is the production-grade version of `pivot()`.

Think of it as a cross-tabulation with math: for every (row, column) combination, it applies your aggregation function to all matching values. This is what you want when your data has repeats, multiple metrics, or when you need subtotals.

```python
import pandas as pd

sales = pd.DataFrame({
    'region':  ['North', 'North', 'South', 'South'],
    'product': ['A', 'B', 'A', 'B'],
    'sales':   [100, 200, 150, 180],
    'units':   [10, 20, 15, 18]
})

pt = pd.pivot_table(
    sales,
    values=['sales', 'units'],    # ← which columns to aggregate
    index='region',               # ← row dimension
    columns='product',            # ← column dimension
    aggfunc='sum',                # ← aggregation: 'sum', 'mean', 'count', or per-column dict
    fill_value=0                  # ← replace NaN cells with 0
)

print(pt)
```

Result:

```
        sales       units
product     A    B      A   B
region
North     100  200     10  20
South     150  180     15  18
```

Add **`margins=True`** to get row and column subtotals (an "All" row and column):

```python
pt_with_totals = pd.pivot_table(
    sales,
    values='sales',
    index='region',
    columns='product',
    aggfunc='sum',
    margins=True,      # ← adds an "All" row and "All" column
    margins_name='Total'
)
```

For per-column aggregation, pass a dict to `aggfunc`:

```python
aggfunc={'sales': 'sum', 'units': 'mean'}  # ← different functions per value column
```

---

## 🗂️ Section 5: stack() and unstack() — Multi-Index Reshaping

Once your DataFrame has a **multi-level index** (MultiIndex), `stack()` and `unstack()` become your primary reshaping tools. Think of the index as a filing cabinet with multiple drawer levels — `stack()` pulls one column level down into a drawer, `unstack()` pushes one drawer level back up into columns.

`stack()` rotates the innermost column level into the innermost row index level (wide to long at the index level). `unstack()` does the reverse.

```python
import pandas as pd

df = pd.DataFrame(
    {'A': [1, 2], 'B': [3, 4]},
    index=['x', 'y']
)

stacked = df.stack()   # ← columns A, B become an inner index level
print(stacked)
```

Result:

```
x  A    1
   B    3
y  A    2
   B    4
dtype: int64
```

```python
print(stacked.unstack())       # ← reverses stack, back to original shape
print(stacked.unstack(level=0)) # ← unstack a different level → different wide shape
```

**`stack()`** is useful when you get data with multi-level column headers (common after a `pivot_table` with multiple `values`). **`unstack()`** is useful when you have a MultiIndex Series or DataFrame and want to spread one level back into columns for display or modeling.

For DataFrames with a simple single-level index, `melt` and `pivot` are usually cleaner. Reserve `stack`/`unstack` for multi-level index situations.

---

## 🧮 Section 6: crosstab() — Frequency Tables

`crosstab()` counts how often combinations of two categorical variables co-occur. It is essentially a pivot table that always counts. The classic AI/ML application: **confusion matrices**.

Think of it as asking "how many times did X happen together with Y?" — it builds the answer into a grid automatically.

```python
import pandas as pd

labels_true = pd.Series(['cat', 'dog', 'cat', 'cat', 'dog'])  # ← ground truth
labels_pred = pd.Series(['cat', 'dog', 'dog', 'cat', 'cat'])  # ← model predictions

cm = pd.crosstab(labels_true, labels_pred)
print(cm)
```

Result:

```
col_0  cat  dog
row_0
cat      2    1
dog      1    1
```

This is a confusion matrix built with pure Pandas — no sklearn needed for quick spot-checks.

Add **`normalize`** to convert counts to proportions:

```python
pd.crosstab(labels_true, labels_pred, normalize='all')   # ← proportions over total
pd.crosstab(labels_true, labels_pred, normalize='index') # ← proportions per true label (row)
pd.crosstab(labels_true, labels_pred, normalize='columns') # ← proportions per predicted label
```

Add **`margins=True`** for row and column totals:

```python
pd.crosstab(
    labels_true,
    labels_pred,
    margins=True,          # ← adds "All" row and column
    margins_name='Total'
)
```

---

## 🤖 Section 7: Real AI/ML Use Cases

Reshaping is not just a data cleaning step — it shows up throughout the ML pipeline.

**Feature engineering for model input.** Most models (sklearn, XGBoost, PyTorch tabular) expect one row per sample and one column per feature — that is wide format. When your raw data arrives in long format (a time-series log, event stream, or sensor feed), you pivot it wide before passing it to `model.fit()`.

```python
# Long: (user_id, feature_name, feature_value) → Wide: one column per feature
features_wide = features_long.pivot_table(
    index='user_id',
    columns='feature_name',
    values='feature_value',
    aggfunc='last',     # ← take the most recent value if duplicates exist
    fill_value=0
)
```

**Evaluation with confusion matrices.** `crosstab` gives you a quick confusion matrix without importing sklearn, useful in notebooks and data validation steps.

```python
pd.crosstab(y_true, y_pred, normalize='index')  # ← normalized confusion matrix
```

**Time-series correlation analysis.** Pivot a long `(timestamp, metric, value)` table into wide `(timestamp × metric)` format to run `.corr()` across metrics.

```python
ts_wide = ts_long.pivot_table(
    index='timestamp',
    columns='metric',
    values='value',
    aggfunc='mean'
)
correlation_matrix = ts_wide.corr()  # ← pairwise Pearson correlation
```

**Cleaning variable-width data before groupby.** Raw data often comes with one column per time period or category — a common survey or reporting format. Melt it first, then groupby cleanly.

```python
df_melted = df_raw.melt(id_vars=['id', 'region'], var_name='month', value_name='revenue')
df_melted.groupby(['region', 'month'])['revenue'].sum()  # ← now this works cleanly
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⬅️ Prev Topic | [03_groupby_advanced.md](./03_groupby_advanced.md) |
| ➡️ Next Topic | [05_query_and_eval.md](./05_query_and_eval.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
