# 🎯 Conditional Operations — np.where, np.select, np.clip

A bouncer at a club checks each person at the door: "Are you over 21? Yes — in. No — out." That check runs on one person at a time. NumPy's conditional operations do the exact same check but on millions of values simultaneously, in a single vectorized pass through memory, with no Python loop overhead.

The payoff is massive: code that would take seconds in a Python loop runs in milliseconds across a 10-million-element array.

---

## 🔀 Section 1: np.where — vectorized if/else

`np.where(condition, value_if_true, value_if_false)` is a vectorized ternary expression. For every element, it evaluates the condition and selects from one of two values. The condition, true-branch, and false-branch can all be arrays — they are broadcast together.

```python
import numpy as np

ages = np.array([15, 25, 17, 30, 12])
labels = np.where(ages >= 18, 'adult', 'minor')   # ← condition, true value, false value
# → ['minor', 'adult', 'minor', 'adult', 'minor']

# Binary classification: threshold logits to 0/1 predictions
logits = np.array([0.2, 0.8, 0.5, 0.9, 0.3])
predictions = np.where(logits >= 0.5, 1, 0)       # ← 1 if >= 0.5, else 0
# → [0, 1, 1, 1, 0]

# ReLU activation — zero out all negative values:
x = np.array([-2.0, 1.5, -0.3, 4.0])
relu = np.where(x > 0, x, 0)   # ← keep positive values, zero out negatives
# Equivalent to np.maximum(x, 0) — see Section 5 for which to prefer
```

Both the true and false branches are evaluated before the condition is applied — they are regular array expressions, not lazy. This means `np.where(denom != 0, num / denom, 0)` will still compute `num / denom` for all elements including where `denom == 0`. The safe pattern for division is covered in Section 7.

---

## 🔎 Section 2: np.where with single argument — find indices

When called with only a condition (no true/false values), `np.where` switches roles entirely: it returns the **indices** where the condition is True. Think of it as a filter that hands you the position numbers rather than the values.

```python
arr = np.array([1, -2, 3, -4, 5])
neg_indices = np.where(arr < 0)    # ← returns a tuple of index arrays
# (array([1, 3]),)                 ← one array per dimension; 2D arrays give two arrays

arr[neg_indices]                   # array([-2, -4]) ← use indices to extract values

# Practical: find positions of statistical outliers
data = np.array([1.0, 2.0, 15.0, 2.5, 1.8, 20.0])
mean, std = data.mean(), data.std()
outlier_positions = np.where(np.abs(data - mean) > 2 * std)
# ← returns indices where values are more than 2 standard deviations from mean

data[outlier_positions]            # ← extract the actual outlier values
```

The single-argument form returns a tuple because for N-dimensional arrays it returns N index arrays — one per axis — which can be zipped together to get coordinate pairs.

---

## 🎛️ Section 3: np.select — multi-condition branching

`np.where` handles a single binary condition. When you need more than two outcomes, `np.select` extends the pattern to an ordered list of conditions, each paired with a corresponding output value. The first matching condition wins — just like an if/elif/elif/else chain.

```python
scores = np.array([45, 72, 88, 55, 93, 60])

conditions = [
    scores >= 90,   # ← checked first; if True, result is 'A'
    scores >= 70,   # ← checked second
    scores >= 50,   # ← checked third
]
grades = ['A', 'B', 'C']   # ← paired one-to-one with conditions

result = np.select(conditions, grades, default='F')
# → ['F', 'B', 'B', 'C', 'A', 'C']
# Note: 72 matches both scores >= 70 AND scores >= 50 — first match (B) wins
```

The `default` value applies to any element where none of the conditions matched — equivalent to the final `else` in an if/elif chain.

Multi-class label assignment from probability arrays follows the same pattern:

```python
# Assign class label based on which probability bucket a score falls in
probs = np.array([0.05, 0.45, 0.72, 0.91, 0.38])
conditions = [probs >= 0.8, probs >= 0.5, probs >= 0.3]
labels     = ['high_conf', 'medium_conf', 'low_conf']
result = np.select(conditions, labels, default='very_low')
```

---

## 📏 Section 4: np.clip — bound values to a range

`np.clip(arr, min, max)` enforces a floor and a ceiling on every element. Values below the minimum are raised to the minimum; values above the maximum are lowered to the maximum; values in range are unchanged. Think of it as a hardware limiter that prevents a signal from going outside safe operating bounds.

```python
logits = np.array([-2.0, 0.5, 3.8, -0.1, 1.2])
clipped = np.clip(logits, -1.0, 1.0)   # ← no element outside [-1.0, 1.0]
# → [-1.0, 0.5, 1.0, -0.1, 1.0]

# Critical ML use case 1: prevent log(0) in cross-entropy loss
# log(0) = -inf, which produces NaN gradients and breaks training
probs = np.array([0.0, 0.3, 1.0, 0.7])
probs = np.clip(probs, 1e-7, 1 - 1e-7)   # ← keep values away from 0 and 1
loss = -np.log(probs)                      # ← safe: no zeros, no infinities

# Critical ML use case 2: gradient clipping in training
# Prevents exploding gradients from destabilising weight updates
gradients = np.array([-5.0, 0.2, 8.3, -1.1, 0.7])
gradients = np.clip(gradients, -1.0, 1.0)   # ← cap gradient magnitude at 1.0
# → [-1.0, 0.2, 1.0, -1.0, 0.7]
```

