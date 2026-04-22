# 🔍 EDA — Exploratory Data Analysis Workflow

---

You get a new dataset. You're supposed to build a model. Where do you start?

The junior engineer opens a notebook and immediately starts training. The senior engineer opens the same notebook and spends the first hour *understanding the data*. They check what columns exist. They look at distributions. They find the hidden column with 80% missing values. They discover that the target column has a data type error — dates stored as strings. They notice two columns that are almost perfectly correlated (probable data leakage).

By the time the senior engineer starts modeling, they've avoided five different ways the model could silently fail. The junior engineer's model is already training — on corrupted data — and will produce a result that looks plausible but is wrong.

**Exploratory Data Analysis (EDA)** is the systematic process of understanding a dataset before modeling.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
`df.info()` · `df.describe()` · `df.isnull().sum()` · Value counts · Distribution plots · Correlation matrix · Outlier detection

**Should Learn** — Important for real projects, comes up regularly:
`pandas_profiling` / `ydata-profiling` · Duplicate detection · Cardinality analysis · Target leakage detection · Time series stationarity checks

**Good to Know** — Useful in specific situations:
`sweetviz` · `dtale` · `lux` · Advanced missing data patterns (MCAR/MAR/MNAR) · Cross-feature interaction analysis

**Reference** — Know it exists, look up when needed:
`missingno` library · Geospatial EDA · `pandas-visual-analysis`

---

## 1️⃣ The EDA Checklist

Every EDA follows roughly the same sequence:

```
Step 1: Load and inspect shape
Step 2: Column names, types, and basic info
Step 3: Missing values
Step 4: Duplicates
Step 5: Distributions (numeric)
Step 6: Cardinality and frequencies (categorical)
Step 7: Target variable analysis
Step 8: Correlation analysis
Step 9: Outlier detection
Step 10: Feature-target relationships
```

---

## 2️⃣ Phase 1 — Loading and Shape

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data.csv")

# Basic shape
print(df.shape)          # (rows, columns)
print(df.dtypes)         # data type per column
print(df.info())         # dtypes + non-null count + memory usage
print(df.head(5))        # first rows
print(df.tail(5))        # last rows
print(df.sample(5))      # random rows (better for spotting patterns)

# Numeric summary
print(df.describe())              # count, mean, std, quartiles — only numeric
print(df.describe(include="all")) # include categoricals too
```

---

## 3️⃣ Phase 2 — Missing Values

```python
# Missing value summary
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)

summary = pd.DataFrame({
    "missing_count": missing,
    "missing_pct": missing_pct
}).query("missing_count > 0").sort_values("missing_pct", ascending=False)

print(summary)

# Visualize missing value pattern
import missingno as msno   # pip install missingno
msno.matrix(df)            # white = missing, black = present
msno.heatmap(df)           # correlation of missingness between columns

# Thresholds
# < 5% missing: safe to drop rows or impute
# 5-30% missing: impute carefully (mean/median/KNN)
# > 30% missing: consider dropping the column or creating missingness indicator
```

---

## 4️⃣ Phase 3 — Distributions

```python
# Numeric columns — distribution overview
fig, axes = plt.subplots(3, 4, figsize=(16, 10))
numeric_cols = df.select_dtypes(include="number").columns

for ax, col in zip(axes.flatten(), numeric_cols):
    df[col].hist(bins=30, ax=ax, edgecolor="white", color="steelblue")
    ax.set_title(col, fontsize=10)

plt.suptitle("Numeric Feature Distributions")
plt.tight_layout()

# Single column — detailed
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
df["price"].hist(bins=50, ax=ax1)
ax1.set_title("Price Distribution")
np.log1p(df["price"]).hist(bins=50, ax=ax2, color="coral")
ax2.set_title("Log(1 + Price) Distribution")   # log transform often reveals structure
```

---

## 5️⃣ Phase 4 — Categorical Features

```python
cat_cols = df.select_dtypes(include=["object", "category"]).columns

for col in cat_cols:
    n_unique = df[col].nunique()
    top_values = df[col].value_counts().head(10)
    print(f"\n{col}: {n_unique} unique values")
    print(top_values)

# Cardinality categories
# Low (< 10): likely ordinal or nominal — use OHE or ordinal encoding
# Medium (10-100): consider target encoding or embedding
# High (> 100): ID-like — probably should be dropped or hashed

# Bar chart for low-cardinality features
for col in cat_cols:
    if df[col].nunique() <= 15:
        fig, ax = plt.subplots(figsize=(8, 4))
        df[col].value_counts().plot(kind="bar", ax=ax)
        ax.set_title(f"{col} Value Counts")
        ax.tick_params(axis="x", rotation=45)
        plt.tight_layout()
```

---

## 6️⃣ Phase 5 — Target Variable

```python
target = "price"

# Distribution
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
df[target].hist(bins=50, ax=axes[0])
axes[0].set_title(f"Target: {target}")

np.log1p(df[target]).hist(bins=50, ax=axes[1], color="coral")
axes[1].set_title(f"Log({target})")

# Class balance (classification)
print(df[target].value_counts(normalize=True))
# Imbalance > 10:1 ratio → need SMOTE or class weights
```

---

## 7️⃣ Phase 6 — Correlations and Outliers

```python
# Correlation matrix
corr = df.select_dtypes(include="number").corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
plt.title("Correlation Matrix")
plt.tight_layout()

# Correlations with target
target_corr = corr[target].drop(target).sort_values(ascending=False)
print("Features most correlated with target:")
print(target_corr)

# Outlier detection with IQR
def flag_outliers(series, factor=1.5):
    Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
    IQR = Q3 - Q1
    lower, upper = Q1 - factor * IQR, Q3 + factor * IQR
    return (series < lower) | (series > upper)

outlier_counts = {col: flag_outliers(df[col]).sum()
                  for col in df.select_dtypes(include="number").columns}
print(pd.Series(outlier_counts).sort_values(ascending=False))
```

---

## 8️⃣ Automated EDA

```python
# ydata-profiling (formerly pandas-profiling)
# pip install ydata-profiling
from ydata_profiling import ProfileReport

report = ProfileReport(df, title="EDA Report", explorative=True)
report.to_file("eda_report.html")    # open in browser for full interactive report

# sweetviz (comparison between datasets)
# pip install sweetviz
import sweetviz as sv

train_report = sv.analyze(df_train)
compare_report = sv.compare([df_train, "Train"], [df_test, "Test"])
compare_report.show_html("comparison.html")
```

---

## Common Mistakes to Avoid ⚠️

- **Skipping EDA and going straight to modeling**: EDA catches problems that silently poison models — missing values, wrong dtypes, data leakage, class imbalance.
- **Not checking for duplicates**: duplicate rows inflate evaluation metrics and cause overfitting.
- **Treating ID-like columns as features**: user_id, transaction_id have high cardinality and are not predictors — always check and drop them.
- **Ignoring the target variable distribution**: a heavily skewed target (house prices) often needs a log transform before regression.
- **Checking correlations but not checking for non-linear relationships**: scatter plots reveal U-shapes, thresholds, and interactions that correlation coefficients miss.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Prev Module | [../27_matplotlib_seaborn/theory.md](../27_matplotlib_seaborn/theory.md) |
| ➡️ Next Module | [../29_web_scraping/theory.md](../29_web_scraping/theory.md) |

---

**[🏠 Back to README](../README.md)**
