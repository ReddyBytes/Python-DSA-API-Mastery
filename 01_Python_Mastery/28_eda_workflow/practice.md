# EDA Workflow — Practice

## Quick Index

| # | Chapter | Topic | Difficulty |
|---|---------|-------|------------|
| Q1 | Ch1 EDA Checklist | Order of operations | 🟢 |
| Q2 | Ch1 EDA Checklist | What EDA catches | 🟢 |
| Q3 | Ch2 Loading & Shape | read_csv + shape | 🟢 |
| Q4 | Ch2 Loading & Shape | df.info() vs df.describe() | 🟢 |
| Q5 | Ch2 Loading & Shape | dtypes inspection | 🟢 |
| Q6 | Ch2 Loading & Shape | head vs tail vs sample | 🟢 |
| Q7 | Ch3 Missing Values | isnull summary table | 🟡 |
| Q8 | Ch3 Missing Values | Missing value heatmap | 🟡 |
| Q9 | Ch3 Missing Values | fillna strategies by threshold | 🟡 |
| Q10 | Ch3 Missing Values | Drop vs impute decision | 🟡 |
| Q11 | Ch4 Distributions | Histogram grid | 🟢 |
| Q12 | Ch4 Distributions | Boxplot for outlier shape | 🟢 |
| Q13 | Ch4 Distributions | Skewness check | 🟡 |
| Q14 | Ch4 Distributions | Log transform for skewed | 🟡 |
| Q15 | Ch5 Categorical Features | value_counts | 🟢 |
| Q16 | Ch5 Categorical Features | Bar chart for low-cardinality | 🟢 |
| Q17 | Ch5 Categorical Features | Cardinality classification | 🟡 |
| Q18 | Ch5 Categorical Features | Rare category handling | 🟡 |
| Q19 | Ch6 Target Variable | Class balance check | 🟡 |
| Q20 | Ch6 Target Variable | Target distribution plot | 🟢 |
| Q21 | Ch6 Target Variable | Imbalance strategies | 🟠 |
| Q22 | Ch7 Correlations & Outliers | Correlation heatmap | 🟡 |
| Q23 | Ch7 Correlations & Outliers | IQR outlier detection | 🟡 |
| Q24 | Ch7 Correlations & Outliers | Z-score outliers | 🟡 |
| Q25 | Ch7 Correlations & Outliers | Scatter matrix | 🟡 |
| Q26 | Ch7 Correlations & Outliers | VIF for multicollinearity | 🟠 |
| Q27 | Ch8 Automated EDA | ydata-profiling | 🟢 |
| Q28 | Ch8 Automated EDA | sweetviz comparison | 🟡 |
| Q29 | Ch8 Automated EDA | dtale interactive | 🟡 |
| Q30 | Ch8 Automated EDA | When to use each tool | 🟠 |

---

## Ch1 — EDA Checklist

---

### Q1 · Ch1 EDA Checklist — Order of operations 🟢

You receive a CSV with 50 columns and 100,000 rows. List the correct order of the 10 EDA phases a senior engineer would follow before touching any model code.

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)

<details><summary>💡 Hint</summary>Start with shape, then types, then quality, then distributions, then relationships.</details>

<details><summary>✅ Answer</summary>

```python
# The 10-phase EDA order:
# 1.  Load and inspect shape           — df.shape, df.info(), df.dtypes
# 2.  Column names and types           — rename, cast, verify
# 3.  Missing values                   — df.isnull().sum()
# 4.  Duplicates                       — df.duplicated().sum()
# 5.  Distributions (numeric)          — histograms, skewness
# 6.  Cardinality and frequencies      — value_counts() per categorical
# 7.  Target variable analysis         — distribution, class balance
# 8.  Correlation analysis             — heatmap, top-N with target
# 9.  Outlier detection                — IQR or Z-score per column
# 10. Feature-target relationships     — scatter plots, boxplots
```

**Why:** Quality checks (steps 3–4) must come before analysis — you can't trust distributions computed on dirty data.
</details>

---

### Q2 · Ch1 EDA Checklist — What EDA catches 🟢

A junior engineer skips EDA and trains a model immediately. Name five specific problems the model will silently suffer from that EDA would have caught.

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)

<details><summary>💡 Hint</summary>Think: quality bugs, type bugs, leakage, imbalance, scale bugs.</details>

<details><summary>✅ Answer</summary>

