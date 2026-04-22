# 📊 Statistics and Probability — Cheatsheet

## Descriptive Statistics

```python
import numpy as np
import pandas as pd
from scipy import stats

data = pd.Series([12, 15, 14, 10, 99, 13, 16, 12, 14, 11])

# Summary
print(data.describe())           # count, mean, std, quartiles
print(data.mean())               # arithmetic mean
print(data.median())             # robust to outliers
print(data.mode()[0])            # most frequent
print(data.std(ddof=1))          # sample std (ddof=1 for unbiased)
print(stats.iqr(data))           # interquartile range Q3-Q1
print(stats.skew(data))          # >0: right skewed, <0: left skewed
print(stats.kurtosis(data))      # >3: heavy tails, <3: light tails
```

---

## Distributions

```python
from scipy import stats

# Normal
dist = stats.norm(loc=0, scale=1)
dist.pdf(x)     # probability density at x
dist.cdf(x)     # P(X <= x)
dist.ppf(0.95)  # x such that P(X <= x) = 0.95 (inverse CDF)
dist.rvs(100)   # 100 random samples

# t-distribution (use when n < 30 or σ unknown)
dist = stats.t(df=29)

# Binomial
dist = stats.binom(n=10, p=0.3)
dist.pmf(3)     # P(X = 3) — discrete

# Poisson
dist = stats.poisson(mu=5)
dist.pmf(3)     # P(3 events)
```

---

## Hypothesis Tests

```python
from scipy import stats

# One-sample t-test: is the mean different from mu_0?
t_stat, p_val = stats.ttest_1samp(sample, popmean=0)

# Two-sample t-test: are two groups different?
t_stat, p_val = stats.ttest_ind(group_a, group_b)

# Paired t-test (before/after)
t_stat, p_val = stats.ttest_rel(before, after)

# Mann-Whitney U (non-parametric alternative to t-test)
u_stat, p_val = stats.mannwhitneyu(group_a, group_b)

# Chi-square test of independence (categorical data)
chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)

# A/B test: two proportions
from statsmodels.stats.proportion import proportions_ztest
z, p = proportions_ztest([clicks_a, clicks_b], [n_a, n_b])
```

---

## Confidence Intervals

```python
import numpy as np
from scipy import stats

data = np.array([5.1, 4.9, 5.3, 5.0, 4.8, 5.2])
n = len(data)
mean = np.mean(data)
se = stats.sem(data)   # standard error = std / sqrt(n)

# 95% confidence interval
ci = stats.t.interval(0.95, df=n-1, loc=mean, scale=se)
print(f"95% CI: ({ci[0]:.3f}, {ci[1]:.3f})")

# Bootstrap CI (distribution-free)
bootstrap = stats.bootstrap((data,), np.mean, confidence_level=0.95, n_resamples=9999)
print(f"Bootstrap CI: {bootstrap.confidence_interval}")
```

---

## Bayes' Theorem

```python
def bayes_update(prior, likelihood, false_positive_rate):
    """P(hypothesis | evidence)"""
    p_evidence = likelihood * prior + false_positive_rate * (1 - prior)
    return (likelihood * prior) / p_evidence

# Disease test: prior=1%, sensitivity=99%, false positive=1%
posterior = bayes_update(prior=0.01, likelihood=0.99, false_positive_rate=0.01)
print(f"P(disease | positive test): {posterior:.2%}")   # ~50%
```

---

## Correlation

```python
import numpy as np
from scipy import stats

# Pearson (linear relationships)
r, p = stats.pearsonr(x, y)

# Spearman (monotonic, robust to outliers)
rho, p = stats.spearmanr(x, y)

# Correlation matrix
df.corr(method="pearson")   # or "spearman", "kendall"
```

**Interpretation:**
- |r| 0.0–0.1: negligible
- |r| 0.1–0.3: small
- |r| 0.3–0.5: medium
- |r| 0.5+: large

---

## A/B Testing Workflow

```python
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportions_ztest
import numpy as np

# 1. Power analysis — decide sample size BEFORE running test
effect_size = 0.05 / 0.032    # minimum detectable effect / baseline
n = NormalIndPower().solve_power(effect_size=0.2, alpha=0.05, power=0.8)

# 2. Run test, collect data

# 3. Analyze
z, p = proportions_ztest([320, 380], [10000, 10000])
print(f"p-value: {p:.4f}")
print("Significant" if p < 0.05 else "Not significant")

# 4. Report effect size, not just p-value
control_rate = 320 / 10000
treatment_rate = 380 / 10000
lift = (treatment_rate - control_rate) / control_rate
print(f"Relative lift: {lift:.1%}")
```

---

## Key Formulas

| Concept | Formula |
|---|---|
| Mean | `μ = Σxᵢ / n` |
| Std deviation | `σ = √(Σ(xᵢ-μ)² / (n-1))` |
| Standard error | `SE = σ / √n` |
| z-score | `z = (x - μ) / σ` |
| Confidence interval | `x̄ ± z × SE` |
| Bayes' theorem | `P(A|B) = P(B|A)P(A) / P(B)` |
| Pearson r | `r = Σ(xᵢ-x̄)(yᵢ-ȳ) / (n·σₓ·σᵧ)` |

---

## Common Test Selection Guide

```
Are the groups independent?
├── Yes → Independent samples t-test (or Mann-Whitney for non-normal)
└── No (paired) → Paired t-test

Comparing more than 2 groups?
└── ANOVA (or Kruskal-Wallis for non-normal)

Categorical data?
└── Chi-square test of independence

Proportion comparison?
└── Proportions z-test

Small sample (n < 30), non-normal?
└── Non-parametric: Mann-Whitney, Wilcoxon, bootstrap
```

---

## Golden Rules

1. Always visualize data before running statistics — summary stats hide the distribution shape
2. Use median and IQR for skewed data, not mean and std
3. A p-value tells you significance, not importance — always report effect size too
4. n < 30: check normality before using t-tests; consider non-parametric alternatives
5. Multiple tests: use Bonferroni (α/n) or Benjamini-Hochberg FDR control
