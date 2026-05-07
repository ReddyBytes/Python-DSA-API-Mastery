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

**Q: How do you detect and handle class imbalance in a classification dataset?**

Detection: `df["target"].value_counts(normalize=True)` — flag any class below 10% of the majority. Compute the imbalance ratio (majority count / minority count); ratios above 5:1 are moderate, above 10:1 are severe.

Handling strategies:
- **class_weight="balanced"** (algorithmic): tells the model to penalize minority misclassifications more heavily. Zero data change, works with sklearn classifiers. Best starting point.
- **SMOTE** (data-level): generates synthetic minority samples by interpolating between real minority examples. Increases dataset size; risk is that synthetic samples may not reflect real distribution boundaries. Apply only to training data, never to test.
- **Threshold tuning** (post-hoc): lower the classification threshold from 0.5 to 0.3 so more samples are predicted as minority. No retraining needed, but requires calibrated probabilities.
- **Metric change**: switch from accuracy to F1, precision-recall AUC, or Matthews Correlation Coefficient — accuracy is meaningless on imbalanced data.

---

**Q: What is VIF and when would you compute it during EDA?**

VIF (Variance Inflation Factor) measures how much the variance of a regression coefficient is inflated due to multicollinearity with other features. A VIF of 10 for feature X means its variance is 10x larger than it would be if X were uncorrelated with all other features — this makes coefficient estimates unstable.

Compute VIF when: (1) you're using linear or logistic regression (tree models are less affected by multicollinearity); (2) the correlation heatmap shows pairs with |r| > 0.8; (3) you notice that adding/removing one feature drastically changes another's coefficient. VIF > 10 is the standard threshold to flag a feature for potential removal. Implementation uses `statsmodels.stats.outliers_influence.variance_inflation_factor`.

---

**Q: What is the difference between IQR and Z-score outlier detection?**

IQR (Interquartile Range) method defines outliers as values below Q1 − 1.5×IQR or above Q3 + 1.5×IQR. It is **robust** — the quartiles are not affected by extreme values, so existing outliers don't influence where the fence sits.

Z-score method defines outliers as values where |(x − mean) / std| > 3. It is **sensitive** — the mean and standard deviation are themselves pulled by extreme values, which can make the fence too wide and miss real outliers in highly skewed data.

Rule of thumb: use IQR first, especially for skewed distributions (income, price, count data). Use Z-score only when you've confirmed the distribution is approximately normal.

---

**Q: When would you use sweetviz instead of ydata-profiling?**

Use sweetviz when you need a **comparison** between two datasets — typically train vs test, or pre-treatment vs post-treatment. sweetviz places both distributions side by side for every feature so you can spot distribution shift at a glance. It also highlights the target variable prominently across all feature views.

Use ydata-profiling when you need a **deep single-dataset report**: it provides Pearson, Spearman, and Kendall correlation matrices, a missing value matrix, interaction plots, and automated warnings (skewness, high cardinality, constant columns) — all in one HTML file.

---

**Q: How would you conduct EDA on a dataset with 500 features?**

With 500 features, manual inspection per column is impractical. Strategy: (1) **Automated profiling** — ydata-profiling generates a full report including distributions, correlations, and warnings in one command; (2) **Filter by type** — separate numeric, categorical, datetime, and text columns and handle each class; (3) **Missing value sweep** — `df.isnull().mean()` across all 500 columns, immediately drop columns > 50% missing; (4) **Variance filter** — drop constant or near-constant columns (`df.nunique() <= 2`); (5) **High cardinality filter** — flag columns where `nunique() / len(df) > 0.9` (likely IDs); (6) **Correlation sweep** — compute pairwise correlation matrix, flag pairs with |r| > 0.95 (remove one of each pair as redundant); (7) **Feature importance proxy** — run a quick Random Forest and check SHAP-based importance to identify top-20 features for deeper analysis; (8) **Target correlation** — sort all features by correlation with target to find the most predictive ones.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⬅️ Prev Module | [../27_matplotlib_seaborn/theory.md](../27_matplotlib_seaborn/theory.md) |
| ➡️ Next Module | [../29_web_scraping/theory.md](../29_web_scraping/theory.md) |

---

**[🏠 Back to README](../README.md)**