```python
# Five problems EDA catches that silent training misses:

# 1. Wrong dtypes — dates stored as strings, so date math silently fails
# 2. Missing values — NaN rows silently dropped or zero-filled by sklearn
# 3. Data leakage — a feature derived from the target gives 99% accuracy
#    that collapses in production
# 4. Class imbalance — a 95:5 split means a model that always predicts
#    the majority class gets 95% accuracy while being completely useless
# 5. Heavily skewed targets — regression on raw house prices (skew=3.5)
#    loses all predictive signal in the long tail
```

**Why:** All five bugs produce models that look plausible in training but fail in production.
</details>

---

## Ch2 — Loading & Shape

---

### Q3 · Ch2 Loading & Shape — read_csv + shape 🟢

Load a CSV file called `sales.csv` and print: total rows, total columns, and whether any column has a non-default index.

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)

<details><summary>💡 Hint</summary>df.shape returns a tuple. df.index tells you about the index type.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

df = pd.read_csv("sales.csv")

rows, cols = df.shape                          # unpack tuple
print(f"Rows: {rows}, Columns: {cols}")        # ← total dimensions

# Check if index is default integer range
is_default = isinstance(df.index, pd.RangeIndex)
print(f"Default integer index: {is_default}")  # False = custom index
```

**Why:** `df.shape` is the fastest first sanity check — if rows or columns is unexpectedly zero or huge, something went wrong at load time.
</details>

---

### Q4 · Ch2 Loading & Shape — df.info() vs df.describe() 🟢

Explain what `df.info()` and `df.describe()` each show, and when you would use one over the other.

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)

<details><summary>💡 Hint</summary>One shows column metadata. The other shows statistical summaries.</details>

<details><summary>✅ Answer</summary>

```python
df.info()
# Shows: column name, non-null count, dtype, total memory usage
# Use when: checking for wrong types or unexpected nulls

df.describe()
# Shows: count, mean, std, min, 25%, 50%, 75%, max — numeric only
# Use when: checking ranges, spotting impossible values, comparing spreads

df.describe(include="all")
# Also adds: unique, top, freq for categorical columns
# Use when: you want one-shot summary of every column type

# Quick rule: info() = column health; describe() = numeric statistics
```

**Why:** `info()` catches structural problems (nulls, wrong types); `describe()` catches value problems (impossible ranges, high skew).
</details>

---

### Q5 · Ch2 Loading & Shape — dtypes inspection 🟢

A DataFrame has a column `transaction_date` stored as `object` dtype. Write code to detect this and convert it to proper datetime.

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)

<details><summary>💡 Hint</summary>Use df.dtypes to find object columns, then pd.to_datetime() to cast.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

# Detect object columns that look like dates
date_cols = [col for col in df.columns
             if df[col].dtype == object
             and "date" in col.lower()]        # ← name heuristic

# Convert
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce")  # errors="coerce" → NaT on failure
    print(f"{col}: {df[col].dtype}")           # should now show datetime64[ns]

# Verify no parse failures
null_after = df[date_cols].isnull().sum()
print(null_after)                              # new NaTs = rows that couldn't parse
```

**Why:** Date columns stored as strings break all time-based features — `.dt.year`, `.dt.dayofweek`, date arithmetic all fail silently.
</details>

---

### Q6 · Ch2 Loading & Shape — head vs tail vs sample 🟢

Why is `df.sample(10)` often more useful than `df.head(10)` for spotting data issues?

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)

<details><summary>💡 Hint</summary>Think about how data is often ordered in a CSV — by time, by ID, by category.</details>

<details><summary>✅ Answer</summary>

```python
df.head(10)     # always shows rows 0–9
                # problem: data sorted by date → head = all 2019 rows
                #          data sorted by class → head = all class 0 rows

df.tail(10)     # always shows last 10 rows
                # same bias problem in reverse

df.sample(10, random_state=42)  # random 10 rows from anywhere
                                # catches: mixed encodings, weird nulls in later rows,
                                #          rare categories that only appear mid-dataset

# Best practice: use all three
print(df.head(3))
print(df.tail(3))
print(df.sample(5, random_state=0))
```

**Why:** CSV files are often sorted by date or ID — `head()` shows only the earliest/lowest-ID rows, missing the full diversity of the data.
</details>

---

## Ch3 — Missing Values

---

### Q7 · Ch3 Missing Values — isnull summary table 🟡

Build a missing value summary DataFrame showing each column's missing count and percentage, sorted by percentage descending, filtered to only columns with any missing values.

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)

<details><summary>💡 Hint</summary>Combine isnull().sum() and a percentage calculation into a DataFrame, then query and sort.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

missing_count = df.isnull().sum()                         # ← absolute count per column
missing_pct   = (missing_count / len(df) * 100).round(2) # ← percentage per column

