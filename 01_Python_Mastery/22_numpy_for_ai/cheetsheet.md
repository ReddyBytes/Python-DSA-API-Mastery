# ⚡ Cheatsheet: NumPy for AI

---

## Array Creation

```python
import numpy as np

np.array([1, 2, 3])                        # from list
np.array([1, 2, 3], dtype=np.float32)      # specify dtype
np.zeros((3, 4))                            # 3x4 matrix of 0.0
np.ones((2, 3))                             # 2x3 matrix of 1.0
np.eye(4)                                   # 4x4 identity matrix
np.arange(0, 10, 2)                         # [0 2 4 6 8]
np.linspace(0, 1, 5)                        # 5 evenly spaced from 0 to 1

rng = np.random.default_rng(seed=42)
rng.random((3, 3))                          # uniform [0, 1)
rng.standard_normal((3, 3))                 # N(0, 1) Gaussian
rng.integers(0, 10, size=(2, 5))            # random ints
```

---

## Array Properties

```python
arr.shape      # (rows, cols, ...) — tuple of dimensions
arr.ndim       # number of dimensions
arr.dtype      # data type (float32, int64, etc.)
arr.size       # total number of elements
arr.nbytes     # total bytes in memory
```

---

## Indexing and Slicing

```python
# 1D
v[0]           # first element
v[-1]          # last element
v[1:4]         # elements 1, 2, 3
v[::-1]        # reversed

# 2D
m[0, 1]        # row 0, col 1
m[0]           # entire row 0
m[:, 1]        # entire column 1
m[0:2, 1:3]   # submatrix

# Boolean indexing
v[v > 0.5]                     # elements where condition is True
v[(v > 0) & (v < 1)]           # combine conditions with &

# Fancy indexing
v[[0, 2, 4]]                   # elements at indices 0, 2, 4
```

---

## Math and Vectorized Ops

```python
a + b    # element-wise add
a - b    # element-wise subtract
a * b    # element-wise multiply
a / b    # element-wise divide
a ** 2   # element-wise power

np.sqrt(arr)
np.exp(arr)
np.log(arr)
np.abs(arr)
np.sin(arr)
np.cos(arr)
np.clip(arr, min_val, max_val)
```

---

## Matrix Operations

```python
A @ B                  # matrix multiply  (preferred)
np.matmul(A, B)        # same as A @ B
np.dot(a, b)           # dot product (vectors) or matmul (matrices)
A.T                    # transpose
np.linalg.inv(A)       # matrix inverse
np.linalg.norm(v)      # L2 norm of vector
np.linalg.norm(v, ord=1)  # L1 norm
np.linalg.solve(A, b)  # solve Ax = b
```

**Shape rule for matmul:** `(m, k) @ (k, n)` → `(m, n)`. Inner dimensions must match.

---

## Aggregations

```python
np.sum(arr)              # total sum
np.mean(arr)             # mean
np.min(arr)              # minimum
np.max(arr)              # maximum
np.std(arr)              # standard deviation
np.argmax(arr)           # index of maximum
np.argmin(arr)           # index of minimum
np.argsort(arr)          # indices that sort ascending

# axis parameter
np.sum(arr, axis=0)      # sum each column (collapse rows)
np.sum(arr, axis=1)      # sum each row (collapse columns)
np.mean(arr, axis=0)     # mean of each column
```

---

## Reshaping and Stacking

```python
arr.reshape((3, 4))         # new shape (total elements must match)
arr.reshape((3, -1))        # NumPy infers last dimension
arr.flatten()               # any shape → 1D copy
arr.ravel()                 # any shape → 1D view (faster)

np.expand_dims(v, axis=0)   # (n,) → (1, n)
np.squeeze(arr)             # remove dimensions of size 1

np.concatenate([a, b], axis=0)   # join along existing axis
np.vstack([a, b])                # stack vertically (axis=0)
np.hstack([a, b])                # stack horizontally (axis=1)
np.stack([a, b], axis=0)         # stack along new axis
```

---

