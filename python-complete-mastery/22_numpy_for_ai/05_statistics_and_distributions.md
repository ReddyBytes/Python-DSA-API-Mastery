# 🎯 Statistics and Distributions — Describing What Your Data Looks Like

> A histogram is a fingerprint of your dataset. Percentiles are its vital signs. Correlation is how you catch two features that are secretly the same feature.

---

## Percentiles and Quantiles — Robust Summary Statistics

You're monitoring an API serving 10,000 requests/second. Average latency is 200ms — looks good. But users complain. You check P99: 4 seconds. 1% of requests are hanging. The mean hid the problem. Percentiles expose it.

**Percentiles** answer the question: "What value is X% of the data below?" They are more robust than the mean for skewed data or data with outliers — a single bad value cannot distort them catastrophically.

The **median** is the 50th percentile. The **IQR** (interquartile range) — the gap between the 25th and 75th percentile — measures spread without being fooled by outliers.

```python
import numpy as np

rng = np.random.default_rng(42)
data = rng.exponential(scale=2.0, size=10000)   # right-skewed distribution

# Single percentile
median = np.percentile(data, 50)
print(f"Median: {median:.3f}")

# Multiple percentiles at once
p25, p50, p75 = np.percentile(data, [25, 50, 75])
iqr = p75 - p25                                   # ← interquartile range
print(f"IQR: {iqr:.3f}")

# Five-number summary
summary = np.percentile(data, [0, 25, 50, 75, 100])  # min, Q1, Q2, Q3, max
print(f"Five-number summary: {summary.round(3)}")

# Outlier detection using IQR fence
lower_fence = p25 - 1.5 * iqr    # ← Tukey fences
upper_fence = p75 + 1.5 * iqr
outliers = data[(data < lower_fence) | (data > upper_fence)]
print(f"Outlier count: {len(outliers)} ({len(outliers)/len(data)*100:.1f}%)")
```

**`np.quantile`** is identical to `np.percentile` but uses [0, 1] scale instead of [0, 100]:

```python
# Same result, different scale
q50_a = np.percentile(data, 50)
q50_b = np.quantile(data, 0.50)    # ← 0.5 instead of 50
print(np.isclose(q50_a, q50_b))    # True

# Useful for thresholding: keep top 10% most confident predictions
scores = rng.random(1000)
threshold = np.quantile(scores, 0.90)             # 90th percentile
top_10pct = scores[scores >= threshold]
print(f"Top 10% threshold: {threshold:.3f}, count: {len(top_10pct)}")
```

---

## Interpolation Methods for Percentiles

When the percentile falls between two data points, NumPy needs to **interpolate**. The default method is `"linear"`, but ML workflows sometimes need specific methods:

```python
small = np.array([1, 3, 5, 7, 9])

methods = ["linear", "lower", "higher", "nearest", "midpoint"]
for method in methods:
    val = np.percentile(small, 30, interpolation=method)  # NumPy < 1.22
    # For NumPy >= 1.22:
    val = np.percentile(small, 30, method=method)
    print(f"{method:10s}: {val}")
# linear  : 2.2
# lower   : 1   ← always returns an actual data point (conservative)
# higher  : 3   ← returns the next data point up
# nearest : 3   ← rounds to closest data point
# midpoint: 2.0 ← average of lower and higher
```

---

## Histograms — Visualizing Distributions

You've trained a model for 3 days. Now you want to understand the distribution of your 50k loss values. A histogram gives you the shape — not just the average. It tells you whether losses are tightly clustered, bimodal, or hiding a long tail of catastrophic failures.

A **histogram** bins continuous data into intervals and counts how many values fall in each bin. NumPy computes the bin counts and edges; you need Matplotlib only if you want to draw it.