summary = pd.DataFrame({
    "missing_count": missing_count,
    "missing_pct":   missing_pct,
}).query("missing_count > 0") \
  .sort_values("missing_pct", ascending=False)

print(summary)
# Output example:
#             missing_count  missing_pct
# salary                120        24.0
# age                    50        10.0
```

**Why:** Sorting by percentage lets you immediately see which columns are candidates for dropping (>30%) vs imputing.
</details>

---

### Q8 · Ch3 Missing Values — Missing value heatmap 🟡

Use the `missingno` library to visualize whether missing values in two columns occur together (correlated missingness).

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)

<details><summary>💡 Hint</summary>msno.heatmap shows correlation between missingness patterns across columns.</details>

<details><summary>✅ Answer</summary>

```python
import missingno as msno  # pip install missingno

# Matrix view: white gaps = missing, black bars = present
msno.matrix(df)            # ← visual scan across all columns

# Heatmap: correlation of missingness between column pairs
msno.heatmap(df)
# A value close to 1.0 → these two columns go missing together
# (same survey skipped, same time window, same sensor failure)

# Dendrogram: clusters columns by similar missingness patterns
msno.dendrogram(df)
```

**Why:** If salary and bonus always go missing together, they were probably collected from the same source — impute them together or drop both.
</details>

---

### Q9 · Ch3 Missing Values — fillna strategies by threshold 🟡

Write a function that receives a DataFrame and applies the correct imputation strategy based on each column's missing percentage: drop rows for <5%, median-impute for 5–30%, and drop the column for >30%.

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)

<details><summary>💡 Hint</summary>Compute pct per column, then branch on the threshold with separate pandas operations.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

def smart_impute(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pct = df.isnull().mean() * 100          # ← fraction missing per column

    drop_cols   = pct[pct > 30].index.tolist()   # too many missing → drop column
    impute_cols = pct[(pct > 5) & (pct <= 30)].index.tolist()  # moderate → median
    drop_row_cols = pct[(pct > 0) & (pct <= 5)].index.tolist() # tiny → drop rows

    df = df.drop(columns=drop_cols)              # ← drop high-missing columns
    for col in impute_cols:
        df[col] = df[col].fillna(df[col].median())  # ← median imputation
    df = df.dropna(subset=drop_row_cols)         # ← drop rows with tiny missing

    return df
```

**Why:** Using a fixed threshold strategy avoids ad-hoc decisions and makes the pipeline reproducible.
</details>

---

### Q10 · Ch3 Missing Values — Drop vs impute decision 🟡

When should you create a separate `col_was_missing` binary indicator column instead of just imputing or dropping?

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)

<details><summary>💡 Hint</summary>Think about MNAR — Missing Not at Random.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd
import numpy as np

# MNAR example: income is blank only for people who refused to report it
# The fact that it's missing is itself a signal — these may be high earners

df["income_was_missing"] = df["income"].isnull().astype(int)  # ← binary flag
df["income"] = df["income"].fillna(df["income"].median())      # ← then impute

# When to add missingness indicator:
# - MNAR: missingness correlates with the target
# - When you expect the model to learn: "if income unknown → predict X"
# - Test by checking: df.groupby("income_was_missing")["target"].mean()
#   If means differ significantly → the missingness is predictive → keep flag

print(df.groupby("income_was_missing")["target"].mean())
```

**Why:** Dropping or blindly imputing MNAR data discards a signal — the "why" of missingness predicts the target.
</details>

---

## Ch4 — Distributions

---

### Q11 · Ch4 Distributions — Histogram grid 🟢

Plot a grid of histograms for all numeric columns in a DataFrame using a single `plt.subplots` call.

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)

<details><summary>💡 Hint</summary>Use axes.flatten() to iterate axes alongside columns in a zip.</details>

<details><summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt

numeric_cols = df.select_dtypes(include="number").columns

fig, axes = plt.subplots(3, 4, figsize=(16, 10))  # ← adjust grid to column count

for ax, col in zip(axes.flatten(), numeric_cols):
    df[col].hist(bins=30, ax=ax, edgecolor="white", color="steelblue")
    ax.set_title(col, fontsize=10)

# Hide empty subplots if fewer columns than grid cells
for ax in axes.flatten()[len(numeric_cols):]:
    ax.set_visible(False)

plt.suptitle("Numeric Feature Distributions", fontsize=14)
plt.tight_layout()
plt.show()
```

**Why:** Seeing all distributions together at once lets you spot the right-skewed, bimodal, and near-constant columns in one glance.
</details>

---

### Q12 · Ch4 Distributions — Boxplot for outlier shape 🟢

