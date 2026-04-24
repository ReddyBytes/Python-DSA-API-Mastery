# 🎯 ML Data Prep — Turning Raw DataFrames Into Training-Ready Datasets

> Raw data is like unsorted mail. Before a model can learn from it, you have to sort it, remove junk, handle the edge cases, and put it in a format the algorithm expects. This file is the complete playbook for that job.

The gap between a raw DataFrame and a model-ready dataset is where most ML projects spend the most time. You need to split data without leaking information from test to train, handle class imbalance before it silently dominates your metrics, encode categorical columns into numbers a model can process, and scale features so no single column dominates by magnitude alone. Each of these steps has a correct order and a wrong order — doing them out of sequence causes **data leakage**, one of the most common and hardest-to-detect bugs in ML pipelines. This file covers every step of that pipeline in the right order.

---

## Stratified Train/Val/Test Splits — Keeping Class Balance Intact

The naive approach — `df.sample(frac=0.7)` — splits randomly, which can accidentally put 90% of rare class samples into training and leave almost none in validation. **Stratified splitting** preserves the class distribution in every split.

### With sklearn (recommended)

```python
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_parquet("dataset.parquet")

# Step 1: train vs temp (85% / 15%)
df_train, df_temp = train_test_split(
    df,
    test_size=0.30,           # ← 30% goes to temp
    stratify=df["label"],     # ← preserve class ratios
    random_state=42,
)

# Step 2: val vs test from temp (50/50 of the 30% = 15% each)
df_val, df_test = train_test_split(
    df_temp,
    test_size=0.50,
    stratify=df_temp["label"],
    random_state=42,
)

print(f"Train: {len(df_train):,} | Val: {len(df_val):,} | Test: {len(df_test):,}")

# Verify stratification held
for name, split in [("train", df_train), ("val", df_val), ("test", df_test)]:
    dist = split["label"].value_counts(normalize=True).round(3)
    print(f"{name}: {dist.to_dict()}")
```

### Manual 70/15/15 Split (no sklearn)

```python
# Sort by label then shuffle — ensures both classes appear early in each slice
df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)

n = len(df_shuffled)
n_train = int(n * 0.70)
n_val   = int(n * 0.15)

df_train = df_shuffled.iloc[:n_train]
df_val   = df_shuffled.iloc[n_train : n_train + n_val]
df_test  = df_shuffled.iloc[n_train + n_val:]

# Verify no overlap
assert set(df_train.index).isdisjoint(set(df_val.index)), "Overlap between train and val"
assert set(df_train.index).isdisjoint(set(df_test.index)), "Overlap between train and test"
```

---

## Class Imbalance — Diagnosing and Fixing Skewed Datasets

**Class imbalance** occurs when one label dominates the dataset (e.g., 95% negative, 5% positive). A model that always predicts "negative" would achieve 95% accuracy while being completely useless.

### Diagnosing Imbalance

```python
# Absolute counts
print(df["label"].value_counts())

# Relative proportions — this is the diagnostic view
print(df["label"].value_counts(normalize=True).round(4))
# If any class is below ~5% for a binary task, you have an imbalance problem

# For multi-class
print(df["label"].value_counts(normalize=True).sort_index())
```

### Oversampling the Minority Class

```python
# Manual oversampling: sample minority class with replacement to match majority
majority_size = df["label"].value_counts().max()
majority_class = df["label"].value_counts().idxmax()

parts = []
for label, group in df.groupby("label"):
    if label == majority_class:
        parts.append(group)
    else:
        # Oversample minority: sample WITH replacement until it matches majority
        oversampled = group.sample(n=majority_size, replace=True, random_state=42)
        parts.append(oversampled)

df_balanced = pd.concat(parts).sample(frac=1, random_state=42).reset_index(drop=True)
print(df_balanced["label"].value_counts(normalize=True))
```

### Undersampling the Majority Class