`np.clip` is the standard tool whenever you need to enforce valid ranges — pixel values in [0, 255], probabilities in (0, 1), or normalized scores in [-1, 1].

---

## ⚡ Section 5: np.maximum and np.minimum — element-wise with array

It is easy to confuse `np.maximum` with `np.max`. They are completely different operations.

- `np.max(a)` — **reduction**: collapses an array to its single maximum value
- `np.maximum(a, b)` — **element-wise**: compares two arrays and returns the larger element at each position

Think of `np.maximum` as running the bouncer check between two arrays simultaneously, picking the winner at each slot.

```python
a = np.array([1, 5, 3, 8])
b = np.array([4, 2, 6, 7])

np.maximum(a, b)   # [4, 5, 6, 8] ← element-wise: max of a[i] and b[i] at each i
np.minimum(a, b)   # [1, 2, 3, 7]

np.max(a)          # 8           ← single scalar, entire array
np.min(a)          # 1

# ReLU activation — the canonical use of np.maximum:
x = np.array([-2.0, 1.5, -0.3, 4.0])
relu = np.maximum(x, 0)   # ← cleaner and marginally faster than np.where(x > 0, x, 0)
# → [0.0, 1.5, 0.0, 4.0]

# Leaky ReLU:
alpha = 0.01
leaky_relu = np.maximum(alpha * x, x)   # ← alpha*x for negatives, x for positives
```

`np.maximum(x, 0)` is the preferred ReLU implementation in NumPy — it is self-documenting and avoids redundant condition evaluation.

---

## 🧹 Section 6: np.nan_to_num — handle NaN and Inf

**NaN** (Not a Number) and **Inf** (Infinity) are the numerical equivalent of corrupted data records — they propagate through every downstream computation and silently poison results. `np.nan_to_num` replaces them with finite values before they can spread.

```python
arr = np.array([1.0, np.nan, np.inf, -np.inf, 2.0])
clean = np.nan_to_num(arr, nan=0.0, posinf=1e6, neginf=-1e6)
# → [1.0, 0.0, 1000000.0, -1000000.0, 2.0]

# Diagnostic checks — run these before training or after data loading:
np.isnan(arr).any()     # True  — at least one NaN present
np.isinf(arr).any()     # True  — at least one Inf present
np.isfinite(arr).all()  # False — not all values are finite numbers

# Find exactly where the bad values are:
np.where(np.isnan(arr))    # (array([1]),) ← index 1 is NaN
np.where(~np.isfinite(arr)) # (array([1, 2, 3]),) ← indices of all non-finite values
```

In ML pipelines, NaN values commonly arise from: dividing by zero, `log(0)`, `0/0` in softmax on all-zero inputs, or corrupted input data. Running `np.isnan(X).any()` and `np.isinf(X).any()` at the start of training is a low-cost sanity check that catches data pipeline bugs early.

---

## 🎭 Section 7: Vectorized masking patterns

**Masking** is the technique of using a boolean array to selectively modify or zero out values. It is foundational in attention mechanisms, loss computation, and any pipeline that processes variable-length sequences.

```python
# Causal attention masking — block future positions in self-attention:
attention_scores = np.random.randn(4, 8)          # ← (heads, seq_len)
future_mask = np.triu(np.ones((8, 8), dtype=bool), k=1)  # ← upper triangle = future
attention_scores[:, future_mask] = float('-inf')   # ← -inf → 0 after softmax

# Zero out values below threshold (soft masking):
scores = np.random.randn(100)
mask = scores < 0                  # ← boolean mask
scores[mask] = 0.0                 # ← in-place zero-out via boolean indexing

# Safe divide — avoid division by zero without Python loops:
numerator   = np.array([1.0, 2.0, 3.0, 4.0])
denominator = np.array([0.0, 2.0, 0.0, 4.0])

# The trick: use np.where twice — once for the condition, once to make division safe
safe_denom = np.where(denominator != 0, denominator, 1)   # ← replace 0s with 1 temporarily
result     = np.where(denominator != 0, numerator / safe_denom, 0.0)
# → [0.0, 1.0, 0.0, 1.0] ← division-by-zero positions return 0, not inf/NaN

# Masked mean (ignore padding tokens in loss):
token_losses = np.array([0.5, 0.8, 0.3, 0.0, 0.0])   # ← last 2 are padding
valid_mask   = np.array([True, True, True, False, False])
mean_loss    = token_losses[valid_mask].mean()         # ← only average real tokens
```

The double `np.where` safe-divide pattern avoids a true division-by-zero (which would produce Inf or NaN) while keeping the computation fully vectorized — no Python loop, no try/except.

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⬅️ Prev Topic | [03_random_and_sampling.md](./03_random_and_sampling.md) |
| ➡️ Next Topic | [05_statistics_and_distributions.md](./05_statistics_and_distributions.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🎤 Interview | [interview.md](./interview.md) |
