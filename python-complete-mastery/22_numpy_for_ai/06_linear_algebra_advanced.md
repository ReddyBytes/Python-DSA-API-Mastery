# 🎯 Linear Algebra (Advanced) — The Math Behind the Model

> Least squares, QR, and matrix rank are not abstract theorems — they are the exact computations your ML framework runs when it fits a line, solves a system, or checks if your features are redundant.

---

## Least Squares Regression — Fitting Without Inverting

You have 1,000 houses with price, size, and location data. You want the best-fit weights without manually inverting matrices — which is numerically unstable and fails silently when features are correlated. `lstsq` does it in one call, safely, using SVD under the hood.

The classic linear regression problem: given a matrix of features `X` (shape `(n, p)`) and a target vector `y` (shape `(n,)`), find weights `w` such that `Xw ≈ y`.

The **normal equations** give the exact solution: `w = (XᵀX)⁻¹ Xᵀy`. But directly inverting `XᵀX` is numerically unstable. NumPy's `np.linalg.lstsq` solves this safely using **singular value decomposition (SVD)** under the hood.

```python
import numpy as np

# Synthetic dataset: 100 samples, 3 features
rng = np.random.default_rng(42)
X_raw = rng.normal(0, 1, size=(100, 3))
true_w = np.array([2.0, -1.5, 0.8])
noise  = rng.normal(0, 0.1, size=100)
y      = X_raw @ true_w + noise

# Add bias column (intercept)
X = np.column_stack([np.ones(100), X_raw])  # ← prepend a column of 1s

# Solve: minimizes ||Xw - y||² (least-squares residuals)
w, residuals, rank, sv = np.linalg.lstsq(X, y, rcond=None)
# w         ← solved weights [bias, w0, w1, w2]
# residuals ← sum of squared residuals (if rank == n_cols)
# rank      ← numerical rank of X
# sv        ← singular values of X

print(f"Recovered weights: {w[1:]}")   # should be close to [2.0, -1.5, 0.8]
print(f"Bias term:         {w[0]:.4f}")
print(f"Matrix rank:       {rank}")
```

**Residuals** are the squared differences between predictions and actuals — the quantity least squares minimizes. A lower residual means a better fit.

---

## QR Decomposition — Orthogonal Foundations

Gaussian elimination on a whiteboard is straightforward. But on a computer, floating-point rounding compounds across thousands of steps — small errors grow until your solution is meaningless. QR decomposition is how numerical software actually solves linear systems stably.

**QR decomposition** factors a matrix `A` into `Q` (orthogonal — columns are unit vectors at right angles) and `R` (upper triangular). It is numerically more stable than using the normal equations directly.

The analogy: QR is like finding the natural coordinate system that your data lives in, then expressing the regression in that system.

```python
A = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9],
              [10, 11, 13]], dtype=float)  # ← last element breaks perfect singularity

Q, R = np.linalg.qr(A)
# Q shape: (4, 3) — orthonormal columns (Q.T @ Q = I)
# R shape: (3, 3) — upper triangular

print(np.allclose(Q.T @ Q, np.eye(3)))   # True — columns are orthonormal
print(np.allclose(Q @ R, A))             # True — reconstruction is exact

# QR-based least squares (more stable than lstsq for well-conditioned systems)
# Solve: Rw = Qᵀy
b = np.array([1.0, 2.0, 3.0, 4.0])
Qt_b = Q.T @ b
w_qr = np.linalg.solve(R, Qt_b)          # ← back substitution (fast for triangular R)
```

**Use cases for QR in ML:**
- Gram-Schmidt orthogonalization of feature vectors
- Solving linear systems in optimization algorithms
- Computing orthonormal bases for subspace methods (PCA via QR iteration)

---

## Condition Number — How Trustworthy Is Your Solution?

Two matrices can look similar but behave very differently under small perturbations. A condition number of 1 means rock-solid — noise in your input barely affects the output. A condition number of 10^12 means your solution will be garbage if there's any noise in your data.

The **condition number** of a matrix tells you how sensitive the solution `w` is to small changes in the data `y`. A high condition number means small noise in `y` causes large swings in `w` — the system is **ill-conditioned**.

Think of it as the amplification factor for errors: a condition number of 1000 means a 0.1% perturbation in input could cause up to 100% error in output.

```python
# Well-conditioned matrix
A_good = np.array([[3.0, 1.0],
                   [1.0, 4.0]])
print(f"Condition number (good): {np.linalg.cond(A_good):.2f}")  # ← small, near 1

# Ill-conditioned matrix (nearly singular columns)
A_bad = np.array([[1.0, 1.0],
                  [1.0, 1.0001]])   # ← columns nearly identical
print(f"Condition number (bad):  {np.linalg.cond(A_bad):.2f}")   # ← huge number

# Practical threshold: cond > 1e6 means results may be unreliable
# np.linalg.lstsq handles this via SVD; direct np.linalg.solve does not
```

**ML relevance:** Highly correlated features produce ill-conditioned feature matrices. This is why **feature scaling** and **L2 regularization** (ridge regression) are essential — they reduce the condition number.

```python
# Ridge regression: adds λI to XᵀX, reducing condition number
lambda_reg = 0.01
XtX = X.T @ X
Xty = X.T @ y
w_ridge = np.linalg.solve(XtX + lambda_reg * np.eye(XtX.shape[0]), Xty)
# ← lambda_reg * I improves conditioning by making eigenvalues larger
```

