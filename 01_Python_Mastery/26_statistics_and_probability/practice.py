"""
Statistics and Probability — Practice Problems
Run each section independently to practice the concepts.
"""

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt


# ─────────────────────────────────────────────
# PROBLEM 1: Descriptive Statistics
# ─────────────────────────────────────────────
print("=" * 50)
print("PROBLEM 1: Descriptive Statistics")
print("=" * 50)

salaries = [45000, 52000, 48000, 55000, 51000, 250000, 49000, 53000, 47000, 50000]

mean_sal   = np.mean(salaries)
median_sal = np.median(salaries)
std_sal    = np.std(salaries, ddof=1)
iqr_sal    = stats.iqr(salaries)

print(f"Mean salary:   ${mean_sal:,.0f}")
print(f"Median salary: ${median_sal:,.0f}")
print(f"Std deviation: ${std_sal:,.0f}")
print(f"IQR:           ${iqr_sal:,.0f}")
print(f"Skewness:      {stats.skew(salaries):.2f}")
print()
print("Which better represents typical salary? Median — the $250K outlier pulls mean up by 20%")


# ─────────────────────────────────────────────
# PROBLEM 2: Normal Distribution
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 2: Normal Distribution")
print("=" * 50)

# Model test scores: N(75, 12)
score_dist = stats.norm(loc=75, scale=12)

p_above_90 = 1 - score_dist.cdf(90)
p_below_60 = score_dist.cdf(60)
percentile_95 = score_dist.ppf(0.95)

print(f"P(score > 90):     {p_above_90:.3f}  ({p_above_90*100:.1f}%)")
print(f"P(score < 60):     {p_below_60:.3f}  ({p_below_60*100:.1f}%)")
print(f"95th percentile:   {percentile_95:.1f}")
print(f"68-95-99.7 rule check:")
print(f"  Within 1 std: {score_dist.cdf(75+12) - score_dist.cdf(75-12):.3f}  (expect 0.683)")
print(f"  Within 2 std: {score_dist.cdf(75+24) - score_dist.cdf(75-24):.3f}  (expect 0.954)")


# ─────────────────────────────────────────────
# PROBLEM 3: Hypothesis Testing (t-test)
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 3: Hypothesis Testing")
print("=" * 50)

np.random.seed(42)
# Two groups: control (mean=10) and treatment (mean=11)
control   = np.random.normal(loc=10, scale=2, size=100)
treatment = np.random.normal(loc=11, scale=2, size=100)

t_stat, p_value = stats.ttest_ind(control, treatment)

print(f"Control mean:   {control.mean():.3f}")
print(f"Treatment mean: {treatment.mean():.3f}")
print(f"T-statistic:    {t_stat:.3f}")
print(f"P-value:        {p_value:.4f}")
print(f"Significant:    {'Yes — reject H0' if p_value < 0.05 else 'No — cannot reject H0'}")

# Effect size (Cohen's d)
pooled_std = np.sqrt((control.std(ddof=1)**2 + treatment.std(ddof=1)**2) / 2)
cohens_d = (treatment.mean() - control.mean()) / pooled_std
print(f"Cohen's d:      {cohens_d:.3f}  (effect size)")


# ─────────────────────────────────────────────
# PROBLEM 4: A/B Test — Proportions
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 4: A/B Test — Two Proportions")
print("=" * 50)

from statsmodels.stats.proportion import proportions_ztest

clicks_a, n_a = 320, 10000    # 3.2% CTR
clicks_b, n_b = 390, 10000    # 3.9% CTR

z_stat, p_val = proportions_ztest([clicks_a, clicks_b], [n_a, n_b])

rate_a = clicks_a / n_a
rate_b = clicks_b / n_b
lift   = (rate_b - rate_a) / rate_a

print(f"CTR Group A: {rate_a:.2%}")
print(f"CTR Group B: {rate_b:.2%}")
print(f"Lift: {lift:.1%}")
print(f"Z-statistic: {z_stat:.3f}")
print(f"P-value: {p_val:.4f}")
print(f"Significant: {'Yes' if p_val < 0.05 else 'No'}")


# ─────────────────────────────────────────────
# PROBLEM 5: Bayes' Theorem
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 5: Bayes' Theorem")
print("=" * 50)

def bayesian_update(prior, sensitivity, specificity):
    """P(disease | positive test)"""
    p_pos_disease    = sensitivity
    p_pos_no_disease = 1 - specificity
    p_positive = p_pos_disease * prior + p_pos_no_disease * (1 - prior)
    posterior = (p_pos_disease * prior) / p_positive
    return posterior

# Disease: 1% prevalence, 99% sensitivity, 99% specificity
posterior = bayesian_update(prior=0.01, sensitivity=0.99, specificity=0.99)
print(f"Scenario 1 (rare disease, 1% prevalence):")
print(f"  P(disease | positive test) = {posterior:.2%}")
print(f"  Surprising: even with 99% accurate test, only ~50% chance of disease")

# Higher prevalence
posterior2 = bayesian_update(prior=0.10, sensitivity=0.99, specificity=0.99)
print(f"\nScenario 2 (common disease, 10% prevalence):")
print(f"  P(disease | positive test) = {posterior2:.2%}")


# ─────────────────────────────────────────────
# PROBLEM 6: Confidence Intervals
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 6: Confidence Intervals")
print("=" * 50)

np.random.seed(42)
sample = np.random.normal(loc=100, scale=15, size=30)    # IQ scores, n=30

n    = len(sample)
mean = sample.mean()
se   = stats.sem(sample)

ci_90 = stats.t.interval(0.90, df=n-1, loc=mean, scale=se)
ci_95 = stats.t.interval(0.95, df=n-1, loc=mean, scale=se)
ci_99 = stats.t.interval(0.99, df=n-1, loc=mean, scale=se)

print(f"Sample: n={n}, mean={mean:.1f}, SE={se:.2f}")
print(f"90% CI: ({ci_90[0]:.1f}, {ci_90[1]:.1f})  width={ci_90[1]-ci_90[0]:.1f}")
print(f"95% CI: ({ci_95[0]:.1f}, {ci_95[1]:.1f})  width={ci_95[1]-ci_95[0]:.1f}")
print(f"99% CI: ({ci_99[0]:.1f}, {ci_99[1]:.1f})  width={ci_99[1]-ci_99[0]:.1f}")
print("Observation: higher confidence = wider interval")


# ─────────────────────────────────────────────
# PROBLEM 7: Correlation
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("PROBLEM 7: Correlation Analysis")
print("=" * 50)

np.random.seed(42)
study_hours = np.random.uniform(0, 10, 50)
exam_scores = 50 + 4 * study_hours + np.random.normal(0, 5, 50)   # linear + noise
ice_cream   = np.random.normal(50, 10, 50)   # uncorrelated
drownings   = ice_cream + np.random.normal(0, 5, 50)               # spurious corr

pearson_r,  p1 = stats.pearsonr(study_hours, exam_scores)
spearman_r, p2 = stats.spearmanr(study_hours, exam_scores)
spurious_r, p3 = stats.pearsonr(ice_cream, drownings)

print(f"Study hours vs exam score:")
print(f"  Pearson r = {pearson_r:.3f}, p = {p1:.4f}  ← real causal relationship")
print(f"  Spearman r = {spearman_r:.3f}")
print(f"\nIce cream vs drownings:")
print(f"  Pearson r = {spurious_r:.3f}, p = {p3:.4f}  ← spurious (both driven by summer)")


print("\n✅ All practice problems complete!")
