# 🎯 Random Numbers and Sampling — Controlled Chaos for ML

> A random number generator without a seed is like a recipe without measurements — you can't reproduce the dish.

---

## Why Reproducibility Matters in ML

Machine learning experiments have a dirty secret: most of them are not reproducible by default. You train a model, get great results, share the code — and your colleague gets different numbers. The culprit is almost always **random state**.

NumPy's `np.random` module gives you controlled chaos. You can generate noise, shuffle datasets, sample mini-batches, and initialize weights — and get the exact same sequence every time, as long as you control the seed.

---

## Seeding — The Reproducibility Switch

A **pseudo-random number generator** is like a slot machine with a starting position — if you set the same starting position every time, you always get the same sequence of results. The **seed** is that starting position. Without it, the machine starts at a different position each run, and your results change unpredictably.

A **seed** is the starting value for the pseudorandom number generator (PRNG). Same seed → same sequence of numbers, every time, on any machine.

```python
import numpy as np

# Old-style global seed (works but not recommended for new code)
np.random.seed(42)
print(np.random.rand(3))  # [0.374 0.951 0.732] — same every run

# New-style: Generator object (recommended — isolated, no global state)
rng = np.random.default_rng(seed=42)  # ← create a Generator instance
print(rng.random(3))                  # [0.773 0.438 0.858]
```

The `np.random.default_rng()` approach is preferred because each `rng` object has **isolated state** — multiple generators in the same program don't interfere with each other.

```python
rng_train = np.random.default_rng(seed=0)   # ← for training data shuffles
rng_model = np.random.default_rng(seed=99)  # ← for weight initialization
# These are completely independent — rng_train never affects rng_model
```

---

## Generating Random Numbers

Think of these functions as different dice: a fair die gives uniform results, a weighted die gives a normal distribution, a biased coin gives Bernoulli outcomes.

```python
rng = np.random.default_rng(42)

# Uniform — every value equally likely between 0 and 1
uniform = rng.random((3, 4))        # shape (3, 4), values in [0.0, 1.0)

# Uniform over a range
scores = rng.uniform(low=0.5, high=1.0, size=(100,))  # cosine sim range

# Standard normal — mean=0, std=1 (Gaussian bell curve)
z = rng.standard_normal((5, 5))

# Normal with custom mean and std — useful for weight init
weights = rng.normal(loc=0.0, scale=0.01, size=(128, 64))  # small init values

# Integers — for indices, labels, random choices
labels = rng.integers(low=0, high=10, size=(50,))  # 50 random class labels

# Bernoulli approximation via binomial(n=1)
dropout_mask = rng.binomial(n=1, p=0.8, size=(100,))  # 80% keep rate
```

---

## Probability Distributions for ML

**Distributions** model real-world data shapes. Choosing the right one matters for noise injection, augmentation, and Bayesian approaches.

```python
rng = np.random.default_rng(0)

# Beta — values in [0, 1], used in MixUp augmentation
alpha = rng.beta(a=0.4, b=0.4, size=(32,))  # ← MixUp lambda values

# Dirichlet — probabilities that sum to 1, used in topic models
topic_probs = rng.dirichlet(alpha=[1, 1, 1, 1], size=5)  # 5 docs, 4 topics
print(topic_probs.sum(axis=1))  # [1. 1. 1. 1. 1.] — always sums to 1

# Exponential — wait times, decay rates
wait_times = rng.exponential(scale=2.0, size=(1000,))  # mean = 2.0

# Poisson — count data (events per interval)
token_counts = rng.poisson(lam=15, size=(100,))  # avg 15 tokens per sentence

# Multinomial — draw from a distribution (like softmax sampling)
probs = np.array([0.1, 0.3, 0.4, 0.2])        # ← must sum to 1
sample = rng.multinomial(n=1, pvals=probs)     # one-hot style draw
samples = rng.multinomial(n=10, pvals=probs)   # 10 draws
```

---

## Shuffling and Permutations