```python
# Undersample: reduce majority class to match smallest minority
minority_size = df["label"].value_counts().min()

parts = []
for label, group in df.groupby("label"):
    parts.append(group.sample(n=minority_size, random_state=42))

df_undersampled = pd.concat(parts).sample(frac=1, random_state=42).reset_index(drop=True)
```

Rule of thumb: oversampling is safer when data is scarce; undersampling is preferred when you have millions of majority-class rows and can afford to discard them.

---

## Outlier Detection — Finding and Handling Extreme Values

**Outliers** are data points so far from the norm they either represent measurement errors or genuinely unusual events. Both matter differently depending on your task.

### IQR Method (Distribution-Free)

The **IQR (Interquartile Range)** method defines outliers relative to the spread of the middle 50% of data. It's robust to extreme values because it doesn't use the mean.

```python
def flag_outliers_iqr(series, multiplier=1.5):
    """
    Returns a boolean mask: True where a value is an outlier.
    multiplier=1.5 is standard; use 3.0 for extreme outliers only.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return (series < lower) | (series > upper)

# Flag outliers in every numeric column
numeric_cols = df.select_dtypes(include="number").columns
for col in numeric_cols:
    df[f"{col}_is_outlier"] = flag_outliers_iqr(df[col])

# Remove outlier rows across all numeric columns
outlier_mask = df[[f"{c}_is_outlier" for c in numeric_cols]].any(axis=1)
df_clean = df[~outlier_mask].drop(columns=[f"{c}_is_outlier" for c in numeric_cols])
print(f"Removed {outlier_mask.sum()} outlier rows ({outlier_mask.mean():.1%})")
```

### Z-Score Method (Assumes Normality)

The **z-score** measures how many standard deviations a value is from the mean. Values beyond ±3 are typically considered outliers — but this only works well for normally distributed data.

```python
import numpy as np

def flag_outliers_zscore(series, threshold=3.0):
    """Returns True where |z-score| > threshold."""
    z_scores = (series - series.mean()) / series.std()
    return z_scores.abs() > threshold

# Apply to a specific column
df["latency_is_outlier"] = flag_outliers_zscore(df["latency_ms"])

# Clip instead of remove: replace outliers with boundary values
q_low  = df["latency_ms"].quantile(0.01)
q_high = df["latency_ms"].quantile(0.99)
df["latency_clipped"] = df["latency_ms"].clip(lower=q_low, upper=q_high)
```

---

## Cross-Validation Fold Assignment

Instead of a single train/val split, **cross-validation** uses k different splits and averages performance across all of them. This gives a more reliable estimate of model quality.

```python
import numpy as np

def assign_cv_folds(df, n_folds=5, stratify_col=None, random_state=42):
    """
    Assigns a fold number (0 to n_folds-1) to each row.
    If stratify_col is provided, preserves class distribution per fold.
    """
    df = df.copy()

    if stratify_col is not None:
        # Stratified: assign folds within each class
        df["fold"] = -1
        rng = np.random.RandomState(random_state)

        for label, group in df.groupby(stratify_col):
            idx = group.index.tolist()
            rng.shuffle(idx)
            folds = np.arange(len(idx)) % n_folds
            df.loc[idx, "fold"] = folds
    else:
        # Simple: shuffle and assign
        df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)
        df["fold"] = np.arange(len(df)) % n_folds

    return df

df = assign_cv_folds(df, n_folds=5, stratify_col="label")

# Use fold k as validation, rest as training
k = 0
df_train = df[df["fold"] != k]
df_val   = df[df["fold"] == k]
```

---

## Feature Correlation — Finding and Removing Redundant Features

**Feature correlation** measures how much two features move together. Highly correlated features (e.g., `age` and `years_experience`) add redundant information and can destabilize some models.

