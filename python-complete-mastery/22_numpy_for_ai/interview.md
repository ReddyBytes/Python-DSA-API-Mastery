# 🎯 NumPy for AI — Interview Preparation Guide

---

# 🧠 What Interviewers Evaluate Here

NumPy questions appear in:
- ML engineer interviews
- Data science interviews
- Backend AI interviews
- Any role that involves embeddings, model inference, or data pipelines

They test:
- Whether you understand how vectorized computing actually works
- Whether you can reason about shapes and dimensions
- Whether you know the difference between views and copies
- Whether you can implement AI primitives (cosine similarity, softmax, normalization) from scratch

---

# 🔹 Level 1: Beginner (0–1 Years)

---

## 1️⃣ What is NumPy?

Strong answer:

> NumPy is a Python library for numerical computing. It provides the `ndarray` data structure — a fixed-type, multi-dimensional array stored in a contiguous block of memory. Operations on NumPy arrays are implemented in C, so they run orders of magnitude faster than equivalent Python loops.

Keep it simple. Mention: arrays, C, fast.

---

## 2️⃣ What is the difference between a NumPy array and a Python list?

Strong answer:

> Python lists are general-purpose containers. Each element is a separate Python object with its own type information and reference count. NumPy arrays store all elements as the same type in a contiguous block of raw memory. This makes NumPy arrays much faster for numerical operations and dramatically more memory-efficient.

Concrete numbers help:

> A Python int takes ~28 bytes. A NumPy float32 takes 4 bytes. For a million numbers, that is a 7x difference in memory.

---

## 3️⃣ What is the shape of an array?

Strong answer:

> Shape is a tuple describing the size of each dimension. A 1D array with 4 elements has shape `(4,)`. A 2D array with 3 rows and 5 columns has shape `(3, 5)`. A 3D array representing a batch of 32 attention matrices of size `(10, 512)` has shape `(32, 10, 512)`.

Then explain in AI context:

> In AI, a batch of 100 document embeddings each with 1536 dimensions has shape `(100, 1536)`. The shape tells you exactly how to interpret the data.

---

## 4️⃣ What is a dtype?

Strong answer:

> dtype is the data type of array elements. Common types are `float32`, `float64`, `int32`, `int64`, `bool`. All elements in a NumPy array share the same dtype, which is why arrays are memory-efficient and fast.

Why it matters:

> In AI, models use `float32` by default. If you accidentally create `float64` arrays, you double your memory usage for no accuracy benefit. Always check your dtype when working with embeddings.

---

## 5️⃣ How do you create a NumPy array?

```python
import numpy as np

np.array([1, 2, 3])                   # from list
np.zeros((3, 4))                       # zeros
np.ones((2, 3))                        # ones
np.arange(0, 10, 2)                    # like range
np.linspace(0, 1, 5)                   # 5 points from 0 to 1
np.random.default_rng(42).standard_normal((3, 3))  # Gaussian random
```

---

# 🔹 Level 2: Intermediate (1–3 Years)

---

## 6️⃣ What is broadcasting?

Strong answer:

> Broadcasting is NumPy's mechanism for performing operations on arrays with different shapes without explicitly copying data. NumPy expands the smaller array conceptually across the dimensions where it has size 1, so the operation runs as if both arrays had the same shape.

Example:

```python
m = np.ones((4, 3))    # shape (4, 3)
v = np.array([1, 2, 3])  # shape (3,)

result = m + v         # v is broadcast across all 4 rows
# result shape: (4, 3)
```

The broadcasting rule:

> Align shapes from the right. Dimensions are compatible if they are equal or one of them is 1. If they are incompatible, NumPy raises an error.

In AI terms:

> Adding a bias vector of shape `(512,)` to a batch output of shape `(32, 512)` uses broadcasting. This is exactly what a neural network layer does.

---

## 7️⃣ What is vectorization and why does it matter?

Strong answer:

> Vectorization means expressing operations as array-level calls instead of Python loops. NumPy implements these operations in compiled C/Fortran code. The result runs outside the Python interpreter, eliminating per-iteration overhead.

Concrete example:

```python
# Slow — Python loop
result = [a[i] * b[i] for i in range(len(a))]

# Fast — vectorized
result = a * b
```

Why it matters:

> For 1 million elements, the Python loop might take 200ms. The NumPy version takes under 1ms. In production AI systems handling thousands of requests, this is not a micro-optimization — it is the difference between a scalable product and one that falls over under load.

---

## 8️⃣ How does matrix multiplication work and why does it matter for AI?

Strong answer:

> Matrix multiplication computes the dot product of every row of the left matrix with every column of the right matrix. For shapes `(m, k)` and `(k, n)`, the result has shape `(m, n)`. The inner dimension `k` must match.

In NumPy:

```python
result = A @ B         # preferred syntax
result = np.matmul(A, B)
```

In AI:

> Every dense layer in a neural network is `output = input @ weights + bias`. The input batch has shape `(batch_size, input_features)`. The weight matrix has shape `(input_features, output_features)`. One `@` call transforms the whole batch in one shot — no loop over samples.

---

## 9️⃣ What is the difference between a view and a copy?

Strong answer:

> A view shares memory with the original array. Modifying a view modifies the original. A copy has its own memory block — modifying it does not affect the original.

```python
a = np.array([1, 2, 3, 4, 5])

b = a[1:4]        # view — shares memory
b[0] = 99
print(a)          # [1 99 3 4 5] — a changed!

c = a[1:4].copy() # copy — independent
c[0] = 0
print(a)          # unchanged
```

Why it matters:

> In AI pipelines processing large tensors, unexpected mutations through views cause subtle bugs that are hard to trace. Always call `.copy()` when you need independence, or be explicit in your reasoning.