## Broadcasting Rules

Two shapes are compatible (right to left):
- Dimensions are equal, OR
- One of them is 1

```python
(4, 3) + (3,)      # OK — (3,) broadcasts to (4, 3)
(4, 1) + (1, 3)    # OK — broadcasts to (4, 3)
(4, 3) + (4,)      # ERROR — (4,) doesn't align right
```

---

## Cosine Similarity — The AI Formula

```
cosine_similarity(a, b) = (a · b) / (||a|| * ||b||)
```

```python
# Single pair
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Query vs many docs (vectorized — no loop)
def cosine_search(query, docs, top_k=5):
    q = query / np.linalg.norm(query)
    d = docs / np.linalg.norm(docs, axis=1, keepdims=True)
    sims = d @ q                                    # shape (n_docs,)
    top_idx = np.argsort(sims)[-top_k:][::-1]
    return top_idx, sims[top_idx]
```

**Key insight:** normalize once, then use dot product instead of full cosine formula.

---

## Common dtypes in AI

```
float32    — standard for embeddings and model weights (4 bytes)
float64    — default NumPy float, higher precision (8 bytes)
int32      — token IDs, class labels (4 bytes)
int64      — default NumPy int (8 bytes)
bool       — masks, attention masks (1 byte)
```

Convert:
```python
arr.astype(np.float32)
```

---

## Memory Layout

```python
arr.flags['C_CONTIGUOUS']    # True = row-major (C order) — fast for row ops
arr.flags['F_CONTIGUOUS']    # True = column-major (Fortran order) — fast for col ops

np.ascontiguousarray(arr)    # force C order — speeds up many ops
```

---

## Quick Gotchas

```python
# Views vs copies
b = a[0:3]          # b is a VIEW — modifying b changes a
b = a[0:3].copy()   # b is a COPY — safe to modify independently

# Boolean indexing always returns a copy
b = a[a > 0]        # copy

# Shape confusion
v = np.array([1, 2, 3])
v.shape             # (3,)  — 1D, not a row or column
v.reshape(1, 3)     # (1, 3) — explicitly a row vector
v.reshape(3, 1)     # (3, 1) — explicitly a column vector
```

---

## Views vs Copies

```python
b = a[1:4]          # VIEW — shares memory with a
b = a[1:4].copy()   # COPY — independent allocation
b.base is a         # True  = b is a view of a
b.base is None      # True  = b owns its data (copy or original)

# Operations that return a VIEW:  slice, .T, compatible reshape, .ravel()
# Operations that return a COPY:  boolean index, fancy index, .astype(), .flatten()

# DANGER — in-place op mutates caller's array if passed a view:
arr /= arr.max()    # modifies original if arr is a view
# SAFE:
arr = arr / arr.max()
```

---

## Precision and Memory

```python
np.finfo(np.float16).max   # 65504 — max value before overflow
np.finfo(np.float32).eps   # ~1.2e-7 — smallest representable delta from 1.0
np.iinfo(np.int8).max      # 127

np.can_cast(np.float32, np.float16)   # False — range loss
np.can_cast(np.float32, np.float64)   # True  — safe upcast

# Memory cost per 1M embeddings of dim 768:
# float64 → 6.1 GB | float32 → 3.0 GB | float16 → 1.5 GB | int8 → 768 MB
```

---

## Random (New API)

```python
rng = np.random.default_rng(seed=42)   # reproducible generator
rng.random((3, 4))                      # uniform [0, 1)
rng.standard_normal((3, 4))             # N(0, 1)
rng.integers(0, 10, size=(2, 5))        # int in [0, 10)
rng.choice(arr, size=100, replace=False) # sampling without replacement
rng.shuffle(arr)                         # in-place shuffle

# Weight initialization patterns:
rng.standard_normal((fan_in, fan_out)) * np.sqrt(2 / fan_in)  # He init
rng.standard_normal((fan_in, fan_out)) * np.sqrt(1 / fan_in)  # Xavier init
```

---

## Conditional Operations