Create a side-by-side plot showing a histogram and a boxplot for the same column. What does each tell you that the other doesn't?

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)

<details><summary>💡 Hint</summary>Histogram shows shape and modes; boxplot shows quartiles and outlier points explicitly.</details>

<details><summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt
import seaborn as sns

col = "income"
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Histogram — shows the shape and where mass is concentrated
df[col].hist(bins=50, ax=ax1, color="steelblue", edgecolor="white")
ax1.set_title(f"{col} — Histogram")

# Boxplot — shows IQR box, whiskers at 1.5*IQR, and outlier dots beyond
sns.boxplot(y=df[col], ax=ax2, color="coral")
ax2.set_title(f"{col} — Boxplot")

plt.tight_layout()
# Histogram: reveals bimodal distributions, skew direction
# Boxplot:   reveals exact outlier count, median vs mean separation
```

**Why:** Boxplot outlier dots are explicit data points above/below 1.5×IQR — the histogram just shows a long tail without counting them.
</details>

---

### Q13 · Ch4 Distributions — Skewness check 🟡

Write code that prints the skewness of every numeric column and flags any column with absolute skewness greater than 1.

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)

<details><summary>💡 Hint</summary>Use scipy.stats.skew or pandas Series.skew().</details>

<details><summary>✅ Answer</summary>

```python
from scipy import stats

numeric_cols = df.select_dtypes(include="number").columns

for col in numeric_cols:
    series = df[col].dropna()
    skew_val = stats.skew(series)               # ← scipy skewness
    flag = " ← highly skewed" if abs(skew_val) > 1 else ""
    print(f"{col:20s}  skew={skew_val:+.2f}{flag}")

# Rules of thumb:
# skew ~0        → roughly symmetric (safe for linear models)
# |skew| 0.5–1  → moderate skew
# |skew| > 1    → highly skewed → log transform recommended
# |skew| > 2    → very heavy tail (common in income, price, count data)
```

**Why:** Highly skewed features violate the normality assumption of linear models and cause gradient-based learners to focus disproportionately on tail values.
</details>

---

### Q14 · Ch4 Distributions — Log transform for skewed 🟡

A `price` column has skewness of 3.2. Apply a log transform and verify that skewness dropped below 1.

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)

<details><summary>💡 Hint</summary>Use np.log1p (not np.log) to handle zeros safely.</details>

<details><summary>✅ Answer</summary>

```python
import numpy as np
from scipy import stats

before_skew = stats.skew(df["price"].dropna())
print(f"Before: skew = {before_skew:.2f}")     # e.g. 3.20

df["price_log"] = np.log1p(df["price"])        # log(1 + x) handles 0s safely
after_skew = stats.skew(df["price_log"].dropna())
print(f"After:  skew = {after_skew:.2f}")      # should be < 1

# Why log1p and not log?
# np.log(0) = -inf  → breaks everything
# np.log1p(0) = 0   → safe; for large values log1p(x) ≈ log(x)

# Other options if log1p isn't enough:
# np.sqrt(df["price"])         — gentler than log
# df["price"] ** (1/3)        — cube root
# scipy.stats.boxcox(df["price"])  — finds optimal power transform
```

**Why:** log1p compresses the long right tail so that extreme values no longer dominate the loss function during model training.
</details>

---

## Ch5 — Categorical Features

---

### Q15 · Ch5 Categorical Features — value_counts 🟢

Print the top 10 values and their percentage share for a categorical column `city`. Show both absolute count and normalized frequency.

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)

<details><summary>💡 Hint</summary>value_counts() has a normalize parameter for percentages.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

col = "city"
counts = df[col].value_counts().head(10)            # ← absolute count
pcts   = df[col].value_counts(normalize=True).mul(100).round(1).head(10)  # ← %

summary = pd.DataFrame({"count": counts, "pct": pcts})
print(summary)

# Output:
#             count   pct
# New York      430  14.3
# Los Angeles   280   9.3
# ...

# Also useful: missing in value_counts
print(f"Null count: {df[col].isnull().sum()}")  # nulls not shown in value_counts
```

**Why:** `value_counts()` alone hides what fraction each category represents — showing both absolute and percentage prevents misreading rare categories as significant.
</details>

---

### Q16 · Ch5 Categorical Features — Bar chart for low-cardinality 🟢

Plot a horizontal bar chart of value counts for any categorical column with fewer than 15 unique values.

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)

<details><summary>💡 Hint</summary>Filter columns by nunique() <= 15, then use .plot(kind="barh").</details>

<details><summary>✅ Answer</summary>

