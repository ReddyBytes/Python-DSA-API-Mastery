# 📊 Statistics and Probability for Data Science

---

You're building a spam classifier. Your model says an email is 70% likely to be spam. A colleague asks: "How confident are you that this model actually works and isn't just guessing?"

You run a test. On 1000 emails, it catches 87% of spam. But is that luck, or is it real? If you ran the same test on a different 1000 emails, would you still get 87%? Or would you get 55%? Or 99%?

These questions are statistics. And until you can answer them, you don't actually know if your model works.

Statistics is the science of learning from data when the data is incomplete, noisy, and sampled — which describes every real dataset you will ever work with.

---

## 📌 Learning Priority

**Must Learn** — Core concept, daily use, interview essential:
Mean · Median · Std deviation · Normal distribution · Central Limit Theorem · Hypothesis testing · p-value · Confidence intervals

**Should Learn** — Important for real projects, comes up regularly:
Bayes' theorem · Conditional probability · Type I / Type II errors · A/B testing · Chi-square test · Correlation vs causation

**Good to Know** — Useful in specific situations:
Power analysis · Multiple testing correction (Bonferroni) · Bootstrap sampling · MLE (Maximum Likelihood Estimation) · KL divergence

**Reference** — Know it exists, look up when needed:
Moment generating functions · Characteristic functions · Cramér–Rao bound · Fisher information

---

## 1️⃣ Descriptive Statistics — Summarizing Data

Before any model, you describe your data. The three things you always want to know:

**Center**: where is the data concentrated?
**Spread**: how variable is it?
**Shape**: is it symmetric, skewed, multi-modal?

```python
import numpy as np
import pandas as pd
from scipy import stats

data = [12, 15, 14, 10, 99, 13, 16, 12, 14, 11]   # note: 99 is an outlier

# Measures of center
mean   = np.mean(data)           # 21.6  ← pulled up by 99
median = np.median(data)         # 13.5  ← robust to 99
mode   = stats.mode(data).mode   # 12    ← most frequent value

# Measures of spread
std    = np.std(data, ddof=1)    # ddof=1 for sample std (Bessel correction)
var    = np.var(data, ddof=1)    # variance = std²
iqr    = stats.iqr(data)         # interquartile range: Q3 - Q1

print(f"Mean: {mean:.1f}, Median: {median:.1f}")
print(f"Std: {std:.1f}, IQR: {iqr:.1f}")

# Full summary with pandas
s = pd.Series(data)
print(s.describe())   # count, mean, std, min, 25%, 50%, 75%, max
```

**When to use mean vs median:**
- Use **mean** when data is symmetric, no extreme outliers
- Use **median** when data is skewed or has outliers (house prices, salaries, response times)

---

## 2️⃣ Probability Distributions

A **probability distribution** describes how likely each outcome is.

```
Discrete distributions (countable outcomes):
┌─────────────────┬──────────────────────────────────────────────┐
│ Distribution    │ Use Case                                     │
├─────────────────┼──────────────────────────────────────────────┤
│ Bernoulli       │ Single coin flip: P(heads) = p              │
│ Binomial        │ k successes in n flips: spam in 100 emails  │
│ Poisson         │ Count of events per time: API calls/second  │
└─────────────────┴──────────────────────────────────────────────┘

Continuous distributions (any value in a range):
┌─────────────────┬──────────────────────────────────────────────┐
│ Distribution    │ Use Case                                     │
├─────────────────┼──────────────────────────────────────────────┤
│ Normal/Gaussian │ Errors, measurement noise, many ML outputs  │
│ Uniform         │ Random split thresholds, hyperparameter search│
│ Exponential     │ Time between events (arrivals, failures)    │
│ Beta            │ Probability estimates: click-through rates  │
└─────────────────┴──────────────────────────────────────────────┘
```

