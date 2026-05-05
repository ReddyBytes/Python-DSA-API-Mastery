"""
EDA Workflow — Practice Problems
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sns.set_theme(style="whitegrid")


# ─────────────────────────────────────────────
# Setup: Generate a messy dataset
# ─────────────────────────────────────────────
np.random.seed(42)
n = 500

df = pd.DataFrame({
    "age":          np.random.randint(18, 80, n),
    "income":       np.random.exponential(50000, n),      # right-skewed
    "education":    np.random.choice(["HS", "Bachelor", "Master", "PhD"], n, p=[0.3, 0.4, 0.2, 0.1]),
    "experience":   np.random.randint(0, 40, n),
    "score":        np.random.normal(70, 15, n).clip(0, 100),
    "customer_id":  range(1, n+1),                         # ID column — should be dropped
})

# Introduce issues
df.loc[np.random.choice(n, 50, replace=False), "age"] = np.nan       # 10% missing
df.loc[np.random.choice(n, 20, replace=False), "income"] = np.nan    # 4% missing
df.loc[np.random.choice(n, 5, replace=False), "age"] = -5            # impossible values
df = pd.concat([df, df.sample(20, random_state=0)])                   # add duplicates
df["target"] = 0.4 * df["age"].fillna(40) + 0.0001 * df["income"].fillna(50000) + \
               np.random.normal(0, 5, len(df))


# ─────────────────────────────────────────────
# PROBLEM 1: Basic Inspection
# ─────────────────────────────────────────────
print("=" * 50)
print("PROBLEM 1: Basic Inspection")
print("=" * 50)

print(f"Shape: {df.shape}")
print(f"\nData types:")
print(df.dtypes)
print(f"\nFirst 5 rows sample:")
print(df.sample(5, random_state=1).to_string())


# ─────────────────────────────────────────────
# PROBLEM 2: Missing Values
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 2: Missing Values")
print("=" * 50)

missing = df.isnull().sum()
pct = (missing / len(df) * 100).round(2)
summary = pd.DataFrame({"count": missing, "pct": pct}).query("count > 0").sort_values("pct", ascending=False)
print(summary)

# Strategy
for col, row in summary.iterrows():
    if row["pct"] < 5:
        print(f"  {col}: {row['pct']:.1f}% — safe to drop rows or impute")
    elif row["pct"] < 30:
        print(f"  {col}: {row['pct']:.1f}% — impute with median")
    else:
        print(f"  {col}: {row['pct']:.1f}% — consider dropping column")


# ─────────────────────────────────────────────
# PROBLEM 3: Duplicates and Data Quality
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 3: Data Quality")
print("=" * 50)

print(f"Duplicate rows: {df.duplicated().sum()}")
print(f"Impossible age values (< 0): {(df['age'] < 0).sum()}")
print(f"High-cardinality ID column: customer_id nunique = {df['customer_id'].nunique()}")

# Fix
df_clean = df.drop_duplicates()
df_clean = df_clean[df_clean["age"].isna() | (df_clean["age"] >= 0)]
df_clean = df_clean.drop(columns=["customer_id"])
print(f"\nAfter cleaning — shape: {df_clean.shape} (was {df.shape})")


# ─────────────────────────────────────────────
# PROBLEM 4: Distributions
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 4: Distribution Analysis")
print("=" * 50)

for col in ["age", "income", "score"]:
    d = df_clean[col].dropna()
    skew = stats.skew(d)
    print(f"{col}: mean={d.mean():.1f}, median={d.median():.1f}, skew={skew:.2f}")
    if abs(skew) > 1:
        print(f"  → Highly skewed — consider log transform")

# Income is exponentially distributed (skew > 2)
df_clean["income_log"] = np.log1p(df_clean["income"])
print(f"\nAfter log transform — income skew: {stats.skew(df_clean['income_log'].dropna()):.2f}")


# ─────────────────────────────────────────────
# PROBLEM 5: Categorical Analysis
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 5: Categorical Analysis")
print("=" * 50)

print("Education value counts:")
print(df_clean["education"].value_counts(normalize=True).round(3))
print(f"Cardinality: {df_clean['education'].nunique()} unique values → low → OHE or ordinal encoding")


# ─────────────────────────────────────────────
# PROBLEM 6: Correlation Analysis
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 6: Correlation with Target")
print("=" * 50)

numeric_df = df_clean.select_dtypes(include="number").dropna()
corr = numeric_df.corr()
target_corr = corr["target"].drop("target").sort_values(key=abs, ascending=False)
print("Feature correlations with target:")
print(target_corr.round(3))


# ─────────────────────────────────────────────
# PROBLEM 7: Outlier Detection
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 7: Outlier Detection")
print("=" * 50)

for col in ["age", "income", "score"]:
    d = df_clean[col].dropna()
    Q1, Q3 = d.quantile(0.25), d.quantile(0.75)
    IQR = Q3 - Q1
    n_outliers = ((d < Q1 - 1.5*IQR) | (d > Q3 + 1.5*IQR)).sum()
    print(f"{col}: {n_outliers} IQR outliers ({100*n_outliers/len(d):.1f}%)")


print("\n✅ EDA workflow practice complete!")