```python
import matplotlib.pyplot as plt

cat_cols = df.select_dtypes(include=["object", "category"]).columns

for col in cat_cols:
    if df[col].nunique() <= 15:                    # ← low cardinality only
        fig, ax = plt.subplots(figsize=(8, 4))
        df[col].value_counts().plot(
            kind="barh",                           # ← horizontal = long labels fit
            ax=ax,
            color="steelblue"
        )
        ax.set_title(f"{col} — Value Counts")
        ax.set_xlabel("Count")
        plt.tight_layout()
        plt.show()
```

**Why:** Horizontal bars are better than vertical when category names are long — no overlapping tick labels.
</details>

---

### Q17 · Ch5 Categorical Features — Cardinality classification 🟡

Write a function that classifies every categorical column by cardinality and prints the recommended encoding strategy.

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)

<details><summary>💡 Hint</summary>Low < 10, Medium 10–100, High > 100 — each has a different encoding strategy.</details>

<details><summary>✅ Answer</summary>

```python
def classify_cardinality(df):
    cat_cols = df.select_dtypes(include=["object", "category"]).columns

    for col in cat_cols:
        n = df[col].nunique()

        if n < 10:
            strategy = "OHE or ordinal encoding"     # ← low: few dummies
        elif n <= 100:
            strategy = "target encoding or embedding" # ← medium: OHE too wide
        else:
            strategy = "likely ID — consider dropping or hashing"

        print(f"{col:25s}  nunique={n:5d}  → {strategy}")

classify_cardinality(df)
# product_category        nunique=    6  → OHE or ordinal encoding
# zip_code                nunique= 1842  → likely ID — consider dropping
```

**Why:** One-hot encoding a 1000-category column creates 1000 sparse features — most tree models handle this poorly and linear models become extremely wide.
</details>

---

### Q18 · Ch5 Categorical Features — Rare category handling 🟡

A `product_type` column has 50 categories, but 40 of them appear fewer than 20 times each. Write code to group rare categories into an `"Other"` bucket.

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)

<details><summary>💡 Hint</summary>Use value_counts to find rare categories, then Series.where() or map() to replace them.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

col = "product_type"
threshold = 20                                         # ← min count to keep

counts = df[col].value_counts()
rare_categories = counts[counts < threshold].index    # ← categories below threshold

df[col] = df[col].where(
    ~df[col].isin(rare_categories),                   # ← keep if not rare
    other="Other"                                     # ← replace rare with "Other"
)

print(df[col].value_counts())
# Electronics     5200
# Clothing        3100
# Other            840   ← all 40 rare categories merged
```

**Why:** Rare categories don't provide reliable statistical signal and inflate feature space — grouping them into "Other" reduces noise without losing the common patterns.
</details>

---

## Ch6 — Target Variable

---

### Q19 · Ch6 Target Variable — Class balance check 🟡

For a binary classification target `churn`, print class counts and flag if the imbalance ratio exceeds 5:1.

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)

<details><summary>💡 Hint</summary>value_counts(normalize=True) gives proportions; compute the ratio between majority and minority.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

target = "churn"
counts = df[target].value_counts()
pcts   = df[target].value_counts(normalize=True)

print("Class distribution:")
for cls in counts.index:
    print(f"  {cls}: {counts[cls]:,d}  ({pcts[cls]*100:.1f}%)")

# Check imbalance ratio
majority = counts.max()
minority = counts.min()
ratio = majority / minority
print(f"\nImbalance ratio: {ratio:.1f}:1")

if ratio > 10:
    print("SEVERE imbalance — use SMOTE + class_weight='balanced'")
elif ratio > 5:
    print("MODERATE imbalance — use class_weight='balanced'")
else:
    print("Acceptable balance")
```

**Why:** A 95:5 split means a classifier that always predicts "no churn" gets 95% accuracy — class balance determines whether accuracy is even a valid metric.
</details>

---

### Q20 · Ch6 Target Variable — Target distribution plot 🟢

Plot the raw distribution and log-transformed distribution of a regression target `price` side by side.

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)

<details><summary>💡 Hint</summary>Two subplots — one for raw, one for np.log1p transformed.</details>

<details><summary>✅ Answer</summary>

```python
import numpy as np
import matplotlib.pyplot as plt

target = "price"
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

df[target].hist(bins=50, ax=ax1, color="steelblue", edgecolor="white")
ax1.set_title(f"Target: {target} (raw)")
ax1.set_xlabel(target)

np.log1p(df[target]).hist(bins=50, ax=ax2, color="coral", edgecolor="white")
ax2.set_title(f"Target: log(1 + {target})")
ax2.set_xlabel(f"log(1 + {target})")

skew_raw = df[target].skew()
skew_log = np.log1p(df[target]).skew()
print(f"Raw skew: {skew_raw:.2f}  |  Log skew: {skew_log:.2f}")

plt.tight_layout()
plt.show()
```

