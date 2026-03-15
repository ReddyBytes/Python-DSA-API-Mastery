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
