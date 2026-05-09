# Statistics and Probability — Practice

## Quick Index

| Q | Topic | Difficulty |
|---|---|---|
| [Q1](#q1) | descriptive stats — mean, median, mode with numpy | 🟢 |
| [Q2](#q2) | std vs variance — Bessel correction | 🟢 |
| [Q3](#q3) | IQR and outlier detection | 🟢 |
| [Q4](#q4) | skewness — identify skewed data | 🟡 |
| [Q5](#q5) | pandas describe() — full summary | 🟢 |
| [Q6](#q6) | uniform distribution — random sampling | 🟢 |
| [Q7](#q7) | binomial pmf — coin flips | 🟡 |
| [Q8](#q8) | Poisson pmf — event counting | 🟡 |
| [Q9](#q9) | normal pdf and cdf | 🟡 |
| [Q10](#q10) | scipy.stats — build and query a distribution | 🟡 |
| [Q11](#q11) | 68-95-99.7 rule — verify with code | 🟢 |
| [Q12](#q12) | z-score — standardize a data point | 🟢 |
| [Q13](#q13) | Central Limit Theorem — demonstrate with samples | 🟠 |
| [Q14](#q14) | null vs alternative hypothesis — write them out | 🟢 |
| [Q15](#q15) | p-value interpretation — given output, what does it mean? | 🟡 |
| [Q16](#q16) | independent samples t-test with scipy | 🟡 |
| [Q17](#q17) | chi-square test of independence | 🟡 |
| [Q18](#q18) | one-tailed vs two-tailed test | 🟡 |
| [Q19](#q19) | significance threshold — when to reject H₀ | 🟢 |
| [Q20](#q20) | define Type I and Type II errors | 🟢 |
| [Q21](#q21) | false positive vs false negative — real-world impact | 🟡 |
| [Q22](#q22) | power of test — sample size calculation | 🟠 |
| [Q23](#q23) | Bayes formula — write and apply it | 🟡 |
| [Q24](#q24) | prior, posterior, likelihood — label the parts | 🟡 |
| [Q25](#q25) | medical test — Bayes with rare disease | 🟠 |
| [Q26](#q26) | Pearson correlation — compute and interpret | 🟡 |
| [Q27](#q27) | Spearman correlation — when to use it | 🟡 |
| [Q28](#q28) | covariance matrix — build and interpret | 🟡 |
| [Q29](#q29) | A/B test end-to-end — proportions z-test | 🟠 |
| [Q30](#q30) | interpret regression output — coefficients and p-values | 🟠 |

---

<a id="q1"></a>

### Q1 · Descriptive Stats — Mean, Median, Mode 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q1](./practice_local.py)


You have a list of salaries: `[45000, 52000, 48000, 55000, 51000, 250000, 49000, 53000, 47000, 50000]`. Compute mean, median, and mode. Which one best represents the "typical" salary and why?


<details>
<summary>💡 Hint</summary>
Use np.mean, np.median, and stats.mode. Compare all three — the $250K outlier will skew one of them.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
from scipy import stats

salaries = [45000, 52000, 48000, 55000, 51000, 250000, 49000, 53000, 47000, 50000]

mean   = np.mean(salaries)           # 70000.0  ← pulled up by $250K outlier
median = np.median(salaries)         # 50500.0  ← robust to the outlier
mode   = stats.mode(salaries).mode   # 45000    ← first value (all appear once)

print(f"Mean:   ${mean:,.0f}")     # $70,000
print(f"Median: ${median:,.0f}")   # $50,500
print(f"Mode:   ${mode:,.0f}")     # $45,000
```

**Why:** Median is the best answer. The $250K outlier pulls the mean up by ~$20K, making it unrepresentative. Median ignores the outlier and reports the actual middle of the distribution.
</details>

---

<a id="q2"></a>

### Q2 · Descriptive Stats — Std vs Variance, Bessel Correction 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q2](./practice_local.py)


Given `data = [4, 8, 6, 5, 3, 2, 8, 9, 2, 5]`, compute both sample variance and sample standard deviation. Explain what `ddof=1` means and why you use it.


<details>
<summary>💡 Hint</summary>
np.var and np.std both accept ddof. ddof=1 divides by n-1 instead of n — this is Bessel's correction for sample estimates.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np

data = [4, 8, 6, 5, 3, 2, 8, 9, 2, 5]

var = np.var(data, ddof=1)    # sample variance  ← divides by n-1
std = np.std(data, ddof=1)    # sample std       ← sqrt of variance

print(f"Variance: {var:.2f}")   # 5.43
print(f"Std dev:  {std:.2f}")   # 2.33
print(f"Check: std² = {std**2:.2f} == variance: {var:.2f}")
```

**Why:** `ddof=1` applies Bessel's correction — dividing by n-1 instead of n gives an unbiased estimate of the population variance when you only have a sample. Std deviation is just the square root of variance, and it shares the same units as the original data (making it more interpretable).
</details>

---

<a id="q3"></a>

### Q3 · Descriptive Stats — IQR and Outlier Detection 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q3](./practice_local.py)


Given exam scores `[55, 60, 62, 65, 68, 70, 71, 72, 73, 75, 76, 78, 80, 95, 150]`, compute the IQR and use the 1.5×IQR rule to identify outliers.


<details>
<summary>💡 Hint</summary>
IQR = Q3 - Q1. Outliers are values below Q1 - 1.5*IQR or above Q3 + 1.5*IQR. Use np.percentile or stats.iqr.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
from scipy import stats

scores = [55, 60, 62, 65, 68, 70, 71, 72, 73, 75, 76, 78, 80, 95, 150]

q1  = np.percentile(scores, 25)    # 65.0
q3  = np.percentile(scores, 75)    # 78.0
iqr = stats.iqr(scores)            # 13.0

lower_fence = q1 - 1.5 * iqr      # 45.5
upper_fence = q3 + 1.5 * iqr      # 97.5

outliers = [x for x in scores if x < lower_fence or x > upper_fence]

print(f"Q1={q1}, Q3={q3}, IQR={iqr}")
print(f"Fences: [{lower_fence}, {upper_fence}]")
print(f"Outliers: {outliers}")     # [150]
```

**Why:** IQR-based detection is robust — it doesn't assume a normal distribution and isn't thrown off by the very outliers it's trying to find (unlike std-based methods where extreme values inflate the std).
</details>

---

<a id="q4"></a>

### Q4 · Descriptive Stats — Skewness 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q4](./practice_local.py)


Compute skewness for two datasets: symmetric data `[5, 6, 7, 8, 9]` and right-skewed data `[1, 2, 3, 4, 100]`. Explain what positive skewness means.


<details>
<summary>💡 Hint</summary>
Use scipy.stats.skew(). Positive = right tail is longer. Negative = left tail is longer.
</details>

<details>
<summary>✅ Answer</summary>

```python
from scipy import stats

symmetric = [5, 6, 7, 8, 9]
right_skewed = [1, 2, 3, 4, 100]   # 100 is a high outlier

sym_skew  = stats.skew(symmetric)      # ~0.0  ← balanced
rskew     = stats.skew(right_skewed)   # ~2.2  ← right (positive) skew

print(f"Symmetric skewness: {sym_skew:.2f}")     # 0.00
print(f"Right-skewed skewness: {rskew:.2f}")     # ~2.24
```

**Why:** Positive skewness means the tail stretches to the right — a few high values pull the mean above the median. This is common in income, house prices, and response times. When skewness > 1, prefer median over mean as the center measure.
</details>

---

<a id="q5"></a>

### Q5 · Descriptive Stats — pandas describe() 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q5](./practice_local.py)


Create a pandas Series from `[23, 25, 22, 28, 35, 21, 24, 26, 27, 29]`. Call `.describe()` and identify what each output line tells you.


<details>
<summary>💡 Hint</summary>
pd.Series().describe() returns count, mean, std, min, 25%, 50%, 75%, max. The 50% percentile is the median.
</details>

<details>
<summary>✅ Answer</summary>

```python
import pandas as pd

ages = pd.Series([23, 25, 22, 28, 35, 21, 24, 26, 27, 29])
summary = ages.describe()

print(summary)
# count    10.000   ← number of values
# mean     26.000   ← arithmetic average
# std       3.742   ← sample standard deviation
# min      21.000   ← smallest value
# 25%      23.250   ← first quartile
# 50%      25.500   ← median
# 75%      27.750   ← third quartile
# max      35.000   ← largest value
```

**Why:** `describe()` gives you a rapid snapshot of center, spread, and range. The gap between mean (26) and median (25.5) is tiny here — confirming near-symmetric data. The jump from 75% (27.75) to max (35) hints at a mild outlier on the high end.
</details>

---

<a id="q6"></a>

### Q6 · Distributions — Uniform Random Sampling 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q6](./practice_local.py)


Generate 5 random floats uniformly distributed between 10 and 50. Then generate 5 random integers uniformly between 1 and 6 (like dice rolls). Use numpy.


<details>
<summary>💡 Hint</summary>
np.random.uniform(low, high, size) for floats. np.random.randint(low, high+1, size) for integers. Or use scipy.stats.uniform.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# Continuous uniform: any value between 10 and 50
floats = np.random.uniform(low=10, high=50, size=5)   # [47.4, 19.5, 23.1, ...]
print(f"Random floats: {floats.round(1)}")

# Discrete uniform: integers 1-6 (dice)
dice = np.random.randint(low=1, high=7, size=5)        # [1, 5, 4, ...]
print(f"Dice rolls: {dice}")

# Using scipy.stats
dist = stats.uniform(loc=10, scale=40)   # scale = high - low
samples = dist.rvs(size=5)
```

**Why:** Uniform distributions are used for random hyperparameter search, train/test splits, and simulations where all outcomes are equally likely. The key gotcha: `np.random.randint` high is exclusive, so use `high=7` for dice.
</details>

---

<a id="q7"></a>

### Q7 · Distributions — Binomial PMF 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q7](./practice_local.py)


You flip a fair coin 10 times. Use `scipy.stats.binom` to compute: P(exactly 7 heads), P(at most 7 heads), and P(at least 8 heads).


<details>
<summary>💡 Hint</summary>
stats.binom(n=10, p=0.5). Use .pmf(k) for exact, .cdf(k) for at-most, and 1 - .cdf(k-1) for at-least.
</details>

<details>
<summary>✅ Answer</summary>

```python
from scipy import stats

coin = stats.binom(n=10, p=0.5)   # 10 flips, fair coin

p_exactly_7 = coin.pmf(7)             # P(X = 7)
p_at_most_7 = coin.cdf(7)             # P(X <= 7)
p_at_least_8 = 1 - coin.cdf(7)        # P(X >= 8) = 1 - P(X <= 7)

print(f"P(exactly 7 heads):  {p_exactly_7:.4f}")   # 0.1172
print(f"P(at most 7 heads):  {p_at_most_7:.4f}")   # 0.9453
print(f"P(at least 8 heads): {p_at_least_8:.4f}")  # 0.0547
```

**Why:** Binomial models any fixed number of yes/no trials with constant probability. In ML: modeling whether k out of n predictions are correct, or whether k emails out of n are spam.
</details>

---

<a id="q8"></a>

### Q8 · Distributions — Poisson PMF 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q8](./practice_local.py)


A server receives on average 3 API calls per second. Model this as a Poisson distribution. Find: P(exactly 0 calls), P(exactly 3 calls), P(more than 5 calls).


<details>
<summary>💡 Hint</summary>
stats.poisson(mu=3). Use .pmf(k) for exact counts, and 1 - .cdf(5) for "more than 5".
</details>

<details>
<summary>✅ Answer</summary>

```python
from scipy import stats

api_calls = stats.poisson(mu=3)   # average 3 calls/second

p_zero   = api_calls.pmf(0)         # P(X = 0) — server idle
p_three  = api_calls.pmf(3)         # P(X = 3) — at the mean
p_over_5 = 1 - api_calls.cdf(5)    # P(X > 5) — overloaded?

print(f"P(0 calls):      {p_zero:.4f}")    # 0.0498
print(f"P(3 calls):      {p_three:.4f}")   # 0.2240
print(f"P(> 5 calls):    {p_over_5:.4f}")  # 0.0839
```

**Why:** Poisson models count events in a fixed time/space window. Use it for: API requests per second, errors per day, support tickets per hour. Key property: mean equals variance (both equal mu).
</details>

---

<a id="q9"></a>

### Q9 · Distributions — Normal PDF and CDF 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q9](./practice_local.py)


Test scores are normally distributed with mean=75, std=12. Find: P(score > 90), P(score < 60), and the score at the 95th percentile.


<details>
<summary>💡 Hint</summary>
stats.norm(loc=75, scale=12). Use .cdf(x) for "less than x". For "greater than", use 1 - .cdf(x). Use .ppf(0.95) for the 95th percentile.
</details>

<details>
<summary>✅ Answer</summary>

```python
from scipy import stats

scores = stats.norm(loc=75, scale=12)

p_above_90    = 1 - scores.cdf(90)    # P(X > 90)
p_below_60    = scores.cdf(60)        # P(X < 60)
percentile_95 = scores.ppf(0.95)      # 95th percentile score

print(f"P(score > 90):    {p_above_90:.3f}")     # 0.106 → ~10.6%
print(f"P(score < 60):    {p_below_60:.3f}")     # 0.106 → ~10.6%
print(f"95th percentile:  {percentile_95:.1f}")  # 94.7
```

**Why:** `.cdf(x)` gives the area to the LEFT (cumulative up to x). `.ppf(p)` is the inverse — it answers "what x value has p% of the distribution below it." These are the two most common operations when working with normal distributions.
</details>

---

<a id="q10"></a>

### Q10 · Distributions — scipy.stats Distribution Object 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q10](./practice_local.py)


Build a t-distribution with 20 degrees of freedom using scipy.stats. Compute its PDF at x=0, CDF at x=2.0, and generate 10 random samples.


<details>
<summary>💡 Hint</summary>
stats.t(df=20). All scipy distributions share the same interface: .pdf(), .cdf(), .ppf(), .rvs(). The t-distribution has heavier tails than normal — useful when n < 30.
</details>

<details>
<summary>✅ Answer</summary>

```python
from scipy import stats
import numpy as np

np.random.seed(42)

t_dist = stats.t(df=20)   # t-distribution with 20 degrees of freedom

pdf_at_0   = t_dist.pdf(0)       # peak density at center
cdf_at_2   = t_dist.cdf(2.0)     # P(T <= 2.0)
samples    = t_dist.rvs(size=10) # random samples

print(f"PDF at x=0:  {pdf_at_0:.4f}")    # 0.3940 (slightly less than normal's 0.3989)
print(f"CDF at x=2:  {cdf_at_2:.4f}")   # 0.9697
print(f"10 samples:  {samples.round(2)}")
```

**Why:** The t-distribution has heavier tails than the normal — it accounts for extra uncertainty when estimating from small samples. As df increases toward infinity, it converges to the standard normal. Use t for sample sizes < 30 or when population std is unknown.
</details>

---

<a id="q11"></a>

### Q11 · Normal Distribution — 68-95-99.7 Rule 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q11](./practice_local.py)


Heights are normally distributed: mean=170cm, std=10cm. Verify the 68-95-99.7 rule using scipy — compute what fraction of the population falls within 1, 2, and 3 standard deviations of the mean.


<details>
<summary>💡 Hint</summary>
For within 1 std: compute cdf(mean + std) - cdf(mean - std). Repeat for 2 and 3 std.
</details>

<details>
<summary>✅ Answer</summary>

```python
from scipy import stats

heights = stats.norm(loc=170, scale=10)

within_1std = heights.cdf(180) - heights.cdf(160)   # μ±σ
within_2std = heights.cdf(190) - heights.cdf(150)   # μ±2σ
within_3std = heights.cdf(200) - heights.cdf(140)   # μ±3σ

print(f"Within 1 std: {within_1std:.3f}  (expect ~0.683)")
print(f"Within 2 std: {within_2std:.3f}  (expect ~0.954)")
print(f"Within 3 std: {within_3std:.3f}  (expect ~0.997)")
```

**Why:** The 68-95-99.7 rule is a mental shortcut. In practice: a data point 3 std from the mean is extremely rare (0.3% probability). This is why "3-sigma" events in finance or engineering are considered exceptional — and why z-scores beyond ±3 often flag outliers.
</details>

---

<a id="q12"></a>

### Q12 · Normal Distribution — Z-Score 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q12](./practice_local.py)


A student scored 88 on an exam where the class mean is 75 and std is 12. Compute the z-score and interpret it. Then compute what raw score corresponds to a z-score of -1.5.


<details>
<summary>💡 Hint</summary>
z = (x - mean) / std. To convert back: x = mean + z * std. This is standardization — it puts any normal distribution on a common scale.
</details>

<details>
<summary>✅ Answer</summary>

```python
mean = 75
std  = 12

# Forward: raw score to z-score
score = 88
z = (score - mean) / std     # 1.083

# Backward: z-score to raw score
z_target = -1.5
raw_score = mean + z_target * std   # 75 + (-1.5)(12) = 57.0

print(f"Z-score for 88: {z:.3f}")          # 1.083
print(f"Score for z=-1.5: {raw_score}")    # 57.0

# Verify: what percentile is 88?
from scipy import stats
percentile = stats.norm.cdf(z) * 100
print(f"Student is at the {percentile:.1f}th percentile")  # 86.1th
```

**Why:** Z-scores let you compare values across different scales — a z=1.08 means the student is about 1 standard deviation above the mean, in the top ~14% of the class. This standardization is also the first step in many ML preprocessing pipelines (StandardScaler).
</details>

---

<a id="q13"></a>

### Q13 · Normal Distribution — Central Limit Theorem 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q13](./practice_local.py)


Demonstrate the CLT: generate a highly skewed exponential population (scale=2, size=100000). Then take 1000 samples of size 50 each and compute each sample mean. Show that the distribution of sample means is approximately normal even though the population is skewed.


<details>
<summary>💡 Hint</summary>
Use np.random.exponential() for the population. Use a list comprehension to create 1000 sample means. Compare stats.skew() on the population vs the sample means.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
from scipy import stats

np.random.seed(42)

# Population: highly right-skewed
population = np.random.exponential(scale=2, size=100000)
pop_skew = stats.skew(population)

# Sample means: take 1000 samples of n=50 each
sample_means = [np.mean(np.random.choice(population, size=50)) for _ in range(1000)]
means_skew = stats.skew(sample_means)

print(f"Population skewness:    {pop_skew:.2f}")    # ~2.0 — very skewed
print(f"Sample means skewness:  {means_skew:.2f}")  # ~0.1 — near normal

print(f"Population mean: {np.mean(population):.2f}")
print(f"Mean of sample means: {np.mean(sample_means):.2f}")  # same — unbiased
```

**Why:** The CLT is why we can use normal-distribution-based statistics (t-tests, confidence intervals) on non-normal data — as long as sample size is large enough (n > 30 is the typical threshold). The mean of the sampling distribution equals the population mean, and its std is SE = σ/√n.
</details>

---

<a id="q14"></a>

### Q14 · Hypothesis Testing — State Null and Alternative Hypotheses 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q14](./practice_local.py)


For each scenario, write H₀ and H₁:
1. Testing whether a new drug lowers blood pressure compared to placebo
2. Checking if a coin is fair
3. Testing whether a new checkout page has a higher conversion rate than the old one


<details>
<summary>💡 Hint</summary>
H₀ is always "no effect / no difference." H₁ is the claim you're trying to prove. H₁ can be one-sided (greater/less) or two-sided (just "different").
</details>

<details>
<summary>✅ Answer</summary>

```python
# Scenario 1: Drug study
# H₀: mean BP with drug == mean BP with placebo  (no effect)
# H₁: mean BP with drug < mean BP with placebo   (one-tailed: lower)

# Scenario 2: Coin fairness
# H₀: P(heads) = 0.5  (fair coin)
# H₁: P(heads) != 0.5 (two-tailed: biased in either direction)

# Scenario 3: Checkout conversion
# H₀: new_rate == old_rate  (no improvement)
# H₁: new_rate > old_rate   (one-tailed: specifically testing for improvement)

# Rule: H₀ always includes equality (=, <=, >=)
#       H₁ is the research hypothesis you're trying to support
#       Two-tailed when direction doesn't matter; one-tailed when it does
print("Hypotheses stated (see comments above)")
```

**Why:** Getting hypotheses right before collecting data is non-negotiable. Switching from two-tailed to one-tailed after seeing results is a form of p-hacking — it halves the p-value, artificially inflating significance.
</details>

---

<a id="q15"></a>

### Q15 · Hypothesis Testing — P-Value Interpretation 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q15](./practice_local.py)


A t-test returns p-value = 0.032. Answer these:
1. Do you reject H₀ at α = 0.05?
2. Do you reject H₀ at α = 0.01?
3. Does p = 0.032 mean there's a 3.2% chance H₀ is true?
4. What does the p-value actually mean?


<details>
<summary>💡 Hint</summary>
The most common p-value misconception: it is NOT the probability that H₀ is true. It's a conditional probability about your data.
</details>

<details>
<summary>✅ Answer</summary>

```python
p_value = 0.032
alpha_05 = 0.05
alpha_01 = 0.01

reject_at_05 = p_value < alpha_05    # True  ← 0.032 < 0.05
reject_at_01 = p_value < alpha_01    # False ← 0.032 > 0.01

print(f"Reject H₀ at α=0.05: {reject_at_05}")   # True
print(f"Reject H₀ at α=0.01: {reject_at_01}")   # False

# What p=0.032 ACTUALLY means:
# "If H₀ were true (no real effect), there is a 3.2% probability of
#  observing a test statistic this extreme or more extreme by random chance."

# What it does NOT mean:
# - NOT P(H₀ is true) = 3.2%
# - NOT P(the result is a fluke) = 3.2%
# - NOT P(your hypothesis is correct) = 96.8%
print("p-value = P(data this extreme | H₀ is true) — not P(H₀ is true)")
```

**Why:** Misinterpreting p-values is one of the most common errors in data science. The p-value tells you about the data given H₀ — not about H₀ given the data. For that, you'd need Bayesian inference.
</details>

---

<a id="q16"></a>

### Q16 · Hypothesis Testing — Independent Samples T-Test 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q16](./practice_local.py)


Two versions of a recommendation engine were tested. Group A (old) and Group B (new) each had 100 users. Engagement scores were collected. Run a t-test to determine if the new engine is significantly better. Use `np.random.seed(42)`, Group A ~ N(10, 2), Group B ~ N(11, 2), each n=100.


<details>
<summary>💡 Hint</summary>
Use stats.ttest_ind(group_a, group_b). The function returns (t_statistic, p_value). A negative t-stat means group_a mean < group_b mean.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
from scipy import stats

np.random.seed(42)

group_a = np.random.normal(loc=10, scale=2, size=100)   # old engine
group_b = np.random.normal(loc=11, scale=2, size=100)   # new engine

t_stat, p_value = stats.ttest_ind(group_a, group_b)

print(f"Group A mean: {group_a.mean():.3f}")
print(f"Group B mean: {group_b.mean():.3f}")
print(f"T-statistic:  {t_stat:.3f}")
print(f"P-value:      {p_value:.4f}")

if p_value < 0.05:
    print("Significant — the new engine is statistically better")
else:
    print("Not significant — cannot conclude new engine is better")
```

**Why:** `ttest_ind` assumes independent samples and roughly equal variances (use `equal_var=False` for Welch's t-test when variances differ). Always check both statistical significance (p < 0.05) AND practical significance (effect size like Cohen's d).
</details>

---

<a id="q17"></a>

### Q17 · Hypothesis Testing — Chi-Square Test 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q17](./practice_local.py)


You run an experiment: does browser type (Chrome, Firefox, Safari) affect whether users convert (yes/no)? Build a contingency table and run a chi-square test of independence.

```
             Convert  No Convert
Chrome          120       380
Firefox          60       240
Safari           30       170
```


<details>
<summary>💡 Hint</summary>
Use stats.chi2_contingency(table). It returns (chi2, p_value, dof, expected). p < 0.05 means browser type and conversion are NOT independent.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
from scipy import stats

# Rows: browser, Columns: [convert, no_convert]
contingency = np.array([
    [120, 380],   # Chrome
    [ 60, 240],   # Firefox
    [ 30, 170],   # Safari
])

chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

print(f"Chi2 statistic: {chi2:.3f}")
print(f"P-value:        {p_value:.4f}")
print(f"Degrees of freedom: {dof}")

if p_value < 0.05:
    print("Browser type and conversion are NOT independent (significant)")
else:
    print("No significant relationship between browser and conversion")
```

**Why:** Chi-square tests work on categorical data. It compares observed cell counts to expected counts under independence. The degrees of freedom = (rows-1) × (cols-1) = 2 here. If any expected cell is < 5, consider Fisher's exact test instead.
</details>

---

<a id="q18"></a>

### Q18 · Hypothesis Testing — One-Tailed vs Two-Tailed 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q18](./practice_local.py)


You run a t-test comparing Group A (mean=10) and Group B (mean=10.5). The two-tailed p-value is 0.12. What is the one-tailed p-value if you hypothesized Group B > Group A? Should you switch to one-tailed after seeing the result?


<details>
<summary>💡 Hint</summary>
One-tailed p = two-tailed p / 2 (when result is in the expected direction). But you must decide tail direction BEFORE data collection, not after.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
from scipy import stats

np.random.seed(42)
group_a = np.random.normal(10.0, 2, 80)
group_b = np.random.normal(10.5, 2, 80)

# Two-tailed: H₁ is "they differ" (either direction)
t_stat, p_two_tailed = stats.ttest_ind(group_a, group_b)

# One-tailed: H₁ is "B > A" — only care about right tail
# When t_stat is negative (B > A in ttest_ind(a, b)), the one-tailed p is:
p_one_tailed = p_two_tailed / 2   # if result is in the hypothesized direction

print(f"Two-tailed p: {p_two_tailed:.4f}")
print(f"One-tailed p: {p_one_tailed:.4f}")
print()
print("CRITICAL: You CANNOT switch to one-tailed after seeing results.")
print("Doing so is p-hacking — it halves p-value without scientific justification.")
```

**Why:** One-tailed tests are appropriate only when you pre-specify the direction of your hypothesis. They're more powerful (lower p for the same data) but carry a cost: if the effect is in the opposite direction, you can't detect it.
</details>

---

<a id="q19"></a>

### Q19 · Hypothesis Testing — Significance Threshold 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q19](./practice_local.py)


A study reports p = 0.049 at α = 0.05. Another study reports p = 0.051. Explain: (1) are both conclusions valid? (2) what's wrong with the "bright line" at 0.05? (3) what should you report alongside p-value?


<details>
<summary>💡 Hint</summary>
0.049 and 0.051 are functionally identical in terms of evidence. Report effect size (Cohen's d, relative lift) and confidence intervals alongside p-value.
</details>

<details>
<summary>✅ Answer</summary>

```python
# p = 0.049 vs p = 0.051 — barely different evidence strength
# The binary reject/accept framing is an oversimplification

# What to always report alongside p-value:
import numpy as np
from scipy import stats

np.random.seed(42)
a = np.random.normal(10, 2, 100)
b = np.random.normal(10.4, 2, 100)

t_stat, p_value = stats.ttest_ind(a, b)

# Effect size: Cohen's d
pooled_std = np.sqrt((a.std(ddof=1)**2 + b.std(ddof=1)**2) / 2)
cohens_d   = (b.mean() - a.mean()) / pooled_std   # ~0.2 = small effect

# Confidence interval
mean_diff = b.mean() - a.mean()
se_diff   = pooled_std * np.sqrt(2/100)
ci        = (mean_diff - 1.96*se_diff, mean_diff + 1.96*se_diff)

print(f"p-value: {p_value:.4f}")
print(f"Cohen's d: {cohens_d:.3f}")       # practical significance
print(f"95% CI on difference: {ci}")      # range of plausible effects
```

**Why:** Statistical significance does not equal practical importance. A tiny effect (d=0.01) can reach p < 0.05 with a large enough sample. Always report effect size and confidence intervals — they tell you the magnitude and precision of the effect.
</details>

---

<a id="q20"></a>

### Q20 · Type I and Type II Errors — Definitions 🟢

> 🛠️ **Solve locally:** [practice_local.py → Q20](./practice_local.py)


In your own words and with a fraud detection example, explain: (1) Type I error, (2) Type II error, (3) which is worse, and (4) how you control each.


<details>
<summary>💡 Hint</summary>
Type I = false alarm (flag a good transaction as fraud). Type II = miss (let a real fraud through). The trade-off is controlled by the classification threshold.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Type I Error (False Positive, α):
#   Reality: transaction is LEGITIMATE (H₀ is true)
#   Decision: flag it as FRAUD (reject H₀)
#   Cost: customer is blocked, frustrated, churns
#   Control: raise α threshold (0.05 → 0.01) to flag less aggressively

# Type II Error (False Negative, β):
#   Reality: transaction IS FRAUD (H₀ is false)
#   Decision: let it PASS (fail to reject H₀)
#   Cost: financial loss, chargebacks, reputation damage
#   Control: increase power (larger sample, more sensitive test)

# The trade-off:
#   Lowering fraud threshold → fewer Type II (catch more fraud)
#                           → more Type I (annoy more legit users)
#   Raising fraud threshold → fewer Type I (fewer false blocks)
#                           → more Type II (miss more fraud)

# Which is worse? Context-dependent:
#   Medical test (cancer): Type II worse — missing real cancer is dangerous
#   Spam filter: Type I worse — blocking real email is more disruptive
#   Fraud detection: balance both — usually weighted by dollar cost

print("Type I = False Positive (false alarm), controlled by alpha")
print("Type II = False Negative (missed detection), controlled by beta/power")
```

**Why:** Understanding this trade-off is essential for setting classification thresholds in production ML systems. There's no universally correct answer — the right balance depends on the cost asymmetry between the two error types.
</details>

---

<a id="q21"></a>

### Q21 · Type I and Type II Errors — Medical Test Trade-Off 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q21](./practice_local.py)


A cancer screening test has sensitivity = 90% (catches 90% of real cases) and specificity = 85% (correctly clears 85% of non-cases). For 1000 people where 10% have cancer: compute TP, FP, FN, TN. Identify which cells are Type I and Type II errors.


<details>
<summary>💡 Hint</summary>
TP = sensitivity × cases. FN = (1-sensitivity) × cases. FP = (1-specificity) × non-cases. TN = specificity × non-cases.
</details>

<details>
<summary>✅ Answer</summary>

```python
n_total     = 1000
prevalence  = 0.10      # 10% have cancer
sensitivity = 0.90      # P(positive | cancer)
specificity = 0.85      # P(negative | no cancer)

n_cases     = int(n_total * prevalence)        # 100 with cancer
n_no_cases  = n_total - n_cases                # 900 without cancer

TP = sensitivity * n_cases          # 90   ← correctly detected cancer
FN = (1 - sensitivity) * n_cases    # 10   ← TYPE II ERROR: missed cancer
FP = (1 - specificity) * n_no_cases # 135  ← TYPE I ERROR: false alarm
TN = specificity * n_no_cases       # 765  ← correctly cleared

print(f"True Positive:  {TP:.0f}  (correct cancer detections)")
print(f"False Negative: {FN:.0f}  ← Type II Error (missed cancer!)")
print(f"False Positive: {FP:.0f} ← Type I Error (unnecessary worry)")
print(f"True Negative:  {TN:.0f}  (correct clearances)")
print(f"Precision: {TP/(TP+FP):.2%}")   # 40% — surprisingly low
```

**Why:** Even with decent sensitivity and specificity, low prevalence means most positive tests are false positives — the same insight as Bayes' theorem. This is why mass screening of low-prevalence conditions generates many false alarms.
</details>

---

<a id="q22"></a>

### Q22 · Type I and Type II Errors — Power Calculation 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q22](./practice_local.py)


You're designing an A/B test. Baseline conversion = 5%, minimum detectable effect = 1% (absolute). Set α = 0.05, target power = 0.80. Calculate the required sample size per group using statsmodels.


<details>
<summary>💡 Hint</summary>
Use NormalIndPower().solve_power(). The effect_size here is Cohen's h for proportions: 2*arcsin(sqrt(p2)) - 2*arcsin(sqrt(p1)). Or use proportion_effectsize from statsmodels.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

baseline = 0.05     # 5% current conversion
target   = 0.06     # 6% minimum detectable (1% absolute lift)
alpha    = 0.05
power    = 0.80

# Cohen's h: effect size for proportions
effect_size = proportion_effectsize(target, baseline)

analysis   = NormalIndPower()
n_required = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power)

print(f"Effect size (Cohen's h): {effect_size:.4f}")
print(f"Required n per group:    {int(np.ceil(n_required))}")
print(f"Total required:          {int(np.ceil(n_required)) * 2}")
# Result: ~3,500 per group for this small effect size
```

**Why:** Power analysis MUST happen before the experiment. Running until you see p < 0.05 is p-hacking (optional stopping). Under-powered tests miss real effects (Type II error). This formula tells you exactly how long to run the test.
</details>

---

<a id="q23"></a>

### Q23 · Bayes' Theorem — Formula and Application 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q23](./practice_local.py)


Write out Bayes' theorem formula and implement it in Python. Apply it to: a spam filter where P(spam) = 0.3, P(word "free" | spam) = 0.8, P(word "free" | not spam) = 0.1. Given an email contains "free", compute P(spam | "free").


<details>
<summary>💡 Hint</summary>
P(A|B) = P(B|A) × P(A) / P(B). P(B) = P(B|A)×P(A) + P(B|not A)×P(not A). This is the law of total probability in the denominator.
</details>

<details>
<summary>✅ Answer</summary>

```python
# Bayes' theorem: P(A|B) = P(B|A) × P(A) / P(B)

# Variables:
# A = email is spam
# B = email contains "free"

p_spam                 = 0.3    # P(A) — prior: 30% of emails are spam
p_free_given_spam      = 0.8    # P(B|A) — likelihood
p_free_given_not_spam  = 0.1    # P(B|not A)
p_not_spam             = 1 - p_spam

# Law of total probability: P(B) = P(B|A)×P(A) + P(B|not A)×P(not A)
p_free = p_free_given_spam * p_spam + p_free_given_not_spam * p_not_spam

# Bayes' theorem: P(spam | free)
p_spam_given_free = (p_free_given_spam * p_spam) / p_free

print(f"P(contains 'free'):          {p_free:.3f}")
print(f"P(spam | contains 'free'):   {p_spam_given_free:.3f}")  # 0.774
```

**Why:** The prior P(spam) = 0.3 gets updated to a posterior of 0.77 after observing "free". This is exactly how Naive Bayes spam classifiers work — each word updates the probability. The more spam-indicative words you see, the higher the posterior climbs.
</details>

---

<a id="q24"></a>

### Q24 · Bayes' Theorem — Prior, Posterior, Likelihood 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q24](./practice_local.py)


Label each term in this expression: `P(disease|positive) = P(positive|disease) × P(disease) / P(positive)`. Then explain: what happens to the posterior if the prior (prevalence) drops from 10% to 1%?


<details>
<summary>💡 Hint</summary>
Prior = P(disease), Likelihood = P(positive|disease), Evidence = P(positive), Posterior = P(disease|positive). As prior drops, posterior drops dramatically.
</details>

<details>
<summary>✅ Answer</summary>

```python
def bayes(prior, sensitivity, specificity):
    """P(disease | positive test)"""
    likelihood = sensitivity               # P(positive | disease)
    false_pos  = 1 - specificity          # P(positive | no disease)
    evidence   = likelihood * prior + false_pos * (1 - prior)
    posterior  = (likelihood * prior) / evidence
    return posterior

# Same test: sensitivity=0.99, specificity=0.99
# Effect of varying the PRIOR (prevalence):
for prevalence in [0.10, 0.05, 0.01, 0.001]:
    post = bayes(prior=prevalence, sensitivity=0.99, specificity=0.99)
    print(f"Prevalence {prevalence:.1%} → P(disease|positive): {post:.2%}")

# Output:
# Prevalence 10.0% → P(disease|positive): 91.67%
# Prevalence  5.0% → P(disease|positive): 83.90%
# Prevalence  1.0% → P(disease|positive): 50.00%
# Prevalence  0.1% → P(disease|positive):  9.02%
```

**Why:** The prior dominates when disease is rare — a 99% accurate test gives only 9% certainty for a 0.1% prevalence disease. This is why Bayesian reasoning is critical in medical testing and rare event detection: the base rate matters as much as test accuracy.
</details>

---

<a id="q25"></a>

### Q25 · Bayes' Theorem — Medical Test Full Example 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q25](./practice_local.py)


A disease affects 1% of the population. A test has 99% sensitivity and 99% specificity. (1) What is P(disease | positive test)? (2) What if you test positive twice, independently? Update the posterior from test 1 as the new prior for test 2.


<details>
<summary>💡 Hint</summary>
For the second test, use the posterior from test 1 as the new prior. This is sequential Bayesian updating — each new piece of evidence refines your belief.
</details>

<details>
<summary>✅ Answer</summary>

```python
def bayes_update(prior, sensitivity, specificity):
    p_pos_disease    = sensitivity
    p_pos_no_disease = 1 - specificity
    p_positive = p_pos_disease * prior + p_pos_no_disease * (1 - prior)
    return (p_pos_disease * prior) / p_positive

# Test parameters
sensitivity = 0.99
specificity = 0.99
prior       = 0.01    # 1% prevalence

# First positive test
posterior_1 = bayes_update(prior, sensitivity, specificity)
print(f"After 1st positive test: P(disease) = {posterior_1:.3f}")   # ~0.50

# Second positive test — use posterior_1 as new prior
posterior_2 = bayes_update(posterior_1, sensitivity, specificity)
print(f"After 2nd positive test: P(disease) = {posterior_2:.3f}")   # ~0.99

# Intuition:
# One positive: 50% — still uncertain due to low prior
# Two positives: 99% — two independent confirmations nearly certain
```

**Why:** Sequential Bayesian updating shows how evidence accumulates. This is the power of Bayesian thinking — you never reset to zero; each test builds on prior knowledge. This is the mathematical basis for Bayesian filtering in robotics, NLP, and medical diagnosis.
</details>

---

<a id="q26"></a>

### Q26 · Correlation — Pearson Correlation 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q26](./practice_local.py)


Given study hours `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` and exam scores `[50, 55, 58, 63, 67, 72, 75, 80, 85, 90]`, compute Pearson correlation. Interpret the result. Also compute the p-value and explain what it means here.


<details>
<summary>💡 Hint</summary>
Use scipy.stats.pearsonr(x, y). It returns (correlation, p_value). Correlation range: -1 (perfect negative) to +1 (perfect positive). The p-value tests H₀: correlation = 0.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
from scipy import stats

hours  = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
scores = [50, 55, 58, 63, 67, 72, 75, 80, 85, 90]

r, p_value = stats.pearsonr(hours, scores)

print(f"Pearson r: {r:.4f}")       # ~0.998 — nearly perfect linear
print(f"P-value:   {p_value:.6f}") # very small — correlation is real

# Interpretation:
# r = 0.998: extremely strong positive linear relationship
# p < 0.05: the correlation is statistically significant (not due to chance)
# r²: proportion of variance explained
r_squared = r ** 2
print(f"R²: {r_squared:.4f}")      # 0.996 — 99.6% of score variance explained by hours
```

**Why:** Pearson r measures linear correlation. R² tells you the fraction of variance in one variable explained by the other — a directly interpretable measure of effect size for linear relationships. Always check the scatterplot too — r doesn't capture non-linear patterns.
</details>

---

<a id="q27"></a>

### Q27 · Correlation — Spearman Correlation 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q27](./practice_local.py)


A company ranks 8 employees by peer rating (1-8) and manager rating (1-8). Compute Spearman correlation. Explain when you'd choose Spearman over Pearson.

```
Peer:    [1, 2, 3, 4, 5, 6, 7, 8]
Manager: [2, 1, 4, 3, 6, 5, 8, 7]
```


<details>
<summary>💡 Hint</summary>
Use scipy.stats.spearmanr(). Spearman is Pearson applied to ranks — use it when data is ordinal, non-normal, or has outliers that would distort Pearson.
</details>

<details>
<summary>✅ Answer</summary>

```python
from scipy import stats

peer    = [1, 2, 3, 4, 5, 6, 7, 8]
manager = [2, 1, 4, 3, 6, 5, 8, 7]

rho, p_value = stats.spearmanr(peer, manager)

print(f"Spearman rho: {rho:.4f}")     # 0.9762
print(f"P-value:      {p_value:.4f}") # significant

# When to use Spearman vs Pearson:
# Spearman: ordinal data (rankings), non-normal data, outliers present, monotonic (not necessarily linear) relationship
# Pearson:  continuous data, roughly normal, linear relationship expected, no extreme outliers

# Key difference:
# Pearson measures LINEAR correlation (how close to a line)
# Spearman measures MONOTONIC correlation (whether they move together in the same direction, any shape)
```

**Why:** Spearman is more robust — one extreme outlier can drag Pearson r toward -1 or +1, while Spearman (based on ranks) is unaffected. Use Spearman for salary vs happiness (both ordinal-ish), customer satisfaction scores, or any data with potential outliers.
</details>

---

<a id="q28"></a>

### Q28 · Correlation — Covariance Matrix 🟡

> 🛠️ **Solve locally:** [practice_local.py → Q28](./practice_local.py)


Create a DataFrame with 3 columns: height (cm), weight (kg), and age (years) using random data. Compute the covariance matrix and correlation matrix. Explain the difference between the two.


<details>
<summary>💡 Hint</summary>
Use df.cov() and df.corr(). Covariance has units (cm×kg), correlation is unitless (-1 to +1). Correlation = normalized covariance.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
import pandas as pd

np.random.seed(42)

height = np.random.normal(170, 10, 100)
weight = 0.5 * height + np.random.normal(0, 5, 100)  # correlated with height
age    = np.random.uniform(20, 60, 100)               # independent

df = pd.DataFrame({"height": height, "weight": weight, "age": age})

cov_matrix  = df.cov()    # covariance — values depend on units/scale
corr_matrix = df.corr()   # correlation — always -1 to +1

print("Covariance matrix:")
print(cov_matrix.round(2))

print("\nCorrelation matrix:")
print(corr_matrix.round(3))
# height-weight correlation: ~0.89 (strong positive)
# height-age and weight-age: ~0.0  (independent)
```

**Why:** Covariance tells you direction (positive/negative) but its magnitude is hard to interpret — it depends on the units. Correlation normalizes it to [-1, +1], making comparisons possible. In PCA and feature engineering, the covariance matrix is fundamental.
</details>

---

<a id="q29"></a>

### Q29 · Capstone — A/B Test End-to-End 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q29](./practice_local.py)


Run a complete A/B test analysis. Scenario: old checkout page got 320 conversions from 10000 visits (3.2%). New page got 390 conversions from 10000 visits (3.9%). Steps: (1) state hypotheses, (2) compute lift, (3) run proportions z-test, (4) check significance, (5) compute Cohen's h effect size, (6) interpret results.


<details>
<summary>💡 Hint</summary>
Use statsmodels.stats.proportion.proportions_ztest and proportion_effectsize. A complete analysis reports: p-value, lift, effect size, and a clear business recommendation.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
from statsmodels.stats.proportion import proportions_ztest, proportion_effectsize

# Data
clicks_a, n_a = 320, 10000    # control:   3.2% CTR
clicks_b, n_b = 390, 10000    # treatment: 3.9% CTR

rate_a = clicks_a / n_a       # 0.032
rate_b = clicks_b / n_b       # 0.039

# Step 1: Hypotheses
# H₀: rate_a == rate_b  (no improvement)
# H₁: rate_b > rate_a   (new page is better — one-tailed)

# Step 2: Lift
lift = (rate_b - rate_a) / rate_a
print(f"Relative lift: {lift:.1%}")   # 21.9%

# Step 3: Z-test
z_stat, p_value = proportions_ztest([clicks_a, clicks_b], [n_a, n_b])
print(f"Z-statistic: {z_stat:.3f}")
print(f"P-value (two-tailed): {p_value:.4f}")

# Step 4: Significance
print(f"Significant at α=0.05: {p_value < 0.05}")

# Step 5: Effect size
h = proportion_effectsize(rate_b, rate_a)
print(f"Cohen's h: {h:.4f}")    # small effect (~0.04)

# Step 6: Business recommendation
if p_value < 0.05:
    print(f"RECOMMENDATION: Ship new page. {lift:.1%} lift is statistically significant.")
    print(f"At 10,000 daily visitors, this is ~{int((rate_b-rate_a)*10000)} extra conversions/day.")
```

**Why:** A complete A/B analysis requires more than just p < 0.05. Report lift (business impact), effect size (practical significance), and a clear recommendation. Stakeholders don't want p-values — they want to know whether to ship.
</details>

---

<a id="q30"></a>

### Q30 · Capstone — Interpret Regression Output 🟠

> 🛠️ **Solve locally:** [practice_local.py → Q30](./practice_local.py)


Run a simple linear regression predicting exam score from study hours. Interpret: (1) the coefficient, (2) the intercept, (3) the R², (4) the p-value for the coefficient. Use `np.random.seed(42)`, hours ~ U(1,10), score = 50 + 4*hours + N(0,5).


<details>
<summary>💡 Hint</summary>
Use scipy.stats.linregress(x, y). It returns slope, intercept, r_value, p_value, std_err. R² = r_value². The coefficient p-value tests H₀: slope = 0.
</details>

<details>
<summary>✅ Answer</summary>

```python
import numpy as np
from scipy import stats

np.random.seed(42)

hours  = np.random.uniform(1, 10, 100)
scores = 50 + 4 * hours + np.random.normal(0, 5, 100)

slope, intercept, r_value, p_value, std_err = stats.linregress(hours, scores)

r_squared = r_value ** 2

print(f"Coefficient (slope): {slope:.3f}")
print(f"Intercept:           {intercept:.3f}")
print(f"R²:                  {r_squared:.4f}")
print(f"P-value (slope):     {p_value:.6f}")
print(f"Std error:           {std_err:.3f}")

print()
print(f"Interpretation:")
print(f"  Each additional study hour → +{slope:.1f} points on exam")
print(f"  With 0 hours: predicted score = {intercept:.1f}")
print(f"  Study hours explain {r_squared:.1%} of score variance")
print(f"  Slope is {'significant' if p_value < 0.05 else 'not significant'} (p={p_value:.4f})")
```

**Why:** Regression coefficients are the most important output — they quantify the relationship. R² tells you model quality. The p-value on the slope tests whether the predictor adds information (H₀: slope=0, i.e. no linear relationship). Always report all four: coefficient, p-value, R², and confidence interval on the coefficient.
</details>

---

## Navigation

| | |
|---|---|
| 📖 Theory | [theory.md](./theory.md) |
| ⚡ Cheatsheet | [cheetsheet.md](./cheetsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
| 💻 Practice | [practice.md](./practice.md) |
| ⬅️ Prev Module | [../25_python_ai_ecosystem/theory.md](../25_python_ai_ecosystem/theory.md) |
| ➡️ Next Module | [../27_matplotlib_seaborn/theory.md](../27_matplotlib_seaborn/theory.md) |

---

**[🏠 Back to README](../README.md)**