**Shuffling** is how you randomize dataset order for stochastic gradient descent. Getting this wrong (shuffling X and y independently) is a classic, painful bug.

```python
rng = np.random.default_rng(7)

X = np.arange(20).reshape(10, 2)  # 10 samples, 2 features
y = np.arange(10)                  # 10 labels

# WRONG — shuffles X and y independently, breaks pairing
rng.shuffle(X)
rng.shuffle(y)  # ← now X[0] no longer matches y[0]

# CORRECT — shuffle indices, apply to both
idx = rng.permutation(len(y))  # ← returns shuffled index array
X_shuffled = X[idx]
y_shuffled = y[idx]             # ← same shuffle applied to both

# Alternative: permute a copy without modifying original
X_perm = rng.permutation(X)    # works on 1D; for 2D, shuffles rows
```

---

## Sampling With and Without Replacement

Think of **with replacement** as drawing from a deck and putting the card back — the same card can be drawn again. **Without replacement** means each card is drawn once.

```python
rng = np.random.default_rng(5)

population = np.array([10, 20, 30, 40, 50, 60, 70, 80])

# Without replacement — each element appears at most once
sample_no_replace = rng.choice(population, size=4, replace=False)
# e.g. [50, 10, 70, 30]

# With replacement — same element can appear multiple times
sample_with_replace = rng.choice(population, size=10, replace=True)
# e.g. [30, 30, 80, 10, 30, ...] — repeats allowed

# Weighted sampling — favor certain elements
weights = np.array([0.5, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05])
biased_sample = rng.choice(population, size=5, replace=True, p=weights)
# ← 10 and 20 will appear far more often
```

**Bootstrap sampling** — a core technique in ensemble methods — is just `replace=True`:

```python
data = np.random.default_rng(1).normal(0, 1, size=1000)

# Bootstrap: draw N samples with replacement, compute statistic
bootstrap_means = [
    rng.choice(data, size=len(data), replace=True).mean()
    for _ in range(1000)
]
ci_lower = np.percentile(bootstrap_means, 2.5)   # ← 95% CI lower bound
ci_upper = np.percentile(bootstrap_means, 97.5)  # ← 95% CI upper bound
print(f"95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")
```

---

## Mini-Batch Sampling

The workhorse of deep learning training is the **mini-batch** — a randomly sampled subset of training data used for one gradient update step.

```python
rng = np.random.default_rng(42)

N = 1000     # dataset size
batch_size = 32

# One epoch = one full pass through the data in shuffled mini-batches
indices = rng.permutation(N)   # ← shuffle all indices once per epoch

for start in range(0, N, batch_size):
    batch_idx = indices[start : start + batch_size]  # ← slice the shuffled indices
    X_batch = X[batch_idx]   # ← select batch rows
    y_batch = y[batch_idx]
    # ... gradient update here
```

---

## Practical: Weight Initialization Schemes

Good weight initialization prevents vanishing/exploding gradients. Each scheme has a different distribution.

```python
rng = np.random.default_rng(0)

fan_in  = 512   # neurons in previous layer
fan_out = 256   # neurons in this layer

# Xavier / Glorot — for tanh/sigmoid activations
limit = np.sqrt(6.0 / (fan_in + fan_out))
xavier_weights = rng.uniform(-limit, limit, size=(fan_in, fan_out))

# He / Kaiming — for ReLU activations
std = np.sqrt(2.0 / fan_in)
he_weights = rng.normal(0, std, size=(fan_in, fan_out))

# LeCun — for SELU activations
lecun_std = np.sqrt(1.0 / fan_in)
lecun_weights = rng.normal(0, lecun_std, size=(fan_in, fan_out))
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
| Linear Algebra (Advanced) | [06_linear_algebra_advanced.md](./06_linear_algebra_advanced.md) |
| Einsum and Performance | [07_einsum_and_performance.md](./07_einsum_and_performance.md) |
| Statistics and Distributions | [05_statistics_and_distributions.md](./05_statistics_and_distributions.md) |
| I/O and Memory | [08_io_and_memory.md](./08_io_and_memory.md) |
