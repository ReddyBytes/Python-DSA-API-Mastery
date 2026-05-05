# 🔍 EDA Workflow — Cheatsheet

## EDA Checklist

```
[ ] 1. df.shape / df.info() / df.dtypes
[ ] 2. df.isnull().sum() — missing values
[ ] 3. df.duplicated().sum() — duplicates
[ ] 4. df.describe() — numeric summary
[ ] 5. df[col].value_counts() — categorical frequencies
[ ] 6. Distribution plots for each numeric column
[ ] 7. Correlation heatmap
[ ] 8. Target variable distribution
[ ] 9. Feature-target relationships
[ ] 10. Outlier detection (IQR or Z-score)
```

---

## Quick Inspection

```python
df.shape                              # (rows, cols)
df.dtypes                             # column types
df.info()                             # dtypes + non-null + memory
df.head(); df.tail(); df.sample(5)    # peek at data
df.describe()                         # numeric summary
df.describe(include="all")            # all columns
df.nunique()                          # unique values per column
df.duplicated().sum()                 # number of duplicate rows
df.drop_duplicates(inplace=True)      # remove duplicates
```

---

## Missing Values

```python
# Summary
missing = df.isnull().sum()
pct = missing / len(df) * 100
pd.DataFrame({"count": missing, "pct": pct}).query("count > 0").sort_values("pct", ascending=False)

# Per-row missing count
df.isnull().sum(axis=1).value_counts()

# Thresholds
# < 5%  → impute or drop rows
# 5-30% → impute with mean/median/mode or KNN
# >30%  → consider dropping column or adding missingness indicator
```

---

## Distributions

```python
# All numeric columns at once
df.select_dtypes("number").hist(bins=30, figsize=(16, 10))
plt.tight_layout()

# Single column
df["col"].hist(bins=50)
sns.histplot(df["col"], kde=True)
sns.boxplot(y=df["col"])

# Check skewness
from scipy import stats
stats.skew(df["col"].dropna())   # > 1 or < -1: consider log transform

# Log transform for right-skewed data
import numpy as np
df["col_log"] = np.log1p(df["col"])   # log1p = log(1+x) handles zeros
```

---

## Categorical Analysis

```python
cat_cols = df.select_dtypes(include=["object", "category"]).columns

# Cardinality
df[cat_cols].nunique()

# Value counts
df["col"].value_counts()
df["col"].value_counts(normalize=True)   # as percentages

# Top-N bar chart
df["col"].value_counts().head(10).plot(kind="bar")
```

---

## Correlation

```python
import seaborn as sns

corr = df.select_dtypes("number").corr()

# Heatmap
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, square=True)

# Top correlations with target
corr["target"].drop("target").abs().sort_values(ascending=False).head(10)

# Flag high inter-feature correlations (possible multicollinearity)
high_corr = (corr.abs() > 0.9) & (corr != 1.0)
corr.where(high_corr).stack().reset_index()
```

---

## Outlier Detection

```python
# IQR method
Q1 = df["col"].quantile(0.25)
Q3 = df["col"].quantile(0.75)
IQR = Q3 - Q1
lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
outliers = df[(df["col"] < lower) | (df["col"] > upper)]

# Z-score method
from scipy import stats
z_scores = stats.zscore(df["col"].dropna())
outliers = df[abs(z_scores) > 3]

# Visualize
sns.boxplot(x=df["col"])   # shows IQR box + whiskers + outlier dots
```

---

## Target Analysis

```python
# Regression target
df["target"].hist(bins=50)
print(f"Skewness: {df['target'].skew():.2f}")
# If skewed: try log(target) or sqrt(target)

# Classification target
df["target"].value_counts(normalize=True)
# Imbalanced if any class < 10% of majority class

# Feature-target relationships
for col in numeric_cols:
    print(f"{col}: corr={df[col].corr(df['target']):.3f}")

# Categorical features vs numeric target
sns.boxplot(x="category_col", y="target", data=df)
```

---

## Automated EDA

```python
# ydata-profiling — one command full report
from ydata_profiling import ProfileReport
ProfileReport(df, explorative=True).to_file("report.html")

# sweetviz — train vs test comparison
import sweetviz as sv
sv.compare([df_train, "Train"], [df_test, "Test"]).show_html("comparison.html")
```

---

## Common Data Quality Issues to Check

| Issue | How to Detect |
|---|---|
| Wrong dtypes (dates as strings) | `df.dtypes` + try `pd.to_datetime()` |
| Duplicates | `df.duplicated().sum()` |
| Impossible values (age=-5) | `df.describe()` min/max |
| High cardinality IDs as features | `df.nunique()` |
| Leaking future data | Check if feature is derived from target |
| Constant columns | `df.nunique() == 1` |
| Near-constant columns | `df.nunique() <= 2` |

---

## Golden Rules

1. Always look at the data before touching it — `df.sample(10)` shows more than `df.head()`
2. Check missing values and duplicates before every analysis
3. Log-transform right-skewed numeric targets before regression
4. Correlation heatmap is the fastest way to spot leakage and multicollinearity
5. Automated tools (ydata-profiling) save time — but don't skip manual inspection of suspicious columns