```python
import matplotlib
# No display needed — just compute the matrix

# Compute pairwise Pearson correlation
corr_matrix = df.select_dtypes(include="number").corr().abs()  # ← absolute value

# Find feature pairs with correlation > threshold
threshold = 0.90
upper_tri = corr_matrix.where(
    np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)  # ← upper triangle only
)

# Find columns to drop (highly correlated with a feature to their left)
cols_to_drop = [col for col in upper_tri.columns if any(upper_tri[col] > threshold)]
print(f"Dropping {len(cols_to_drop)} correlated features: {cols_to_drop}")

df_uncorrelated = df.drop(columns=cols_to_drop)

# Print the correlation pairs that triggered the drop
high_corr_pairs = [
    (row, col, upper_tri.loc[row, col])
    for row in upper_tri.index
    for col in upper_tri.columns
    if upper_tri.loc[row, col] > threshold
]
for f1, f2, r in high_corr_pairs:
    print(f"  {f1} — {f2}: r={r:.3f}")
```

---

## Normalization and Standardization

Raw feature values on different scales (age: 0–100, salary: 0–200,000) can mislead distance-based and gradient-based models. **Normalization** and **standardization** put features on comparable scales.

### Standardization (Z-Score Normalization)

Transforms each column to have **mean=0** and **std=1**. Best for models that assume Gaussian distributions (logistic regression, SVMs, linear regression).

```python
# Manual standardization — transparent and portable
numeric_cols = df.select_dtypes(include="number").columns.tolist()

# Compute stats on TRAINING SET ONLY — never fit on val/test
train_mean = df_train[numeric_cols].mean()
train_std  = df_train[numeric_cols].std()

# Apply to all splits using training stats
df_train[numeric_cols] = (df_train[numeric_cols] - train_mean) / train_std
df_val[numeric_cols]   = (df_val[numeric_cols]   - train_mean) / train_std  # ← use train stats
df_test[numeric_cols]  = (df_test[numeric_cols]  - train_mean) / train_std

# Verify training set is normalized
print(df_train[numeric_cols].mean().round(6))  # should be ~0
print(df_train[numeric_cols].std().round(6))   # should be ~1
```

### Min-Max Normalization

Scales each column to the range [0, 1]. Best for neural networks and algorithms sensitive to value magnitude (not distribution shape).

```python
train_min = df_train[numeric_cols].min()
train_max = df_train[numeric_cols].max()

df_train[numeric_cols] = (df_train[numeric_cols] - train_min) / (train_max - train_min)
df_val[numeric_cols]   = (df_val[numeric_cols]   - train_min) / (train_max - train_min)
df_test[numeric_cols]  = (df_test[numeric_cols]  - train_min) / (train_max - train_min)
```

---

## Label Encoding vs One-Hot Encoding

**Categorical features** — strings like `"red"`, `"blue"`, `"green"` — must be converted to numbers before most models can use them.

### Label Encoding — Ordinal Categories

Use when the category has a natural order (e.g., `"low" < "medium" < "high"`).

```python
# Manual label encoding
order = ["low", "medium", "high", "critical"]
label_map = {v: i for i, v in enumerate(order)}
df["severity_encoded"] = df["severity"].map(label_map)

# Using pandas Categorical (efficient memory representation too)
df["severity_cat"] = pd.Categorical(df["severity"], categories=order, ordered=True)
df["severity_codes"] = df["severity_cat"].cat.codes  # ← integer codes
```

### One-Hot Encoding — Nominal Categories

Use when categories have no meaningful order. **`pd.get_dummies()`** creates one binary column per category.

```python
# Basic one-hot encoding
df_encoded = pd.get_dummies(df, columns=["color", "source_domain"], dtype=int)

# drop_first=True removes one category per feature (avoids multicollinearity)
df_encoded = pd.get_dummies(df, columns=["color"], drop_first=True, dtype=int)

# Prefix for clarity
df_encoded = pd.get_dummies(
    df,
    columns=["color", "region"],
    prefix=["color", "region"],   # ← column names: color_red, region_us, etc.
    dtype=int,
)
```

---

## Handling Unseen Categories at Inference Time

A model trained with `color_red`, `color_blue`, `color_green` columns will break at inference if a new color appears. This is the **unseen category problem**.

