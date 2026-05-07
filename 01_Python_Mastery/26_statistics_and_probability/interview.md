# 📊 Statistics and Probability — Interview Questions

---

## Beginner

**Q: What is the difference between mean and median, and when should you use each?**

Mean is the arithmetic average — sum of all values divided by the count. Median is the middle value when sorted. For symmetric data without outliers, they're nearly the same. The difference matters when data is skewed or has outliers. A city's average household income might be $80K, but the median might be $55K — because a few millionaires pull the mean up. For ML features like house prices, salary, or response times (right-skewed distributions), median is a better measure of center. For roughly symmetric, well-behaved data (like many ML model errors), mean is fine. Rule of thumb: always check the distribution shape first with a histogram.

---

**Q: What does a p-value actually mean?**

A p-value is the probability of observing a result as extreme as your data, assuming the null hypothesis is true. If p = 0.03, it means: "If there truly were no effect, there's only a 3% chance of seeing a difference this large just by random chance." Common misconception: p-value is NOT the probability that the null hypothesis is true. It's NOT the probability your result is real. It's a conditional probability. The standard threshold is 0.05. Below it: "statistically significant — we reject the null hypothesis." Above it: "not significant — insufficient evidence to reject." Statistical significance ≠ practical importance — a tiny effect in a huge dataset will be significant but may be meaningless.

---

**Q: What is the Central Limit Theorem and why does it matter in ML?**

The Central Limit Theorem states that the distribution of sample means approaches a normal distribution as sample size increases, regardless of the original distribution's shape. For n > 30, this approximation is usually good. Why it matters in ML: it's why we can use t-tests and confidence intervals on non-normal data as long as sample sizes are adequate. It's why model weights in large neural networks often look normally distributed. It's why we can average metrics across many experiments and apply normal-distribution-based statistics to them. Without CLT, we'd need distribution-specific tools for every dataset.

---

## Intermediate

**Q: What is the difference between Type I and Type II errors, and how do you balance them?**

A Type I error (false positive) occurs when you reject the null hypothesis when it's actually true — you conclude there's an effect when there isn't. A Type II error (false negative) occurs when you fail to reject the null hypothesis when it's false — you miss a real effect. They trade off: lowering your significance threshold (α from 0.05 to 0.01) reduces Type I errors but increases Type II errors. The balance depends on business context. In medical trials, a false positive (approving a harmful drug) is catastrophic — so α is set very low. In A/B testing a button color, a false positive (rolling out a neutral change) is cheap — so you can accept α = 0.05. The statistical power (1 - β) should be specified before running the test; common target is 0.80.

---

**Q: How does Bayes' theorem apply to spam filtering?**

Naive Bayes classifiers implement Bayes' theorem directly. Given a new email, the classifier computes: P(spam | word₁, word₂, ...) ∝ P(spam) × P(word₁|spam) × P(word₂|spam) × ... The prior P(spam) captures overall spam frequency. The likelihoods P(word|spam) are estimated from labeled training data. The "naive" assumption is that words are conditionally independent given the class — which is false in reality but works well in practice because the error usually doesn't affect the ordering of class probabilities. This is why it's called naive. Bayes' theorem also shows why rare events need large priors to not be overwhelmed by likelihoods — a rare disease stays rare even with a positive test because the prior P(disease) is so low.

---

**Q: What is the difference between correlation and causation, and how do you establish causation?**

Correlation measures linear association between two variables — whether they tend to move together. Causation means one variable directly influences another. Correlation does not imply causation because: (1) the relationship may be reversed (B causes A); (2) a third variable C may cause both; (3) it may be spurious coincidence. Classic example: ice cream sales and drowning deaths are correlated — both increase in summer. The confounder is hot weather. To establish causation, you need: randomized controlled experiments (A/B tests are the gold standard); or quasi-experimental methods like instrumental variables, regression discontinuity, or difference-in-differences when randomization isn't possible. Observational ML models find correlations — deploying them as if they're causal is a common mistake that leads to failed interventions.

---

## Advanced

**Q: What is p-hacking and how do you prevent it in A/B testing?**

