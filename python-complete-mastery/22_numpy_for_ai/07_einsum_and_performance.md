# 🎯 Einsum and Performance — Express Any Tensor Operation in One Line

> `np.einsum` is the assembly language of tensor math: verbose to learn, but once fluent, you can write any contraction, product, or transpose without reaching for a reference.

---

## Why Einsum Exists

You're implementing a Transformer attention mechanism from scratch. You need: batch matrix multiply across heads, scaled dot products, and weighted value aggregation. You could write 6 separate NumPy calls, track intermediate arrays, and debug shape mismatches for an afternoon. Or you write one einsum string. That's the point.

NumPy has dozens of functions for dot products, outer products, traces, transposes, and contractions. `np.einsum` replaces all of them with a single, consistent notation borrowed from **Einstein summation convention** — the mathematical shorthand physicists use to describe tensor operations.

The rule: write the indices of input arrays and the indices you want in the output. Any index that appears in inputs but not in the output gets **summed over** (contracted). That's it.

---

## Reading Subscript Notation

Think of index letters as axis names: you declare what goes in, declare what you want out, and any letter that disappears in the output gets summed. The format is: `"input_indices -> output_indices"`. Each letter is an axis label.

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])          # shape (2, 2)
B = np.array([[5, 6], [7, 8]])          # shape (2, 2)

# Matrix multiply: sum over shared index k
# i,j = output axes; k = contracted axis (disappears)
C = np.einsum("ik,kj->ij", A, B)       # ← equivalent to A @ B
print(C)
# [[ 19  22]
#  [ 43  50]]

# Verify
print(np.allclose(C, A @ B))            # True
```

The string `"ik,kj->ij"` reads: "for each output position (i,j), sum over all k of A[i,k] * B[k,j]".

---

## Common Einsum Patterns

Roughly 90% of ML tensor operations reduce to one of these patterns — once you recognize them in einsum notation, you can read model code without decoding shape comments.

These patterns cover the vast majority of ML tensor operations:

```python
rng = np.random.default_rng(0)
A   = rng.normal(0, 1, (3, 4))
B   = rng.normal(0, 1, (4, 5))
v   = rng.normal(0, 1, (4,))
M   = rng.normal(0, 1, (3, 3))

# Dot product (1D vectors)
a = rng.normal(0, 1, (4,))
b = rng.normal(0, 1, (4,))
dot = np.einsum("i,i->", a, b)           # ← no output index = scalar sum
print(dot, np.dot(a, b))                 # same result

# Matrix-vector product
y = np.einsum("ij,j->i", A, v)          # ← A @ v, shape (3,)

# Outer product — no shared indices, no contraction
outer = np.einsum("i,j->ij", a, b)      # shape (4, 4)
print(outer.shape)

# Transpose
At = np.einsum("ij->ji", A)             # ← same as A.T

# Trace (sum of diagonal)
trace = np.einsum("ii->", M)            # ← sum over i where row==col
print(trace, np.trace(M))               # same

# Element-wise (Hadamard) product
C = rng.normal(0, 1, (3, 4))
hadamard = np.einsum("ij,ij->ij", A, C) # ← same as A * C

# Row-wise dot products (batch inner product)
X = rng.normal(0, 1, (10, 8))   # 10 vectors of dim 8
Y = rng.normal(0, 1, (10, 8))   # 10 vectors of dim 8
row_dots = np.einsum("ij,ij->i", X, Y)  # ← shape (10,), one dot per row
```

---

## Batch Matrix Multiply — The Attention Core

Every Transformer processes sequences in parallel across multiple attention heads. Without batch matrix multiply, you'd need a Python loop over heads — orders of magnitude slower. **Batch matrix multiply** is the single most important einsum in modern deep learning.

```python
# Batch matrix multiply: multiply N pairs of matrices
batch_size = 32
m, k, n = 64, 128, 64   # matrix dimensions

A_batch = rng.normal(0, 1, (batch_size, m, k))  # 32 matrices of shape (64, 128)
B_batch = rng.normal(0, 1, (batch_size, k, n))  # 32 matrices of shape (128, 64)

# Einsum: b=batch index (preserved), m,n=output axes, k=contracted
C_batch = np.einsum("bmk,bkn->bmn", A_batch, B_batch)  # shape (32, 64, 64)

# Equivalent (but often slower for large k):
C_np = np.matmul(A_batch, B_batch)              # np.matmul supports batch dims
print(np.allclose(C_batch, C_np))               # True
```

**Scaled dot-product attention** — the core of every Transformer:

```python
def scaled_dot_product_attention(Q, K, V):
    """
    Q, K, V: shape (batch, heads, seq_len, head_dim)
    Returns: attended values of same shape as V
    """
    batch, heads, seq_len, d_k = Q.shape

    # Step 1: attention scores — batch matmul of Q and K transposed
    # "bhqd,bhkd->bhqk": for each (batch,head), dot each query q with each key k
    scores = np.einsum("bhqd,bhkd->bhqk", Q, K)   # shape (batch, heads, seq, seq)
    scores = scores / np.sqrt(d_k)                  # ← scale to prevent softmax saturation

    # Step 2: softmax over key dimension
    scores_exp = np.exp(scores - scores.max(axis=-1, keepdims=True))  # ← stable softmax
    attn_weights = scores_exp / scores_exp.sum(axis=-1, keepdims=True)

    # Step 3: weighted sum of values
    # "bhqk,bhkd->bhqd": weighted combination of value vectors
    output = np.einsum("bhqk,bhkd->bhqd", attn_weights, V)
    return output, attn_weights