```python
# Step 1: At training time, record the known categories
known_categories = {
    "color": df_train["color"].unique().tolist(),
    "region": df_train["region"].unique().tolist(),
}

# Step 2: At inference time, align columns to training schema
def encode_for_inference(df_new, known_categories, training_columns):
    """
    Encode a new DataFrame to match training column schema exactly.
    Unknown categories become all-zeros (ignored).
    Missing categories become zero columns.
    """
    df_new = df_new.copy()

    # Replace unseen categories with a placeholder before get_dummies
    for col, known in known_categories.items():
        df_new[col] = df_new[col].where(df_new[col].isin(known), other="__unknown__")

    # One-hot encode
    df_encoded = pd.get_dummies(df_new, columns=list(known_categories.keys()), dtype=int)

    # Add missing columns (filled with 0)
    for col in training_columns:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    # Remove extra columns that weren't in training
    df_encoded = df_encoded[[c for c in training_columns if c in df_encoded.columns]]

    # Reorder to match training schema exactly
    return df_encoded.reindex(columns=training_columns, fill_value=0)

# At training time: save the column order
training_columns = df_encoded.columns.tolist()

# At inference time:
df_inference_encoded = encode_for_inference(df_inference, known_categories, training_columns)
```

---

## Complete ML Data Prep Pipeline

The sections above cover each step in isolation. This pipeline chains them together in the correct order: load, inspect, drop irrelevant columns, fill missing values, remove outliers, encode categoricals, split with stratification, then standardize using training-set statistics only. Running steps out of order — for example, standardizing before splitting — causes **data leakage**, where test-set information contaminates the training process.

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# ── Load ─────────────────────────────────────────────────────────────────────
df = pd.read_parquet("raw_features.parquet")
print(f"Raw shape: {df.shape}")

# ── Inspect ──────────────────────────────────────────────────────────────────
print(df.dtypes)
print(df.isnull().sum())
print(df["label"].value_counts(normalize=True))

# ── Drop leaky / irrelevant columns ──────────────────────────────────────────
drop_cols = ["row_id", "created_at", "raw_text"]  # ← non-features
df = df.drop(columns=drop_cols)

# ── Handle missing values ─────────────────────────────────────────────────────
df["age"].fillna(df["age"].median(), inplace=True)
df["category"].fillna("unknown", inplace=True)
df = df.dropna(subset=["label"])  # ← never keep rows with missing targets

# ── Remove outliers ──────────────────────────────────────────────────────────
numeric_cols = df.select_dtypes(include="number").columns.difference(["label"])
for col in numeric_cols:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    df = df[(df[col] >= q1 - 1.5 * iqr) & (df[col] <= q3 + 1.5 * iqr)]

print(f"After outlier removal: {df.shape}")

# ── Encode categoricals ───────────────────────────────────────────────────────
df = pd.get_dummies(df, columns=["category", "region"], dtype=int)

# ── Stratified split ─────────────────────────────────────────────────────────
df_train, df_temp = train_test_split(df, test_size=0.30, stratify=df["label"], random_state=42)
df_val, df_test   = train_test_split(df_temp, test_size=0.50, stratify=df_temp["label"], random_state=42)

# ── Standardize using training stats ONLY ────────────────────────────────────
feature_cols = [c for c in df.columns if c != "label"]
train_mean = df_train[feature_cols].mean()
train_std  = df_train[feature_cols].std().replace(0, 1)  # ← avoid division by zero

df_train[feature_cols] = (df_train[feature_cols] - train_mean) / train_std
df_val[feature_cols]   = (df_val[feature_cols]   - train_mean) / train_std
df_test[feature_cols]  = (df_test[feature_cols]  - train_mean) / train_std

# ── Save splits ───────────────────────────────────────────────────────────────
df_train.to_parquet("data/train.parquet", index=False)
df_val.to_parquet("data/val.parquet",     index=False)
df_test.to_parquet("data/test.parquet",   index=False)

print(f"Train: {len(df_train):,} | Val: {len(df_val):,} | Test: {len(df_test):,}")
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
