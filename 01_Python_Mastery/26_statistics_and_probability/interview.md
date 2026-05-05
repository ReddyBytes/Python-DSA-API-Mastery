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
| 💻 Practice | [practice.py](./practice.py) |
| ⬅️ Prev Module | [../25_python_ai_ecosystem/theory.md](../25_python_ai_ecosystem/theory.md) |
| ➡️ Next Module | [../27_matplotlib_seaborn/theory.md](../27_matplotlib_seaborn/theory.md) |

---

**[🏠 Back to README](../README.md)**