P-hacking (data dredging) is when analysts run multiple tests, look at multiple metrics, or keep checking significance during an ongoing test until they find p < 0.05. Because we accept a 5% false positive rate per test, running 20 tests gives an expected 1 spurious significant result even with no real effects. Prevention: (1) pre-register your hypothesis and primary metric before running the test; (2) use sequential testing methods like SPRT (Sequential Probability Ratio Test) if you must check early — these control the false positive rate across repeated checks; (3) apply Bonferroni correction or Benjamini-Hochberg FDR control for multiple simultaneous metrics; (4) report all metrics tested, not just significant ones. Industry standard: define one primary metric and a handful of guardrail metrics before the experiment, not after seeing the data.

---

**Q: What is the common misconception about p-values, and how should you interpret them correctly?**

The most common misconception: "p = 0.03 means there is a 3% probability that the null hypothesis is true." This is wrong. The p-value is P(data this extreme | H₀ is true) — a conditional probability about the data, not about the hypothesis. It says nothing directly about whether H₀ is true. Three things p-value does NOT tell you: (1) the probability your result is real; (2) the probability H₀ is true; (3) whether the effect is practically important. For that last point, always report effect size (Cohen's d, relative lift) alongside p-value. A p = 0.001 with Cohen's d = 0.02 is statistically significant but practically meaningless. Conversely, a p = 0.08 with d = 0.8 might be worth acting on despite missing the threshold.

---

**Q: What is the trade-off between Type I and Type II errors, and how does it affect real ML systems?**

Type I error (false positive, α) is rejecting H₀ when it's true — your system triggers an alert or makes a decision when it shouldn't. Type II error (false negative, β) is failing to reject H₀ when it's false — your system misses a real signal. They trade off: a more sensitive threshold catches more real effects (fewer Type II) but also triggers more false alarms (more Type I). In ML classification, this trade-off is controlled by the decision threshold. Lowering the threshold (from 0.5 to 0.3 for spam detection) catches more spam (fewer false negatives) but also blocks more legitimate mail (more false positives). Statistical power (1 - β) quantifies how well a test avoids Type II errors — standard target is 80%. Power increases with sample size, effect size, and significance level α.

---

**Q: What is Bayes' theorem and how does it apply to ML?**

Bayes' theorem: P(A|B) = P(B|A) × P(A) / P(B). In words: posterior = likelihood × prior / evidence. Given new evidence B, it tells you how to update your prior belief P(A) into a posterior P(A|B). In ML: Naive Bayes classifiers implement this directly — each word in an email updates P(spam). The "naive" assumption is conditional independence of features given class, which is rarely true but works well in practice. More broadly, Bayesian thinking underlies: regularization (priors on weights), hyperparameter tuning (Bayesian optimization), anomaly detection (prior on normal behavior), and uncertainty quantification. The key practical insight: the prior P(A) matters enormously when A is rare. Even a 99% accurate test gives only ~50% posterior probability for a 1% prevalence disease — low base rates dominate.

---

**Q: When should you use Pearson vs Spearman correlation?**

Pearson correlation measures the strength of a LINEAR relationship between two continuous variables. It's sensitive to outliers and assumes roughly normal data. Spearman correlation is rank-based — it measures the strength of a MONOTONIC relationship (whether they increase/decrease together, regardless of linearity). Use Spearman when: data is ordinal (rankings, satisfaction scores); distribution is non-normal; there are outliers that would distort Pearson; or the relationship is monotonic but not linear (e.g., exponential growth). Rule of thumb: if a scatterplot shows a curved (but consistently increasing or decreasing) relationship, Spearman will capture it but Pearson will underestimate it. For truly linear data with no outliers, both give similar results.

---

## Practice Problems

1. Given a list of salaries, compute mean, median, and identify which better describes the "typical" salary — then justify your answer.
2. Run a t-test to determine if two A/B groups have significantly different conversion rates.
3. Calculate the required sample size for an A/B test with 5% baseline conversion, 1% minimum detectable effect, 80% power, 5% significance.
4. Implement Bayes' theorem to compute P(disease|positive test) given prior, sensitivity, and specificity.

---

## 🔁 Navigation

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