# Demo
B, H, S, D = 2, 4, 16, 32    # batch=2, heads=4, seq_len=16, head_dim=32
Q = rng.normal(0, 1, (B, H, S, D))
K = rng.normal(0, 1, (B, H, S, D))
V = rng.normal(0, 1, (B, H, S, D))

output, weights = scaled_dot_product_attention(Q, K, V)
print(f"Output shape:  {output.shape}")   # (2, 4, 16, 32)
print(f"Weights shape: {weights.shape}")  # (2, 4, 16, 16) — seq x seq attention matrix
```

---

## Multi-Head Attention Projection — Einsum Style

```python
# Project input x through W_q, W_k, W_v weight matrices for all heads at once
seq_len = 16
model_dim = 128
n_heads = 4
head_dim = model_dim // n_heads   # 32

x = rng.normal(0, 1, (seq_len, model_dim))         # input sequence
W_q = rng.normal(0, 0.02, (model_dim, n_heads, head_dim))  # query projection

# Project: for each position s, for each head h, compute a head_dim vector
# "sd,dhk->shk": s=seq, d=model_dim (contracted), h=heads, k=head_dim
Q = np.einsum("sd,dhk->shk", x, W_q)  # shape (seq_len, n_heads, head_dim)
```

---

## Performance Tips

### 1. Optimize subscript order

`np.einsum` tries to find an efficient contraction order automatically when you set `optimize=True`:

```python
A = rng.normal(0, 1, (100, 200))
B = rng.normal(0, 1, (200, 300))
C = rng.normal(0, 1, (300, 50))

# Without optimization — may contract in left-to-right order
result_slow = np.einsum("ij,jk,kl->il", A, B, C)

# With optimization — finds optimal contraction path
result_fast = np.einsum("ij,jk,kl->il", A, B, C, optimize=True)

print(np.allclose(result_slow, result_fast))  # True — same result, faster path
```

### 2. Use `np.matmul` / `@` for simple 2D matrix multiply

For the common case of `(m,k) @ (k,n) -> (m,n)`, `@` uses BLAS routines that are faster than einsum:

```python
import time

A = rng.normal(0, 1, (1000, 1000))
B = rng.normal(0, 1, (1000, 1000))

t0 = time.perf_counter()
_ = np.einsum("ij,jk->ik", A, B)
t_ein = time.perf_counter() - t0

t0 = time.perf_counter()
_ = A @ B
t_matmul = time.perf_counter() - t0

print(f"einsum: {t_ein*1000:.1f}ms")
print(f"matmul: {t_matmul*1000:.1f}ms")
# matmul is typically 2-5x faster for simple 2D matmul
```

### 3. Avoid repeated einsum in hot loops — precompute paths

```python
# If you call the same einsum pattern thousands of times in a loop,
# precompute the contraction path once
A_batch = rng.normal(0, 1, (32, 64, 128))
B_batch = rng.normal(0, 1, (32, 128, 64))

# Compute optimal path once
path = np.einsum_path("bmk,bkn->bmn", A_batch, B_batch, optimize="optimal")[0]

# Reuse the path for each call
for _ in range(100):
    result = np.einsum("bmk,bkn->bmn", A_batch, B_batch, optimize=path)
```

### 4. Memory layout matters — prefer C-contiguous arrays

```python
# F-contiguous (Fortran order) can slow down einsum
A_f = np.asfortranarray(rng.normal(0, 1, (500, 500)))  # column-major
A_c = np.ascontiguousarray(A_f)                         # row-major (C order)

# A_c will typically be faster in einsum/matmul — cache-friendly row access
print(A_c.flags["C_CONTIGUOUS"])   # True
```

---

## Quick Reference Table

| Operation | Einsum | Equivalent |
|---|---|---|
| Matrix multiply | `"ij,jk->ik"` | `A @ B` |
| Batch matmul | `"bij,bjk->bik"` | `np.matmul(A,B)` |
| Dot product | `"i,i->"` | `np.dot(a,b)` |
| Outer product | `"i,j->ij"` | `np.outer(a,b)` |
| Transpose | `"ij->ji"` | `A.T` |
| Trace | `"ii->"` | `np.trace(A)` |
| Row norms squared | `"ij,ij->i"` | `(A**2).sum(1)` |
| Element-wise mul | `"ij,ij->ij"` | `A * B` |

---

## 🔁 Navigation

| | |
|---|---|
| 📖 Main Theory | [theory.md](./README.md) |
| ⚡ Cheatsheet | [cheatsheet.md](./cheatsheet.md) |
| 🏠 Module Home | [theory.md](./README.md) |
| Random and Sampling | [03_random_and_sampling.md](./03_random_and_sampling.md) |
| Linear Algebra (Advanced) | [06_linear_algebra_advanced.md](./06_linear_algebra_advanced.md) |
| Statistics and Distributions | [05_statistics_and_distributions.md](./05_statistics_and_distributions.md) |
| I/O and Memory | [08_io_and_memory.md](./08_io_and_memory.md) |