```python
data = rng.normal(0, 1, size=10000)

# Basic histogram: 10 equal-width bins
counts, bin_edges = np.histogram(data, bins=10)
# counts:    how many values in each bin (shape: (10,))
# bin_edges: the bin boundaries (shape: (11,) — one more than counts)

bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2   # ← midpoints of each bin

# Normalized histogram (probability density)
density, edges = np.histogram(data, bins=50, density=True)
# density * bin_width integrates to 1.0 — a probability density estimate

# Custom bin edges
custom_edges = np.linspace(-4, 4, 41)   # 40 bins from -4 to +4
counts_custom, _ = np.histogram(data, bins=custom_edges)

# 2D histogram — for joint distributions of two features
x = rng.normal(0, 1, 5000)
y = x * 0.8 + rng.normal(0, 0.6, 5000)    # ← correlated with x
H, xedges, yedges = np.histogram2d(x, y, bins=20)
print(f"2D histogram shape: {H.shape}")    # (20, 20)
```

**Practical use:** inspecting feature distributions before training to catch issues (multimodal distributions, unexpected spikes, wrong scale).

```python
# Feature distribution audit: check for outliers and skew
def audit_feature(arr, name):
    p = np.percentile(arr, [1, 5, 25, 50, 75, 95, 99])
    print(f"{name}:")
    print(f"  mean={arr.mean():.3f}  std={arr.std():.3f}")
    print(f"  p1={p[0]:.3f}  p5={p[1]:.3f}  p25={p[2]:.3f}")
    print(f"  p50={p[3]:.3f}  p75={p[4]:.3f}  p95={p[5]:.3f}  p99={p[6]:.3f}")
    counts, edges = np.histogram(arr, bins=10)
    print(f"  histogram: {counts}")
```

---

## Correlation Coefficient — Linear Relationship Strength

You have 50 features. Before training, you want to know: are any of them just duplicates of each other? A correlation matrix tells you in one operation. Features with correlation above 0.95 add no new information — keeping both slows training and inflates your model without improving accuracy.

The **Pearson correlation coefficient** measures the linear relationship between two variables. It ranges from -1 (perfect negative correlation) to +1 (perfect positive correlation), with 0 meaning no linear relationship.

`np.corrcoef` returns a **correlation matrix**: a square matrix where entry `[i, j]` is the correlation between variable i and variable j. The diagonal is always 1.0 (a variable is perfectly correlated with itself).

```python
rng = np.random.default_rng(3)

# Two correlated features
x1 = rng.normal(0, 1, 500)
x2 = x1 * 0.9 + rng.normal(0, 0.44, 500)   # ← ~90% correlated with x1
x3 = rng.normal(0, 1, 500)                   # ← uncorrelated

# Stack features row-wise (corrcoef expects shape (n_vars, n_observations))
features = np.vstack([x1, x2, x3])           # shape (3, 500)
corr_matrix = np.corrcoef(features)           # shape (3, 3)

print(corr_matrix.round(3))
# [[1.000  0.897  0.021]
#  [0.897  1.000  0.015]
#  [0.021  0.015  1.000]]

# Extract off-diagonal correlations (upper triangle)
n = corr_matrix.shape[0]
upper_idx = np.triu_indices(n, k=1)          # ← indices of upper triangle (k=1 excludes diagonal)
upper_corrs = corr_matrix[upper_idx]
print(f"Pairwise correlations: {upper_corrs.round(3)}")  # [0.897, 0.021, 0.015]

# Flag highly correlated feature pairs
threshold = 0.8
high_corr = np.abs(corr_matrix) > threshold
np.fill_diagonal(high_corr, False)           # ← ignore self-correlation
pairs = np.argwhere(high_corr)
for i, j in pairs:
    if i < j:   # ← avoid printing both (i,j) and (j,i)
        print(f"High correlation: feature {i} and {j}: {corr_matrix[i,j]:.3f}")
```

**Spearman rank correlation** — non-parametric, robust to outliers and non-linear monotonic relationships:

```python
# Spearman = Pearson on the ranks
def spearman_corrcoef(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)   # ← rank of x
    ry = np.argsort(np.argsort(y)).astype(float)   # ← rank of y
    return np.corrcoef(rx, ry)[0, 1]

x_skewed = rng.exponential(2.0, 500)
y_skewed = x_skewed ** 2 + rng.normal(0, 1, 500)

print(f"Pearson:  {np.corrcoef(x_skewed, y_skewed)[0,1]:.3f}")
print(f"Spearman: {spearman_corrcoef(x_skewed, y_skewed):.3f}")
# Spearman is higher — captures the monotonic (not just linear) relationship
```

