# 🔍 EDA Workflow — Interview Questions

---

## Beginner

**Q: What is EDA and why is it important before building a model?**

EDA (Exploratory Data Analysis) is the process of systematically examining a dataset to understand its structure, distributions, quality, and relationships before building models. It's important because: data quality issues (wrong types, missing values, duplicates) silently corrupt models that would otherwise appear to work; outliers can dramatically skew model training; understanding the target distribution determines which models and loss functions to use; high-cardinality or near-duplicate columns waste compute; and data leakage (features that encode future information) produces falsely high evaluation metrics. A model trained without EDA will often produce results that look plausible but are wrong in systematic ways.

---

**Q: How do you handle missing values in a dataset?**

First, understand the missingness pattern: is it Missing Completely at Random (MCAR — no pattern), Missing at Random (MAR — related to other observed features), or Missing Not at Random (MNAR — the missing value itself is informative). For MCAR with < 5% missing: drop rows. For MAR: impute with mean/median (numeric) or mode (categorical), or use KNN/MICE imputation for higher accuracy. For MNAR: create a binary indicator column (`col_was_missing`) before imputing — the missingness itself is a signal. For > 30% missing: usually better to drop the column unless the missingness is highly predictive. Never impute on the test set using test statistics — fit the imputer on training data only.

---

## Intermediate

**Q: How do you detect data leakage during EDA?**

Data leakage occurs when features contain information that wouldn't be available at prediction time, causing falsely high model performance. Detection methods: (1) Suspiciously high correlation (>0.9) between a feature and the target — check if the feature is derived from the target; (2) Model achieves near-perfect accuracy on training — a tree model with depth-1 that achieves 99% accuracy is learning a leaked feature; (3) Features with timestamps after the prediction time; (4) High-cardinality string features that are actually IDs (customer_id → maps 1-to-1 with target in training data); (5) Run SHAP values — if one feature dominates with implausibly high importance, inspect it. Common examples: using `is_churned` as a feature when predicting churn, including future data in rolling averages.

---

**Q: What is the difference between Pearson correlation and Spearman correlation, and when would you use each?**

Pearson correlation measures linear association: it computes how well the relationship fits a straight line. It requires both variables to be approximately normally distributed and is sensitive to outliers. Spearman correlation measures monotonic association — whether one variable tends to increase when the other increases, regardless of whether the relationship is linear. It's computed on ranks, not values, making it robust to outliers and non-normal distributions. Use Pearson for: normally distributed data, linear relationships, no extreme outliers. Use Spearman for: skewed distributions, ordinal data, presence of outliers, or when you care about monotonic trends rather than linearity. In EDA for ML, Spearman is generally safer as a first-pass correlation analysis.

---

## Advanced

**Q: How would you conduct EDA on a dataset with 500 features?**

With 500 features, manual inspection per column is impractical. Strategy: (1) **Automated profiling** — ydata-profiling generates a full report including distributions, correlations, and warnings in one command; (2) **Filter by type** — separate numeric, categorical, datetime, and text columns and handle each class; (3) **Missing value sweep** — `df.isnull().mean()` across all 500 columns, immediately drop columns > 50% missing; (4) **Variance filter** — drop constant or near-constant columns (`df.nunique() <= 2`); (5) **High cardinality filter** — flag columns where `nunique() / len(df) > 0.9` (likely IDs); (6) **Correlation sweep** — compute pairwise correlation matrix, flag pairs with |r| > 0.95 (remove one of each pair as redundant); (7) **Feature importance proxy** — run a quick Random Forest and check SHAP-based importance to identify top-20 features for deeper analysis; (8) **Target correlation** — sort all features by correlation with target to find the most predictive ones.

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