```python
from scipy import stats
import numpy as np

# Normal distribution (mean=0, std=1)
dist = stats.norm(loc=0, scale=1)
print(dist.pdf(0))          # 0.399 — peak probability density at mean
print(dist.cdf(1.96))       # 0.975 — 97.5% of values below 1.96
print(dist.ppf(0.975))      # 1.960 — the value at the 97.5th percentile

# Binomial: probability of getting k=7 heads in n=10 flips with p=0.5
binom = stats.binom(n=10, p=0.5)
print(binom.pmf(7))         # 0.117 — P(exactly 7 heads)
print(binom.cdf(7))         # 0.945 — P(at most 7 heads)

# Sample from a distribution
samples = stats.norm.rvs(loc=170, scale=10, size=1000)  # 1000 heights
```

---

## 3️⃣ The Normal Distribution and Why It's Everywhere

The **normal distribution** (bell curve) appears naturally when:
- Many independent random factors add together
- Measurement errors accumulate

```
μ-3σ  μ-2σ  μ-σ    μ    μ+σ   μ+2σ  μ+3σ
 |     |     |      |     |     |     |
 |  2% | 14% | 34%  | 34% | 14% |  2% |
 └─────┴─────┴──────┴─────┴─────┴─────┘

68% of data falls within 1 std of the mean
95% of data falls within 2 std of the mean
99.7% of data falls within 3 std of the mean
```

**The Central Limit Theorem (CLT)**: If you take many samples from any distribution and compute each sample's mean, those sample means will be normally distributed — regardless of the original distribution's shape. This is why we can apply normal-distribution-based tests to non-normal data, as long as the sample size is large enough (typically n > 30).

```python
# Demonstrate CLT: sampling from a skewed distribution
import numpy as np

# Original: highly skewed exponential distribution
population = np.random.exponential(scale=2, size=100000)
print(f"Population skewness: {stats.skew(population):.2f}")   # ~2 — very skewed

# Sample means become normal as sample size grows
sample_means = [np.mean(np.random.choice(population, size=50)) for _ in range(1000)]
print(f"Sample means skewness: {stats.skew(sample_means):.2f}")   # ~0 — normal!
```

---

## 4️⃣ Hypothesis Testing

You changed your recommendation algorithm. Click-through rate went from 3.2% to 3.8%. Is that a real improvement, or could it happen by chance with the old algorithm?

Hypothesis testing gives you a framework to answer this.

**The logic:**
1. State the **null hypothesis** H₀: "nothing changed — the difference is random noise"
2. State the **alternative hypothesis** H₁: "something real changed"
3. Compute how likely your observed result would be if H₀ were true (the **p-value**)
4. If p-value < threshold (usually 0.05): reject H₀, accept H₁

```python
from scipy import stats
import numpy as np

# A/B test: did changing the button color improve click-through rate?
# Group A: old button — 320 clicks from 10000 views = 3.2%
# Group B: new button — 380 clicks from 10000 views = 3.8%

clicks_a, n_a = 320, 10000
clicks_b, n_b = 380, 10000

# Two-proportion z-test
count = np.array([clicks_a, clicks_b])
nobs  = np.array([n_a, n_b])

z_stat, p_value = stats.proportions_ztest(count, nobs)

print(f"Z-statistic: {z_stat:.3f}")
print(f"P-value: {p_value:.4f}")

if p_value < 0.05:
    print("Statistically significant — reject H₀")
else:
    print("Not significant — cannot reject H₀")
```

**p-value explained plainly**: "If there truly were no difference, the probability of seeing a gap this large or larger by random chance is p."

p-value of 0.03 means: only a 3% chance of seeing this result if nothing actually changed. We conclude something changed.

---

## 5️⃣ Type I and Type II Errors

```
                   Reality
                   H₀ True         H₀ False
Test    Reject H₀  Type I Error ✗   Correct ✓
Result  Keep H₀    Correct ✓        Type II Error ✗

Type I error  (False Positive): flagging a good model as better — wasted rollout
Type II error (False Negative): missing a real improvement — lost revenue
```