**Why:** A bell-shaped target distribution after log transform means the model's residuals are more evenly distributed — linear regression assumptions are better satisfied.
</details>

---

### Q21 · Ch6 Target Variable — Imbalance strategies 🟠

List three strategies for handling a severe class imbalance (10:1 ratio) and explain the trade-off of each.

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)

<details><summary>💡 Hint</summary>Think: resampling (SMOTE), algorithmic (class_weight), metric (F1 vs accuracy).</details>

<details><summary>✅ Answer</summary>

```python
# Strategy 1: class_weight="balanced" (algorithmic)
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(class_weight="balanced")
# Trade-off: simple, no data change, but may overfit minority class

# Strategy 2: SMOTE — Synthetic Minority Oversampling Technique
from imblearn.over_sampling import SMOTE
sm = SMOTE(random_state=42)
X_res, y_res = sm.fit_resample(X_train, y_train)
# Trade-off: creates synthetic minority samples → bigger dataset
#            risk: synthetic samples may not reflect real distribution

# Strategy 3: Threshold tuning (post-hoc)
# Default threshold = 0.5 → biased toward majority
# Lower threshold → more minority predictions
y_proba = model.predict_proba(X_test)[:, 1]
y_pred_tuned = (y_proba >= 0.3).astype(int)  # ← lower threshold
# Trade-off: simple, no retraining, but requires calibrated probabilities

# Always use F1 / AUC-ROC, never raw accuracy, for imbalanced data
```

**Why:** Each strategy attacks imbalance at a different stage — data level (SMOTE), training level (class_weight), or prediction level (threshold) — combining them often works best.
</details>

---

## Ch7 — Correlations & Outliers

---

### Q22 · Ch7 Correlations & Outliers — Correlation heatmap 🟡

Plot a correlation heatmap for all numeric columns. Then print the top 5 features most correlated with the target, sorted by absolute correlation.

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)

<details><summary>💡 Hint</summary>Use sns.heatmap with annot=True. Sort corr[target].drop(target).abs().</details>

<details><summary>✅ Answer</summary>

```python
import seaborn as sns
import matplotlib.pyplot as plt

target = "price"
corr = df.select_dtypes(include="number").corr()

# Heatmap
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    vmin=-1, vmax=1,        # ← fix color scale to [-1, 1]
    square=True,
    ax=ax
)
plt.title("Correlation Matrix")
plt.tight_layout()

# Top 5 features by absolute correlation with target
top5 = (
    corr[target]
    .drop(target)
    .abs()
    .sort_values(ascending=False)
    .head(5)
)
print("Top 5 features correlated with target:")
print(top5)
```

**Why:** Sorting by absolute value surfaces both strongly positive and strongly negative predictors — a -0.8 correlation is just as predictive as +0.8.
</details>

---

### Q23 · Ch7 Correlations & Outliers — IQR outlier detection 🟡

Write a reusable function that returns a boolean mask of IQR outliers for any numeric Series, with a configurable fence factor (default 1.5).

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)

<details><summary>💡 Hint</summary>Compute Q1, Q3, IQR, then lower/upper bounds. Return (series < lower) | (series > upper).</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd

def iqr_outliers(series: pd.Series, factor: float = 1.5) -> pd.Series:
    """Returns boolean mask: True where value is an IQR outlier."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - factor * IQR   # ← fence below
    upper = Q3 + factor * IQR   # ← fence above
    return (series < lower) | (series > upper)

# Apply to all numeric columns
for col in df.select_dtypes(include="number").columns:
    mask = iqr_outliers(df[col].dropna())
    n = mask.sum()
    pct = 100 * n / len(mask)
    print(f"{col:20s}  {n:4d} outliers  ({pct:.1f}%)")

# To use stricter fences for financial data:
# iqr_outliers(df["salary"], factor=3.0)
```

**Why:** The 1.5×IQR fence is Tukey's standard — it flags roughly 0.7% of a normal distribution as outliers. Use 3.0 for a gentler filter.
</details>

---

### Q24 · Ch7 Correlations & Outliers — Z-score outliers 🟡

Detect outliers in an `income` column using Z-scores. Explain when Z-score is better than IQR and when IQR is better.

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)

<details><summary>💡 Hint</summary>Z = (x - mean) / std. Flag |Z| > 3. Compare against IQR robustness.</details>

<details><summary>✅ Answer</summary>

```python
from scipy import stats
import pandas as pd

col = "income"
series = df[col].dropna()

z_scores = stats.zscore(series)                      # ← (x - mean) / std
outlier_mask = abs(z_scores) > 3                     # ← standard threshold
print(f"Z-score outliers: {outlier_mask.sum()}")

# When to use Z-score vs IQR:
#
# Z-score is better when:
#   - Data is approximately normally distributed
#   - You want a statistically grounded definition (3 sigma = 0.27% of normal)
#   - Features need to be compared on the same scale
#
# IQR is better when:
#   - Data is skewed (income, price, counts) — mean/std get pulled by outliers
#   - You want a robust method (IQR isn't affected by extreme values)
#   - Dataset is small (sample mean is less reliable)
#
# Rule of thumb: IQR first, Z-score if data is confirmed normal
```

**Why:** Z-score uses mean and std which are themselves distorted by outliers — IQR is robust precisely because it's based on quartiles that extreme values can't shift.
</details>

---

### Q25 · Ch7 Correlations & Outliers — Scatter matrix 🟡

Create a scatter matrix (pairplot) for the four most correlated numeric features with the target. Color points by a binary categorical column.

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)

<details><summary>💡 Hint</summary>Use sns.pairplot with hue parameter. Select columns first to keep it readable.</details>

<details><summary>✅ Answer</summary>

```python
import seaborn as sns
import matplotlib.pyplot as plt

target = "price"
corr = df.select_dtypes(include="number").corr()

# Pick top 4 features by correlation with target
top4 = (
    corr[target]
    .drop(target)
    .abs()
    .sort_values(ascending=False)
    .head(4)
    .index.tolist()
)
plot_cols = top4 + [target]

# Scatter matrix with categorical color
sns.pairplot(
    df[plot_cols + ["category_col"]].dropna(),
    hue="category_col",         # ← color by category
    diag_kind="kde",            # ← KDE on diagonal instead of histogram
    plot_kws={"alpha": 0.5}     # ← semi-transparent to see overlap
)
plt.suptitle("Scatter Matrix — Top Features vs Target", y=1.02)
plt.show()
```

**Why:** Pairplot reveals non-linear relationships, clusters, and interactions that the correlation coefficient (a single number) completely misses.
</details>

---

### Q26 · Ch7 Correlations & Outliers — VIF for multicollinearity 🟠

Compute the Variance Inflation Factor (VIF) for all numeric features in a DataFrame and flag any column with VIF > 10.

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)

<details><summary>💡 Hint</summary>Use statsmodels variance_inflation_factor. It requires a design matrix with a constant column.</details>

<details><summary>✅ Answer</summary>

```python
import pandas as pd
import numpy as np
from statsmodels.stats.outliers_influence import variance_inflation_factor

def compute_vif(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include="number").dropna()
    X = numeric.assign(const=1)                         # ← add intercept constant

    vif_data = pd.DataFrame({
        "feature": numeric.columns,
        "VIF": [
            variance_inflation_factor(X.values, i)
            for i in range(len(numeric.columns))        # ← compute per feature
        ]
    }).sort_values("VIF", ascending=False)

    return vif_data

vif = compute_vif(df)
print(vif)
print("\nHigh VIF features (> 10):")
print(vif[vif["VIF"] > 10])

# VIF interpretation:
# 1       → no multicollinearity
# 1–5     → moderate, usually acceptable
# 5–10    → high, monitor
# > 10    → severe — consider dropping one of the correlated pair
```

**Why:** Two features with correlation 0.95 will both have VIF > 10 — keeping both tells the model the same thing twice and inflates coefficient variance in linear models.
</details>

---

## Ch8 — Automated EDA

---

### Q27 · Ch8 Automated EDA — ydata-profiling 🟢

Generate a full HTML EDA report for a DataFrame using ydata-profiling in one code block.

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)

<details><summary>💡 Hint</summary>ProfileReport(df, explorative=True).to_file("report.html")</details>

<details><summary>✅ Answer</summary>

```python
# pip install ydata-profiling
from ydata_profiling import ProfileReport

report = ProfileReport(
    df,
    title="My EDA Report",
    explorative=True,    # ← enables deep analysis (correlations, interactions)
    minimal=False        # ← set True for very large datasets to skip expensive steps
)

report.to_file("eda_report.html")   # ← open in browser
# or in a notebook:
# report.to_notebook_iframe()

# What the report includes automatically:
# - Overview: row/col counts, missing %, duplicate count
# - Per-column: distribution, top values, correlations
# - Correlations: Pearson, Spearman, Kendall heatmaps
# - Missing value matrix
# - Interactions: scatter plots between selected pairs
# - Warnings: high cardinality, skewness, near-constant columns
```

**Why:** A full ydata-profiling report covers 80% of manual EDA in one line — it's the standard starting point for any new dataset.
</details>

---

### Q28 · Ch8 Automated EDA — sweetviz comparison 🟡

Use sweetviz to generate a comparison report between a training set and a test set to detect distribution shift.

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)

<details><summary>💡 Hint</summary>sv.compare([df_train, "Train"], [df_test, "Test"]).show_html()</details>

<details><summary>✅ Answer</summary>

```python
# pip install sweetviz
import sweetviz as sv

# Single dataset analysis
train_report = sv.analyze(df_train, target_feat="price")
train_report.show_html("train_eda.html")

# Side-by-side comparison of train vs test
compare_report = sv.compare(
    [df_train, "Train"],   # ← source dataset with label
    [df_test,  "Test"],    # ← compare dataset with label
    target_feat="price"    # ← optional: highlight target column
)
compare_report.show_html("train_vs_test.html")

# What to look for in comparison:
# - Feature distributions that differ significantly → train/test mismatch
# - Target distribution difference → potential data leakage boundary
# - Missing value % differences → different collection pipeline
```

**Why:** Train/test distribution shift is a common silent bug — a feature that has 5% nulls in train but 40% nulls in test will cause the model to fail in production.
</details>

---

### Q29 · Ch8 Automated EDA — dtale interactive 🟡

Launch dtale for an interactive browser-based EDA session on a DataFrame.

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)

<details><summary>💡 Hint</summary>import dtale; dtale.show(df).open_browser()</details>

<details><summary>✅ Answer</summary>

```python
# pip install dtale
import dtale

# Launch interactive UI in browser
d = dtale.show(df)
d.open_browser()   # ← opens localhost:40000 in default browser

# From a Jupyter notebook:
# dtale.show(df)   # ← renders inline in cell output

# dtale capabilities:
# - Sort, filter, and search rows interactively
# - Column analysis: histogram, value counts, boxplot per column
# - Correlation matrix with drill-down scatter plots
# - Chart builder: drag-and-drop any plot type
# - Code export: generates the pandas code for any operation you do
# - Highlight: flag missing values, outliers, or custom conditions
```

**Why:** dtale is the fastest way to explore a new dataset hands-on — you can filter to outlier rows, drill into a suspicious column, and export the pandas code, all without writing a single line.
</details>

---

### Q30 · Ch8 Automated EDA — When to use each tool 🟠

You have three automated EDA tools: ydata-profiling, sweetviz, and dtale. Describe the ideal use case for each and the situation where you would not rely on automated EDA alone.

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)

<details><summary>💡 Hint</summary>Think: report sharing, comparison tasks, interactive exploration, domain knowledge gaps.</details>

<details><summary>✅ Answer</summary>

```python
# Tool selection guide:

# ydata-profiling — best for:
#   - First look at a completely new dataset
#   - Generating a shareable HTML report for stakeholders
#   - Large teams where everyone needs the same baseline EDA
#   - Detecting warnings automatically (skewness, high cardinality, imbalance)
#   Limitation: slow on large datasets (>1M rows); use minimal=True

# sweetviz — best for:
#   - Comparing train vs test or pre/post split distributions
#   - Comparing two populations (A vs B, treatment vs control)
#   - Quick visual comparison alongside target variable
#   Limitation: no interactivity — output is static HTML

# dtale — best for:
#   - Hands-on interactive exploration, ad-hoc filtering
#   - Sharing with analysts who prefer a spreadsheet-like interface
#   - Generating pandas code from GUI operations
#   Limitation: not reproducible — no code trail unless you export

# When NOT to rely on automated EDA alone:
#   - Domain knowledge issues: an "impossible" value (age=150) won't be flagged
#     unless you know the business rule
#   - Data leakage: a column named "future_outcome" needs domain expertise
#   - Time series: ordering matters; automated tools treat rows as independent
#   - Complex feature interactions: automated tools show pairwise; 3-way
#     interactions require manual hypothesis-driven analysis
```

**Why:** Automated EDA is a starting point, not a finish line — it handles the mechanical checks but can't replace a data scientist who understands what the values should mean.
</details>

---

## Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| ⬅️ Prev Module | [../27_matplotlib_seaborn/theory.md](../27_matplotlib_seaborn/theory.md) |
| ➡️ Next Module | [../29_web_scraping/theory.md](../29_web_scraping/theory.md) |

**[Back to README](../README.md)**