```python
# np.where — vectorized if/else
np.where(condition, val_if_true, val_if_false)
np.where(x > 0, x, 0)                   # ReLU
np.where(condition)                      # returns indices where True

# np.select — multi-condition (first match wins)
np.select([c >= 90, c >= 70, c >= 50], ['A', 'B', 'C'], default='F')

# np.clip — enforce min/max bounds
np.clip(arr, -1.0, 1.0)                 # cap values
np.clip(probs, 1e-7, 1 - 1e-7)         # prevent log(0) in cross-entropy
np.clip(grads, -1.0, 1.0)              # gradient clipping

# np.maximum / np.minimum — element-wise between two arrays
np.maximum(a, b)        # NOT the same as np.max(a)
np.maximum(x, 0)        # ReLU (preferred over np.where)

# NaN / Inf handling
np.isnan(arr).any()     # check for NaN
np.isinf(arr).any()     # check for Inf
np.nan_to_num(arr, nan=0.0, posinf=1e6, neginf=-1e6)
```

---

## Statistics and Distributions

```python
np.percentile(arr, 95)              # 95th percentile (P95)
np.percentile(arr, [25, 50, 75])    # quartiles Q1, Q2, Q3
np.quantile(arr, 0.95)              # same as percentile but 0-1 scale

q1, q3 = np.percentile(arr, [25, 75])
iqr = q3 - q1                       # interquartile range
outliers = arr[(arr < q1 - 1.5*iqr) | (arr > q3 + 1.5*iqr)]

counts, edges = np.histogram(arr, bins=50)       # frequency bins
np.corrcoef(arr1, arr2)[0, 1]                    # Pearson correlation
np.cov(arr1, arr2)                               # covariance matrix
```

---

## Linear Algebra (Advanced)

```python
# Least squares
coeffs, residuals, rank, sv = np.linalg.lstsq(A, b, rcond=None)

# Condition number — sensitivity to perturbations
cond = np.linalg.cond(A)   # > 1e10 = ill-conditioned (numerical instability)

# QR decomposition
Q, R = np.linalg.qr(A)     # A = Q @ R; Q orthogonal, R upper triangular

# SVD
U, s, Vt = np.linalg.svd(A, full_matrices=False)
rank = np.sum(s > 1e-10)   # effective rank
A_approx = U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]  # rank-k approximation

# Eigendecomposition (symmetric matrices only for real eigenvalues)
eigenvalues, eigenvectors = np.linalg.eigh(A)
```

---

## einsum

```python
# Dot product:         np.einsum('i,i->', a, b)
# Matrix multiply:     np.einsum('ij,jk->ik', A, B)
# Batch matmul:        np.einsum('bij,bjk->bik', A, B)
# Transpose:           np.einsum('ij->ji', A)
# Outer product:       np.einsum('i,j->ij', a, b)
# Trace:               np.einsum('ii->', A)

# Transformer attention (scaled dot-product):
scores = np.einsum('bhd,bhd->bh', Q, K) / np.sqrt(d_k)  # simplified
```

---

## I/O and Memory-Mapped Files

```python
# Save / load single array
np.save('arr.npy', arr)          # binary, preserves dtype
arr = np.load('arr.npy')

# Save / load multiple arrays
np.savez('data.npz', X=X, y=y)
data = np.load('data.npz')
X, y = data['X'], data['y']

np.savez_compressed('data.npz', X=X)  # smaller file, slower

# Text formats (CSV interop)
np.savetxt('arr.csv', arr, delimiter=',')
arr = np.loadtxt('arr.csv', delimiter=',')

# Memory-mapped — large arrays without loading into RAM
mmap = np.load('big.npy', mmap_mode='r')   # 'r'=read, 'r+'=read-write, 'w+'=new
row = mmap[0]   # only loads row 0 from disk
```

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Theory](./README.md) &nbsp;|&nbsp; **Next:** [Interview Q&A →](./interview.md)

**Related Topics:** [Theory](./README.md) · [Interview Q&A](./interview.md)