---

## Determinant — Volume and Invertibility

The **determinant** of a square matrix measures the volume scaling factor of the linear transformation it represents. A determinant of zero means the matrix is **singular** — it collapses some dimension, and no inverse exists.

```python
A = np.array([[4.0, 7.0],
              [2.0, 6.0]])

det = np.linalg.det(A)
print(f"det(A) = {det:.4f}")   # 10.0 — non-zero, invertible

# Near-singular matrix
B = np.array([[1.0, 2.0],
              [2.0, 4.0]])     # ← row 2 = 2 * row 1
print(f"det(B) = {np.linalg.det(B):.6f}")  # ≈ 0.0 — singular

# Determinant from LU decomposition (more numerically stable for large matrices)
# np.linalg.det uses LAPACK routines internally — fine for moderate sizes
```

**ML use cases for the determinant:**
- Gaussian density: `p(x) ∝ 1/sqrt(det(Σ)) * exp(...)` — the covariance determinant normalizes the distribution
- Checking if a covariance matrix is positive definite (det > 0 is necessary but not sufficient)
- Log-determinant (`np.linalg.slogdet`) for numerical stability with very small/large determinants

```python
# Log-determinant — avoids overflow/underflow for large matrices
sign, logdet = np.linalg.slogdet(A)
# sign: +1 or -1 (sign of det)
# logdet: log(|det(A)|)
# Reconstruct: det = sign * exp(logdet)
```

---

## Matrix Rank — How Many Independent Directions?

You have 10 features but suspect some are linear combinations of others — redundant copies with different names. Rank tells you how many truly independent dimensions your data has. If rank is 6, you can drop 4 features without losing any information.

The **rank** of a matrix is the number of linearly independent rows (or columns) — the true dimensionality of the information it contains.

Imagine 1000 survey questions where 900 are just paraphrases of the other 100. The matrix has 1000 columns but rank ≈ 100. Most of the data is redundant.

```python
# Full rank matrix
A_full = np.array([[1, 0, 0],
                   [0, 1, 0],
                   [0, 0, 1]], dtype=float)
print(f"Rank (full): {np.linalg.matrix_rank(A_full)}")  # 3

# Rank-deficient matrix (row 3 = row 1 + row 2)
A_deficient = np.array([[1, 2, 3],
                        [4, 5, 6],
                        [5, 7, 9]], dtype=float)  # ← col 3 = col 1 + col 2
print(f"Rank (deficient): {np.linalg.matrix_rank(A_deficient)}")  # 2

# Numerical rank — uses SVD and a tolerance threshold
# Singular values below tol are treated as zero
rank = np.linalg.matrix_rank(A_deficient, tol=1e-10)
print(f"Numerical rank: {rank}")
```

**Rank in ML:**

```python
# Check effective rank of embedding matrix
embeddings = rng.normal(0, 1, size=(1000, 128))    # 1000 embeddings, 128 dims
rank = np.linalg.matrix_rank(embeddings)
print(f"Embedding rank: {rank}")  # likely 128 if embeddings are well-distributed

# SVD reveals the rank via non-zero singular values
U, s, Vt = np.linalg.svd(embeddings, full_matrices=False)
effective_rank = np.sum(s > 1e-10)   # ← count non-negligible singular values
print(f"Effective rank via SVD: {effective_rank}")

# Low-rank approximation: keep top-k singular values (lossy compression)
k = 32
embeddings_lowrank = U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]  # ← rank-32 approximation
compression_ratio = (k * (embeddings.shape[0] + embeddings.shape[1])) / embeddings.size
print(f"Compression ratio: {compression_ratio:.2f}x")
```

---

## SVD — The Swiss Army Knife

**Singular Value Decomposition** (`A = U Σ Vᵀ`) is the backbone of PCA, low-rank approximation, pseudo-inverse, and many recommendation systems.

```python
A = rng.normal(0, 1, size=(50, 10))

# Full SVD
U, s, Vt = np.linalg.svd(A, full_matrices=False)
# U:  (50, 10) — left singular vectors (output space basis)
# s:  (10,)    — singular values (importance weights, descending)
# Vt: (10, 10) — right singular vectors (input space basis)

# Reconstruction check
A_reconstructed = U @ np.diag(s) @ Vt
print(np.allclose(A, A_reconstructed))  # True

# Pseudo-inverse — solves underdetermined or overdetermined systems
A_pinv = np.linalg.pinv(A)             # ← uses SVD internally
print(A_pinv.shape)                     # (10, 50)

# PCA via SVD: center the data, then SVD gives principal components
A_centered = A - A.mean(axis=0)        # ← subtract column means
U, s, Vt = np.linalg.svd(A_centered, full_matrices=False)
# Vt rows are principal component directions
# s² / (n-1) are the explained variances

explained_var_ratio = (s**2) / (s**2).sum()
print(f"Top-3 components explain: {explained_var_ratio[:3].sum()*100:.1f}% of variance")
```

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
| Random and Sampling | [03_random_and_sampling.md](./03_random_and_sampling.md) |
| Einsum and Performance | [07_einsum_and_performance.md](./07_einsum_and_performance.md) |
| Statistics and Distributions | [05_statistics_and_distributions.md](./05_statistics_and_distributions.md) |
| I/O and Memory | [08_io_and_memory.md](./08_io_and_memory.md) |
