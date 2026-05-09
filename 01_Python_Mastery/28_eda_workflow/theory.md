<a id="top"></a>
# 🔍 EDA — Exploratory Data Analysis Workflow

## 📖 Table of Contents

- [Learning Priority](#-learning-priority)
- [1. The EDA Checklist](#1-the-eda-checklist)
- [2. Phase 1 — Loading and Shape](#2-phase-1--loading-and-shape)
- [3. Phase 2 — Missing Values](#3-phase-2--missing-values)
- [4. Phase 3 — Distributions](#4-phase-3--distributions)
- [5. Phase 4 — Categorical Features](#5-phase-4--categorical-features)
- [6. Phase 5 — Target Variable](#6-phase-5--target-variable)
- [7. Phase 6 — Correlations and Outliers](#7-phase-6--correlations-and-outliers)
- [8. Automated EDA](#8-automated-eda)
- [Summary](#-summary)
- [Navigation](#-navigation)

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

You get a new dataset. The junior engineer opens a notebook and immediately starts training. The senior engineer spends the first hour understanding the data — they find the column with 80% missing values, the target column with dates stored as strings, the two features that are almost perfectly correlated (probable data leakage). By the time the senior starts modeling, they've avoided five ways the model could silently fail. **Exploratory Data Analysis (EDA)** is that systematic process of understanding a dataset before modeling.

---

<a id="1-the-eda-checklist"></a>
# 1. The EDA Checklist

Every EDA follows roughly the same sequence:

```
Step 1:  Load and inspect shape
Step 2:  Column names, types, and basic info
Step 3:  Missing values
Step 4:  Duplicates
Step 5:  Distributions (numeric)
Step 6:  Cardinality and frequencies (categorical)
Step 7:  Target variable analysis
Step 8:  Correlation analysis
Step 9:  Outlier detection
Step 10: Feature-target relationships
```

📝 **Practice:** [Q1–Q2 — EDA Checklist](./practice.md#q1)

[↑ Back to Top](#top)

---

<a id="2-phase-1--loading-and-shape"></a>
# 2. Phase 1 — Loading and Shape

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

📝 **Practice:** [Q3–Q6 — Loading & Shape](./practice.md#q3)

[↑ Back to Top](#top)

---

<a id="3-phase-2--missing-values"></a>
# 3. Phase 2 — Missing Values

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

📝 **Practice:** [Q7–Q10 — Missing Values](./practice.md#q7)

[↑ Back to Top](#top)

---

<a id="4-phase-3--distributions"></a>
# 4. Phase 3 — Distributions

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

📝 **Practice:** [Q11–Q14 — Distributions](./practice.md#q11)

[↑ Back to Top](#top)

---

<a id="5-phase-4--categorical-features"></a>
# 5. Phase 4 — Categorical Features

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

📝 **Practice:** [Q15–Q18 — Categorical Features](./practice.md#q15)

[↑ Back to Top](#top)

---

<a id="6-phase-5--target-variable"></a>
# 6. Phase 5 — Target Variable

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

📝 **Practice:** [Q19–Q21 — Target Variable](./practice.md#q19)

[↑ Back to Top](#top)

---

<a id="7-phase-6--correlations-and-outliers"></a>
# 7. Phase 6 — Correlations and Outliers

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

📝 **Practice:** [Q22–Q26 — Correlations & Outliers](./practice.md#q22)

[↑ Back to Top](#top)

---

<a id="8-automated-eda"></a>
# 8. Automated EDA

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

📝 **Practice:** [Q27–Q30 — Automated EDA](./practice.md#q27)

[↑ Back to Top](#top)

---

## 🔥 Summary

EDA is the discipline that separates engineers who build models on corrupted data from engineers who catch problems before they compound. Spend the first hour on understanding — it pays back in every hour of modeling that follows.

**Common mistakes to avoid:**

- **Skipping EDA and going straight to modeling**: EDA catches problems that silently poison models — missing values, wrong dtypes, data leakage, class imbalance.
- **Not checking for duplicates**: duplicate rows inflate evaluation metrics and cause overfitting.
- **Treating ID-like columns as features**: user_id, transaction_id have high cardinality and are not predictors — always check and drop them.
- **Ignoring the target variable distribution**: a heavily skewed target (house prices) often needs a log transform before regression.
- **Checking correlations but not non-linear relationships**: scatter plots reveal U-shapes, thresholds, and interactions that correlation coefficients miss.

| Phase | Key operation |
|---|---|
| Load & Shape | `df.info()`, `df.describe()`, `df.sample()` |
| Missing Values | `isnull().sum()`, missingness heatmap, threshold rules |
| Distributions | Histograms per numeric column, log transform check |
| Categorical | `nunique()`, `value_counts()`, cardinality classification |
| Target Variable | Distribution plot, class balance check |
| Correlations | Heatmap, IQR outlier flagging |
| Automated | `ydata-profiling`, `sweetviz` |

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⬅️ Prev Module | [← Matplotlib & Seaborn](../27_matplotlib_seaborn/README.md) |
| ➡️ Next Module | [→ Web Scraping](../29_web_scraping/theory.md) |

**[🏠 Back to README](../README.md)**

**Prev:** [← Matplotlib & Seaborn](../27_matplotlib_seaborn/README.md) &nbsp;|&nbsp; **Next:** [Web Scraping →](../29_web_scraping/theory.md)

**Related Topics:** [Cheatsheet](./cheetsheet.md) · [Interview Q&A](./interview.md) · [Practice](./practice.md)

[↑ Back to Top](#top)