---

## Covariance Matrix — The Full Picture

The **covariance matrix** is the unnormalized version of the correlation matrix. Entry `[i, j]` is `Cov(Xᵢ, Xⱼ) = E[(Xᵢ - μᵢ)(Xⱼ - μⱼ)]`. It captures both the variance of each feature (diagonal) and how features vary together (off-diagonal).

The covariance matrix is central to PCA, Gaussian distributions, Mahalanobis distance, and Kalman filters.

```python
rng = np.random.default_rng(7)

# Simulate 3 features with known covariance structure
true_cov = np.array([[4.0, 1.8, 0.0],
                     [1.8, 1.0, 0.0],
                     [0.0, 0.0, 2.5]])   # ← features 0,1 correlated; feature 2 independent

# Generate from this covariance (Cholesky method)
L = np.linalg.cholesky(true_cov)         # ← lower triangular such that L @ L.T = true_cov
z = rng.normal(0, 1, size=(1000, 3))
X = z @ L.T                              # ← transform standard normal to desired covariance

# Estimate covariance from data
cov_est = np.cov(X.T)                    # ← np.cov expects shape (n_vars, n_obs)
print(cov_est.round(2))
# Should be close to true_cov

# Diagonal = variances
variances = np.diag(cov_est)
std_devs = np.sqrt(variances)
print(f"Estimated std devs: {std_devs.round(3)}")

# Off-diagonal = covariances (normalize to get correlation)
corr_from_cov = cov_est / np.outer(std_devs, std_devs)   # ← manual normalization
print(np.allclose(corr_from_cov, np.corrcoef(X.T)))       # True
```

**Mahalanobis distance** — anomaly detection using the covariance structure:

```python
# Mahalanobis distance accounts for feature correlations and scales
# Points that are "far" in covariance-space are anomalies

mu = X.mean(axis=0)                       # ← sample mean
cov_inv = np.linalg.inv(cov_est)          # ← precision matrix

# For each data point, compute squared Mahalanobis distance
delta = X - mu                            # ← shape (1000, 3), demeaned
# d²(x) = (x - μ)ᵀ Σ⁻¹ (x - μ)
d2 = np.einsum("ni,ij,nj->n", delta, cov_inv, delta)  # ← shape (1000,)

# Points with d2 > chi2(df=3, p=0.975) ≈ 9.35 are outliers
threshold = 9.35
n_outliers = (d2 > threshold).sum()
print(f"Mahalanobis outliers (expected ~2.5%): {n_outliers/len(X)*100:.1f}%")
```

---

## Descriptive Statistics Cheat Sheet

```python
arr = rng.normal(5, 2, size=(100, 10))   # 100 samples, 10 features

# Central tendency
arr.mean(axis=0)                # ← mean per feature (column-wise)
np.median(arr, axis=0)          # ← median per feature

# Spread
arr.std(axis=0)                 # ← std per feature (ddof=0 by default)
arr.std(axis=0, ddof=1)         # ← unbiased std (Bessel's correction)
arr.var(axis=0)                 # ← variance per feature

# Range
arr.min(axis=0)
arr.max(axis=0)
np.ptp(arr, axis=0)             # ← peak-to-peak (max - min) per feature

# Moments
from scipy import stats as sp_stats   # outside numpy, but related
# np has no built-in skew/kurtosis — use scipy.stats or compute manually

# Manual skewness
mu = arr.mean(axis=0)
sigma = arr.std(axis=0)
skewness = ((arr - mu)**3).mean(axis=0) / sigma**3
print(f"Skewness (should be ~0 for normal): {skewness.mean():.3f}")
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
| Random and Sampling | [03_random_and_sampling.md](./03_random_and_sampling.md) |
| Linear Algebra (Advanced) | [06_linear_algebra_advanced.md](./06_linear_algebra_advanced.md) |
| Einsum and Performance | [07_einsum_and_performance.md](./07_einsum_and_performance.md) |
| I/O and Memory | [08_io_and_memory.md](./08_io_and_memory.md) |