---

## 🔟 Explain the axis parameter in aggregations.

Strong answer:

> `axis=0` collapses across rows — you get one result per column. `axis=1` collapses across columns — you get one result per row. Think of it as: "which dimension disappears?"

```python
arr = np.array([[1, 2, 3],
                [4, 5, 6]])

np.sum(arr, axis=0)   # [5 7 9]  — one sum per column
np.sum(arr, axis=1)   # [6 15]   — one sum per row
```

In AI:

> You have embeddings with shape `(100, 1536)`. `mean(axis=0)` gives the average embedding across all documents — shape `(1536,)`. `mean(axis=1)` gives the average value per document — shape `(100,)`. Knowing which axis you want is critical.

---

# 🔹 Level 3: Advanced (3+ Years)

---

## 1️⃣1️⃣ How do you compute cosine similarity between a query and many documents using NumPy — without a loop?

Strong answer:

> The key insight is that cosine similarity equals the dot product of two unit vectors. So normalize everything first, then use matrix multiplication.

```python
def cosine_search(query, docs, top_k=5):
    # Normalize query to unit vector
    q = query / np.linalg.norm(query)

    # Normalize all docs: divide each row by its norm
    norms = np.linalg.norm(docs, axis=1, keepdims=True)   # shape (n, 1)
    docs_norm = docs / norms                                # shape (n, dim)

    # One matrix multiply: dot product of each doc with query
    similarities = docs_norm @ q                            # shape (n,)

    # Get top-k
    top_idx = np.argsort(similarities)[-top_k:][::-1]
    return top_idx, similarities[top_idx]
```

Why no loop:

> The `@` operator computes all n dot products simultaneously using BLAS routines. For 10,000 documents with 1536 dimensions, this runs in ~3ms. A Python loop over the same computation takes ~3 seconds.

---

## 1️⃣2️⃣ How are embeddings stored as NumPy arrays and what are the memory implications?

Strong answer:

> Embeddings are stored as 2D float32 arrays with shape `(n_documents, embedding_dim)`. Memory = `n_documents × embedding_dim × 4 bytes`.

Concrete calculation:

> 1 million documents × 1536 dimensions × 4 bytes = 6.1 GB. This is why vector databases use quantization — reducing to `int8` cuts memory to 1.5 GB with minimal accuracy loss.

Layout matters for performance:

> NumPy default (C order, row-major) stores rows contiguously. When you compute `docs @ query`, you are reading each row sequentially — this is cache-friendly and fast. If the array were Fortran order (column-major), the same operation would be slower due to cache misses.

---

## 1️⃣3️⃣ What is memory layout (C order vs Fortran order) and why does it matter for performance?

Strong answer:

> C order (row-major) stores elements of each row contiguously in memory. Fortran order (column-major) stores elements of each column contiguously. The difference affects cache performance.

```python
arr_c = np.ascontiguousarray(arr)          # C order (default)
arr_f = np.asfortranarray(arr)             # Fortran order

arr.flags['C_CONTIGUOUS']   # check layout
```

Why it matters:

> Modern CPUs use cache lines — reading nearby memory is fast. If you iterate over rows of a C-order array, each row is a contiguous block in memory — fast. If you iterate over columns of a C-order array, you jump around in memory — cache misses, slow.

In AI:

> Embeddings stored in C order (the default) allow fast row access — reading one document's embedding is one contiguous read. Matrix multiply `docs @ query` is fast because the BLAS routine can read each row of `docs` sequentially. If you accidentally transpose and store in the wrong layout, the same operation can be 3–5x slower on large arrays.

Practical advice:

> After operations like `arr.T` (transpose), the result is a view in the opposite layout. If you then do heavy computation on it, call `np.ascontiguousarray()` first to restore cache-friendly layout.

---

# 🔥 Common Interview Traps

---

**Trap 1: Shape (n,) vs (n, 1)**

```python
v = np.array([1, 2, 3])
print(v.shape)             # (3,)  — 1D

v_col = v.reshape(3, 1)
print(v_col.shape)         # (3, 1) — column vector
```

These behave differently in broadcasting. Know when you need `(n,)` vs `(n, 1)`.

---

**Trap 2: Integer division in reshape**

```python
arr = np.arange(12)
arr.reshape(5, -1)   # ERROR — 12 / 5 is not an integer
arr.reshape(4, -1)   # OK — 12 / 4 = 3
```

---

**Trap 3: Modifying a view when you meant to copy**

```python
batch = embeddings[:10]    # view
batch /= batch.max()       # modifies original embeddings!
```

---

**Trap 4: argmax vs argsort for top-k**

```python
np.argmax(scores)             # index of maximum — O(n)
np.argsort(scores)[-k:][::-1] # top-k indices — O(n log n)
# Use argpartition for faster approximate top-k:
np.argpartition(scores, -k)[-k:]
```

---

# 🎯 Rapid-Fire Revision

- NumPy arrays are typed, contiguous, C-level
- Shape is a tuple: `(rows, cols, ...)` — read left to right
- `axis=0` collapses rows, `axis=1` collapses columns
- Broadcasting aligns shapes from the right, stretches size-1 dims
- `@` for matrix multiply, `.T` for transpose
- Slicing returns a view; boolean indexing returns a copy
- Normalize embeddings → dot product equals cosine similarity
- `float32` for AI (4 bytes), not `float64` (8 bytes)
- C order = row-major = cache-friendly for row operations (the default)
- `np.argsort(scores)[-k:][::-1]` for top-k

---

# 🔁 Navigation

Previous: `21_typing_and_pydantic/interview.md`
Next: `23_pandas_for_ai/interview.md`