- **α (significance level)**: acceptable false positive rate. Standard: 0.05
- **β (false negative rate)**: 1 - statistical power
- **Power (1-β)**: probability of correctly detecting a real effect. Target: 0.80

```python
# Sample size calculation for A/B test
from statsmodels.stats.power import NormalIndPower

effect_size = 0.2   # Cohen's d — small effect
alpha = 0.05
power = 0.80

analysis = NormalIndPower()
n_required = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power)
print(f"Required sample size per group: {int(np.ceil(n_required))}")
```

---

## 6️⃣ Bayes' Theorem

**Bayes' theorem** updates your belief in a hypothesis given new evidence.

`P(A|B) = P(B|A) × P(A) / P(B)`

Classic example: medical test for a rare disease.
- Disease prevalence: 1% (prior)
- Test sensitivity: 99% (P(positive | disease))
- Test specificity: 99% (P(negative | no disease))

```python
# Bayes: given a positive test, what's the probability of actually having the disease?
prevalence = 0.01        # P(disease) — prior
sensitivity = 0.99       # P(positive | disease)
specificity = 0.99       # P(negative | no disease)

p_positive_given_disease    = sensitivity                      # 0.99
p_positive_given_no_disease = 1 - specificity                  # 0.01

# Law of total probability: P(positive)
p_positive = (p_positive_given_disease * prevalence +
              p_positive_given_no_disease * (1 - prevalence))

# Bayes' theorem: P(disease | positive)
p_disease_given_positive = (p_positive_given_disease * prevalence) / p_positive

print(f"P(positive test): {p_positive:.3f}")
print(f"P(disease | positive test): {p_disease_given_positive:.3f}")
# Result: only ~50% — surprising! Low prevalence dominates.
```

This result — that a positive test from a rare disease still only gives ~50% probability — illustrates why Naive Bayes classifiers work despite their independence assumption: prior probability matters enormously.

---

## 7️⃣ Correlation and Covariance

**Correlation** measures the linear relationship between two variables.

```python
import numpy as np
import pandas as pd

x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 5, 4, 5])
z = np.array([5, 4, 3, 2, 1])   # negatively correlated with x

# Pearson correlation (-1 to +1)
print(f"corr(x, y): {np.corrcoef(x, y)[0,1]:.3f}")   # ~0.9 — strong positive
print(f"corr(x, z): {np.corrcoef(x, z)[0,1]:.3f}")   # -1.0 — perfect negative

# DataFrame correlations
df = pd.DataFrame({"x": x, "y": y, "z": z})
print(df.corr())   # correlation matrix

# Spearman (rank-based, robust to non-linear relationships)
from scipy.stats import spearmanr
corr, p_val = spearmanr(x, y)
print(f"Spearman: {corr:.3f}, p-value: {p_val:.3f}")
```

**Correlation ≠ causation.** Two variables can be correlated because:
- A causes B
- B causes A
- A third variable C causes both (confounding)
- Pure coincidence (spurious correlation)

---

## Common Mistakes to Avoid ⚠️

- **Ignoring p-value interpretation**: p < 0.05 means the result is statistically significant, not that the effect is practically important. A tiny effect with a huge sample will be statistically significant but useless.
- **Using mean on skewed data**: always check the distribution shape. For salary analysis, median tells the truth; mean is misleading.
- **Applying parametric tests to non-normal small samples**: t-tests assume normality. For n < 30 with non-normal data, use Mann-Whitney U or bootstrap methods.
- **Ignoring multiple testing**: running 20 t-tests with α=0.05 means you'd expect 1 false positive by chance. Use Bonferroni correction or FDR control.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Prev Module | [../25_python_ai_ecosystem/theory.md](../25_python_ai_ecosystem/theory.md) |
| ➡️ Next Module | [../27_matplotlib_seaborn/theory.md](../27_matplotlib_seaborn/theory.md) |

---

**[🏠 Back to README](../README.md)**
